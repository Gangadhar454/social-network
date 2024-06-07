from rest_framework.views import APIView
from rest_framework.response import Response
from user_management.models import User
from friendship_management.models import FriendRequest
from friendship_management.serializers import (
    FriendRequestValidationSerializer,
    FriendRequestAcceptedSerializer,
    FriendRequestRecievedSerializer
)
from django.db import IntegrityError
from datetime import datetime, timedelta
from django.utils import timezone
import jwt
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Q
from utils.auth import validate_token
from utils.ratelimit import (
    prepare_ratelimit_key,
    apply_rate_limit,
    RateLimitOptions
)


ACTION_STATUS_MAP = {
    'send_request': 'Pending',
    'approve': 'Accepted',
    'reject': 'Rejected'
}
class FriendRequestView(APIView):

    @validate_token()
    @apply_rate_limit(
        RateLimitOptions(
            key=prepare_ratelimit_key,
            rate='3/60s',
            method='PATCH'
        )
    )
    def patch(self, request):
        payload = request.data
        serializer = FriendRequestValidationSerializer(data=payload)
        if not serializer.is_valid():
            return Response(
                {
                    "status": False,
                    "errors": serializer.errors
                }
            )
        requested_action = payload['action']
        friend_id = payload['friend_id']
        user_id = request.META['user_id']
        response_message = ""
        if requested_action == 'send_request':
            request_existed = FriendRequest.objects.filter(
                Q(status='Approved') | Q(status='Pending'),
                requested_from=user_id,
                requested_to=friend_id,
            ).exists()
            if request_existed:
                return Response(
                    {
                        "status": False,
                        "message": "Request already send or already Approved"
                    }
                )
            request_status = ACTION_STATUS_MAP.get(requested_action)
            try:
                FriendRequest.objects.create(
                    requested_from_id=user_id,
                    requested_to_id=friend_id,
                    status=request_status
                )
                response_message = "Friend Request Sent"
            except IntegrityError:
                return Response(
                    {
                        "status": True,
                        "message": "Invalid Friend "
                    }
                )
        else:
            request_status = ACTION_STATUS_MAP.get(requested_action)
            try:
                # Friend Request sent to you
                pending_request = FriendRequest.objects.get(
                    status='Pending',
                    requested_from=friend_id,
                    requested_to=user_id, # requested to your user id
                )
            except FriendRequest.DoesNotExist:
                return Response({
                    "status": False,
                    "message": "Invalid Request"
                })
            pending_request.status = request_status
            pending_request.save()
            if request_status == 'Accepted':
                response_message = 'Friend Request Approved'
            else:
                response_message = 'Friend Request Rejected'
        return Response({
            "status": True,
            "message": response_message
        })

class FriendListView(APIView):

    @validate_token()
    def get(self, request):
        status = request.GET.get('status', None)
        if not (status == 'Accepted' or status == 'Pending'):
            return Response(
                {
                    "status": False,
                    "message": "Invalid status"
                }
            )
        user_id = request.META['user_id']
        if status == 'Accepted':
            # Query to find the accepted friend requests which the requested user sent
            friends = FriendRequest.objects.filter(
                requested_from_id=user_id,
                status='Accepted'
            ).select_related('requested_to')
            request_search_results = FriendRequestAcceptedSerializer(friends, many=True).data
        else:
            # Query to find the pending friend requests which the requested user recieved
            friends = FriendRequest.objects.filter(
                requested_to_id=user_id,
                status='Pending'
            ).select_related('requested_from')
            request_search_results = FriendRequestRecievedSerializer(friends, many=True).data
        return Response({
            "status": True,
            "search_results": request_search_results
        })