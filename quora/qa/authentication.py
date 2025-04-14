from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model
from qa.utils import decode_jwt
import jwt

User = get_user_model()

class QuoraJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("JWT "):
            return None  # No token provided, fallback to other auth if defined

        token = auth_header.split("JWT ")[1]
        try:
            payload = decode_jwt(token)
            user = User.objects.get(id=payload["user_id"])
            setattr(request,'user',user)
            return (user, None)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed("Token has expired")
        except jwt.InvalidTokenError:
            raise AuthenticationFailed("Invalid token")
        except User.DoesNotExist:
            raise AuthenticationFailed("User not found")
