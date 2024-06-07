import functools
from typing import Any, Callable
from django_ratelimit.core import is_ratelimited
from dataclasses import dataclass
from rest_framework.response import Response

def prepare_ratelimit_key(group, request) -> str:
    user_id = request.META['user_id']
    return f'{user_id}:rate:SendRequest'


@dataclass
class RateLimitOptions:
    key: Callable[[Any, Any], Any]
    rate: str
    method: str


def apply_rate_limit(ratelimit_options: RateLimitOptions):
    def actual_decorator(view_method):
        @functools.wraps(view_method)
        def _arguments_wrapper(view_func, *args, **kwargs):
            request = view_func.request
            old_limited = getattr(request, 'limited', False)
            # action = send_request is for new friend request
            is_send_friend_request = request.data['action'] == 'send_request'
            if is_send_friend_request:
                ratelimited = is_ratelimited(
                    request=request,
                    group=None,
                    fn=view_method,
                    key=ratelimit_options.key,
                    rate=ratelimit_options.rate,
                    method=ratelimit_options.method,
                    increment=True
                )
                request.limited = ratelimited or old_limited
                if ratelimited:
                    return Response(
                        {
                            "status": False,
                            "message": "cannot send more than 3 friend requests per minute "
                        },
                        status=429
                    )
            return view_method(view_func, *args, **kwargs)
        return _arguments_wrapper
    return actual_decorator
