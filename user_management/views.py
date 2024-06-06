from rest_framework.views import APIView
from rest_framework.response import Response
from user_management.serializers import (
    SignUpSerializer,
    SignInSerializer,
    UserSerializer
)
import bcrypt
from user_management.models import User
from django.db import IntegrityError
from datetime import datetime, timedelta
from django.utils import timezone
import jwt
from django.core.paginator import Paginator, EmptyPage
from utils.auth import validate_token



# reading public key and privatke for jwt token creation
public_key = open('jwt-key.pub').read()
private_key = open('jwt-key').read()

class UserSignupView(APIView):

    def post(self, request):
        payload = request.data
        serializer = SignUpSerializer(data=payload)
        if not serializer.is_valid():
            return Response(
                {
                    "status": False,
                    "message": serializer.errors
                },
                status=200
            )
        password = payload['password']
        encrypted_password = bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        )
        try:

            user = User.objects.create(
                name=payload['name'],
                email=payload['email'],
                password=encrypted_password.decode('utf-8')
            )
        except IntegrityError:
            return Response(
            {
                "status": False,
                "message": "email already exists"
            },
            status=200
        )
        return Response(
            {
                "status": True,
                "user_id": user.id
            },
            status=201
        )


class UserSignInView(APIView):

    def post(self, request):
        payload = request.data
        serializer = SignInSerializer(data=payload)
        if not serializer.is_valid():
            return Response(
                {
                    "status": False,
                    "message": serializer.errors
                },
                status=200
            )
        try:
            user = User.objects.get(
                email__iexact=payload["email"]
            )
        except User.DoesNotExist:
            return Response({
                "status": False,
                "message": "Invalid Email"
            })

        def utf_encode(raw: str):
            return raw.encode('utf-8')
        if not bcrypt.checkpw(
            utf_encode(payload["password"]),
            utf_encode(user.password)
        ):
            return Response({
                "status": False,
                "message": "Invalid Password"
            })
        access_token = jwt.encode(
            {
                "user_id": user.id,
                "email": user.email,
                "exp": timezone.now() + timedelta(hours=24),
            },
            private_key,
            algorithm='RS256'
        )
        return Response({
            "status": True,
            "access_token": access_token
        })


class UserSearchView(APIView):

    def fetch_queryparams(self, request):
        search_key = request.GET.get('search_key', None)
        search_value = request.GET.get('value', None)
        page = page = request.GET.get('page', 1)
        if not search_key or not search_value:
            return Response(
                {
                    "status": False,
                    "message": 'Invalid search params'
                }
            )
        if not (search_key == 'email' or search_key == 'name'):
            return Response(
                {
                    "status": False,
                    "message": 'Invalid search key'
                }
            )
        return search_key, search_value, page

    @validate_token()
    def get(self, request):
        search_key, search_value, page = self.fetch_queryparams(request)
        if search_key == 'email':
            try:
                user = User.objects.get(email__iexact=search_value)
            except User.DoesNotExist:
                return Response(
                {
                    "status": True,
                    "message": 'No result found'
                }
            )
            user_details = UserSerializer(user).data
            return Response(
                {
                    "status": True,
                    "results": user_details
                }
            )
        users = User.objects.filter(name__icontains=search_value)
        if not users:
            return Response(
                {
                    "status": True,
                    "message": 'No result found'
                }
            )
        try:
            paginator = Paginator(users, 10)
            users = paginator.page(page)
        except EmptyPage:
            return Response(
                {
                    "status": True,
                    "message": 'No result found'
                }
            )
        serialized_users = UserSerializer(users, many=True).data
        return Response(
            {
                "status": True,
                "users": serialized_users
            }
        )