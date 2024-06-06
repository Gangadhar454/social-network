from django.db import models
from user_management.models import User

class FriendRequest(models.Model):
    friend_request_statuses = (
        ("Accepted", "Accepted"),
        ("Rejected", "Rejected"),
        ("Pending", "Pending")
    )
    requested_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_send')
    requested_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requests_recieved')
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    status = models.CharField(choices=friend_request_statuses, max_length=10)