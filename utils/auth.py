import functools
from rest_framework.response import Response
import jwt

from social_network.settings import public_key, private_key
import traceback

def validate_token():
    def actual_decorator(view_method):
        @functools.wraps(view_method)
        def _arguments_wrapper(view_func, *args, **kwargs):
            try:
                request = view_func.request
                auth_header_key = 'HTTP_AUTHORIZATION'
                if (
                    auth_header_key not in request.META
                    or not isinstance(request.META[auth_header_key], str)
                ):
                    return Response(
                        {
                            "status": False,
                            "message": "UnAuthorized"
                        },
                        status=401
                    )
                access_token = request.META[auth_header_key]
                access_token = access_token.replace("Bearer ", "")
                decrypted_token = jwt.decode(
                    access_token,
                    public_key,
                    algorithm='RS256'
                )
                request.META.update(
                    {
                        "user_id": decrypted_token['user_id'],
                        "email": decrypted_token['email']
                    }
                )
                return view_method(view_func, *args, **kwargs)
            except Exception as e:
                traceback.print_exc()
                return Response(
                    {
                        "status": False,
                        "message": "UnAuthorized"
                    },
                    status=401
                )
        return _arguments_wrapper
    return actual_decorator