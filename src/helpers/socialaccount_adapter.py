from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.shortcuts import redirect
from urllib.parse import urlencode


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter to handle social auth for headless/API setup.
    After successful social login, redirects to frontend with JWT tokens.
    """

    def get_login_redirect_url(self, request):
        """
        Override to redirect to frontend with JWT tokens after social login.
        """
        # Get the user from the request (already authenticated by allauth)
        user = request.user

        if user and user.is_authenticated:
            # Generate JWT tokens for the user
            from ninja_jwt.tokens import RefreshToken

            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            # Build frontend URL with tokens
            frontend_url = settings.FRONTEND_URL
            params = urlencode({
                'access': access_token,
                'refresh': refresh_token,
                'username': user.username,
            })

            redirect_url = f"{frontend_url}/auth/callback?{params}"
            return redirect_url

        # Fallback to default behavior
        return super().get_login_redirect_url(request)
