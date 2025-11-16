import helpers
from ninja import NinjaAPI, Schema
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from allauth.headless.account.views import send_verification_email_to_address
from django.shortcuts import get_object_or_404
from typing import Optional
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

from ninja_extra import NinjaExtraAPI, api_controller, route
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import NinjaJWTDefaultController
from ninja_jwt.tokens import RefreshToken
from ninja_jwt.schema import TokenObtainPairInputSchema, TokenObtainPairOutputSchema

User = get_user_model()

# Custom JWT Controller to allow login with email or username
@api_controller("/token", tags=["Auth"], auth=None)
class AsyncNinjaJWTSlidingController:
    @route.post("/pair", response=TokenObtainPairOutputSchema, url_name="token_obtain_pair")
    def obtain_token(self, user_token: TokenObtainPairInputSchema):
        # Try to find user by username first
        user = User.objects.filter(username=user_token.username).first()

        # If not found, try to find by email
        if not user:
            user = User.objects.filter(email=user_token.username).first()

        # Check if user exists and password is correct
        if user and user.check_password(user_token.password):
            refresh = RefreshToken.for_user(user)
            return {
                "refresh": str(refresh),
                "access": str(refresh.access_token),
                "username": user.username,
            }

        # Return 401 if authentication fails
        from ninja.errors import HttpError
        raise HttpError(401, "Invalid credentials")

    @route.post("/refresh", auth=None, url_name="token_refresh")
    def refresh_token(self, refresh_token: str):
        from ninja_jwt.tokens import RefreshToken
        token = RefreshToken(refresh_token)
        return {"access": str(token.access_token)}

api = NinjaExtraAPI()
api.register_controllers(AsyncNinjaJWTSlidingController)
api.add_router("/waitlists/", "waitlists.api.router")

class UserSchema(Schema):
    username: str
    is_authenticated: bool
    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None

class SignupSchema(Schema):
    username: str
    email: str
    password: str
    first_name: str | None = None
    last_name: str | None = None

class SignupResponseSchema(Schema):
    success: bool
    message: str
    user: UserSchema | None = None

class EmailConfirmSchema(Schema):
    key: str

class EmailConfirmResponseSchema(Schema):
    success: bool
    message: str

class ResendEmailSchema(Schema):
    email: str

class ForgotPasswordSchema(Schema):
    email: str

class ForgotPasswordResponseSchema(Schema):
    success: bool
    message: str

class ResetPasswordSchema(Schema):
    uid: str
    token: str
    new_password: str

class ResetPasswordResponseSchema(Schema):
    success: bool
    message: str

class ContactMessageSchema(Schema):
    name: str
    email: str
    message: str

class ContactMessageResponseSchema(Schema):
    success: bool
    message: str

def send_custom_verification_email(request, email_address):
    """Send a custom verification email that points to the Next.js frontend"""
    confirmation = EmailConfirmationHMAC(email_address)
    key = confirmation.key

    # Build frontend verification URL
    frontend_url = settings.FRONTEND_URL
    verification_url = f"{frontend_url}/verify-email?key={key}"

    subject = f"{settings.ACCOUNT_EMAIL_SUBJECT_PREFIX}Please Confirm Your Email Address"
    message = f"""Hello from DigitalPath AI!

You're receiving this email because you registered an account on DigitalPath AI.

To confirm your email address, please click on the following link:

{verification_url}

If you didn't register for an account, you can safely ignore this email.

Thank you for using DigitalPath AI!
"""

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email_address.email],
        fail_silently=False,
    )

@api.get("/hello")
def hello(request):
    # print(request)
    return {"message":"Hello World"}

@api.get("/me",
    response=UserSchema,
    auth=helpers.api_auth_user_required)
def me(request):
    return request.user

@api.post("/auth/signup", response=SignupResponseSchema)
def signup(request, payload: SignupSchema):
    # Check if username already exists
    if User.objects.filter(username=payload.username).exists():
        return {
            "success": False,
            "message": "Username already exists",
            "user": None
        }

    # Check if email already exists
    if User.objects.filter(email=payload.email).exists():
        return {
            "success": False,
            "message": "Email already exists",
            "user": None
        }

    try:
        # Create user (inactive until email is verified)
        user = User.objects.create_user(
            username=payload.username,
            email=payload.email,
            password=payload.password,
            first_name=payload.first_name or "",
            last_name=payload.last_name or "",
            is_active=False  # User must verify email first
        )

        # Create EmailAddress record and send verification email
        email_address = EmailAddress.objects.create(
            user=user,
            email=payload.email,
            primary=True,
            verified=False
        )

        # Send custom verification email with frontend URL
        send_custom_verification_email(request, email_address)

        return {
            "success": True,
            "message": "User created successfully. Please check your email to verify your account.",
            "user": {
                "username": user.username,
                "email": user.email,
                "is_authenticated": False
            }
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error creating user: {str(e)}",
            "user": None
        }

