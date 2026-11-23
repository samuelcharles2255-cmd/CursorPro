from django.urls import path
from .views import (
    ConversationListCreateView,
    ConversationDetailView,
    ConversationMessagesView,
    BlockConversationView,
)

urlpatterns = [
    path("conversations/", ConversationListCreateView.as_view(), name="conversation-list-create"),
    path("conversations/<int:pk>/", ConversationDetailView.as_view(), name="conversation-detail"),
    path("conversations/<int:pk>/messages/", ConversationMessagesView.as_view(), name="conversation-messages"),
    path("conversations/<int:pk>/block/", BlockConversationView.as_view(), name="conversation-block"),
]
