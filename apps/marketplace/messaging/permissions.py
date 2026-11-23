from rest_framework import permissions


class IsConversationParticipant(permissions.BasePermission):
    """
    Guarantees that only users who are direct participants (buyer or seller)
    can view or interact with a conversation and its messages.
    """
    def has_object_permission(self, request, view, obj):
        # Support Conversation or Message objects
        conversation = getattr(obj, "conversation", obj)
        return request.user in (conversation.buyer, conversation.seller)
