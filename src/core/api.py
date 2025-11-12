import helpers
from ninja import NinjaAPI, Schema
from django.contrib.auth import get_user_model
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from allauth.headless.account.views import send_verification_email_to_address
from django.shortcuts import get_object_or_404

from ninja_extra import NinjaExtraAPI
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.controller import NinjaJWTDefaultController

User = get_user_model()

api = NinjaExtraAPI()
api.register_controllers(NinjaJWTDefaultController)
api.add_router("/waitlists/", "waitlists.api.router")

class UserSchema(Schema):
    username: str
    is_authenticated: bool
    # is not requst.user.is_authenticated
    email: str = None

class SignupSchema(Schema):
    username: str
    email: str
    password: str
    first_name: str = None
    last_name: str = None

class SignupResponseSchema(Schema):
    success: bool
    message: str
    user: UserSchema = None

class EmailConfirmSchema(Schema):
    key: str

class EmailConfirmResponseSchema(Schema):
    success: bool
    message: str

class ResendEmailSchema(Schema):
    email: str

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

        # Send verification email
        send_verification_email_to_address(request, email_address)

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

        # Resend confirmation email
        send_verification_email_to_address(request, email_address)

        return {
            "success": True,
            "message": "Verification email sent successfully"
        }
    except Exception as e:
        return {
            "success": False,
            "message": f"Error resending email: {str(e)}"
        }