@api.post("/auth/verify-email", response=EmailConfirmResponseSchema)
def verify_email(request, payload: EmailConfirmSchema):
    """Verify email using the confirmation key sent via email"""
    try:
        # Get the email confirmation using the key
        email_confirmation = EmailConfirmationHMAC.from_key(payload.key)

        if not email_confirmation:
            return {
                "success": False,
                "message": "Invalid or expired confirmation key"
            }

        # Confirm the email
        email_confirmation.confirm(request)

        # Activate the user
        user = email_confirmation.email_address.user
        user.is_active = True
        user.save()

        return {
            "success": True,
            "message": "Email verified successfully. You can now log in."
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error verifying email: {str(e)}"
        }

@api.post("/auth/resend-verification", response=EmailConfirmResponseSchema)
def resend_verification(request, payload: ResendEmailSchema):
    """Resend verification email to user"""
    try:
        # Find user by email
        user = User.objects.filter(email=payload.email).first()

        if not user:
            return {
                "success": False,
                "message": "No user found with this email"
            }

        # Check if already verified
        email_address = EmailAddress.objects.filter(
            user=user,
            email=payload.email,
            primary=True
        ).first()

        if email_address and email_address.verified:
            return {
                "success": False,
                "message": "Email is already verified"
            }

        # Resend confirmation email with frontend URL
        send_custom_verification_email(request, email_address)

        return {
            "success": True,
            "message": "Verification email sent successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error resending email: {str(e)}"
        }

@api.post("/auth/forgot-password", response=ForgotPasswordResponseSchema)
def forgot_password(request, payload: ForgotPasswordSchema):
    """Send password reset email to user"""
    try:
        # Find user by email
        user = User.objects.filter(email=payload.email).first()

        # Always return success for security (don't reveal if email exists)
        # But only send email if user exists
        if user:
            # Generate password reset token
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Build frontend password reset URL
            frontend_url = settings.FRONTEND_URL
            reset_url = f"{frontend_url}/reset-password?uid={uid}&token={token}"

            # Send password reset email
            subject = f"{settings.ACCOUNT_EMAIL_SUBJECT_PREFIX}Password Reset Request"
            message = f"""Hello {user.username},

You're receiving this email because you (or someone else) requested a password reset for your DigitalPath AI account.

To reset your password, please click on the following link:

{reset_url}

This link will expire in 24 hours.

If you didn't request this password reset, you can safely ignore this email. Your password will remain unchanged.

Thank you for using DigitalPath AI!
"""

            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                fail_silently=False,
            )

        return {
            "success": True,
            "message": "If an account exists with this email, you will receive a password reset link shortly."
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error sending password reset email: {str(e)}"
        }

@api.post("/auth/reset-password", response=ResetPasswordResponseSchema)
def reset_password(request, payload: ResetPasswordSchema):
    """Reset user password using uid and token"""
    try:
        # Decode user ID
        try:
            uid = force_str(urlsafe_base64_decode(payload.uid))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return {
                "success": False,
                "message": "Invalid reset link"
            }

        # Check if token is valid
        if not default_token_generator.check_token(user, payload.token):
            return {
                "success": False,
                "message": "Invalid or expired reset link"
            }

        # Set new password
        user.set_password(payload.new_password)
        user.save()

        return {
            "success": True,
            "message": "Password has been reset successfully. You can now log in with your new password."
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error resetting password: {str(e)}"
        }

@api.post("/contact", response=ContactMessageResponseSchema)
def contact(request, payload: ContactMessageSchema):
    """Handle contact form submissions"""
    from contact.models import ContactMessage
    from contact.tasks import send_contact_email_task
    import logging

    logger = logging.getLogger(__name__)

    try:
        # Create contact message record
        contact_message = ContactMessage.objects.create(
            name=payload.name,
            email=payload.email,
            message=payload.message,
            status='pending'
        )

        # Try to send email asynchronously via Celery
        try:
            task_result = send_contact_email_task.delay(contact_message.id)
            logger.info(f"Contact email task dispatched: {task_result.id} for message {contact_message.id}")
        except Exception as celery_error:
            # Fallback: send email synchronously if Celery is not available
            logger.warning(f"Celery not available, sending email synchronously: {celery_error}")
            send_contact_email_task(contact_message.id)

        return {
            "success": True,
            "message": "Thank you for your message! We'll get back to you within 24 hours."
        }
    except Exception as e:
        logger.error(f"Error in contact form: {e}", exc_info=True)
        return {
            "success": False,
            "message": f"Error sending message: {str(e)}"
        }