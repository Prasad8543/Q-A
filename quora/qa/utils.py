from rest_framework_simplejwt.settings import api_settings
import os
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import jwt
from rest_framework_simplejwt.tokens import RefreshToken
import time
from django.conf import settings
from django.core.cache import cache
import uuid
from django.contrib.auth import get_user_model
User = get_user_model()


def get_public_key():
    public_pem = os.getenv('PUBLIC_PEM_FILE')
    if not public_pem:
        return None
    public_key = open(public_pem).read().encode('utf-8')
    public_key = serialization.load_pem_public_key(
        public_key, backend=default_backend()
    )
    return public_key 

def get_private_key():
    password = os.getenv("PRIVATE_PEM_PASSWORD","LOCAL")
    private_pem = os.getenv('PRIVATE_PEM_FILE')
    if not private_pem:
        raise jwt.InvalidTokenError
    private_key = open(private_pem).read().encode('utf-8')
    private_key = serialization.load_pem_private_key(
        private_key, password=password.encode(), backend=default_backend()
    )
    return private_key
    


def encode_jwt(payload):  
    return jwt.encode(
        payload, get_private_key(),"RS256"
    )

def decode_jwt(token):
    try:
        payload = jwt.decode(
            jwt=token,
            key=get_public_key(),
            options= {"verify_exp": api_settings.ACCESS_TOKEN_LIFETIME},
            leeway=api_settings.LEEWAY,
            audience=api_settings.AUDIENCE,
            issuer=api_settings.ISSUER,
            algorithms=["RS256"],
        )
        cache_key = f"{payload.get('username')}:black_list_tokens"
        black_listed_tokens = cache.get(cache_key)
        if black_listed_tokens and token in black_listed_tokens:
            raise jwt.ExpiredSignatureError
        return payload
    except jwt.ExpiredSignatureError as e:
        raise jwt.ExpiredSignatureError
    except Exception as e:
        raise jwt.InvalidTokenError
    

def get_jwt_token(user, iat=None, **kwargs):
    expires_in = settings.TOKEN_EXPIRATION_TIME

    refresh_token = RefreshToken.for_user(user)
    access_token = refresh_token.access_token
    payload = access_token.payload
    payload = {
        'user_id': user.pk,
        'username': user.username,
        'exp': payload.get('exp', None),
        'email': user.email,
        'orig_iat': payload.get('iat', None),
    }
    payload['exp_ms'] = int(
        (time.time() + int(expires_in)) * 1000
    )
    token = encode_jwt(payload=payload)
    return token,expires_in


def generate_unique_username():
    while True:
        username = uuid.uuid4().hex[:30]
        if not User.objects.filter(username=username).exists():
            return username