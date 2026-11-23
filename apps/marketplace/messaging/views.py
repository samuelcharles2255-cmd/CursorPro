from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Conversation, Message
from .permissions import IsConversationParticipant
from .serializers import (
    ConversationSerializer,
    CreateConversationSerializer,
    MessageSerializer,
    SendMessageSerializer,
)


class ConversationListCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        conversations = Conversation.objects.filter(
            Q(buyer=user) | Q(seller=user)
        ).select_related("listing", "buyer", "seller").prefetch_related("messages")
        serializer = ConversationSerializer(conversations, many=True, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CreateConversationSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        listing = serializer.validated_data["listing"]
        buyer = serializer.validated_data["buyer"]
        seller = serializer.validated_data["seller"]
        initial_message = serializer.validated_data["initial_message"]

        # Get or create conversation thread between buyer and listing
        conversation, created = Conversation.objects.get_or_create(
            listing=listing,
            buyer=buyer,
            defaults={"seller": seller}
        )

        # Create initial message
        msg = Message.objects.create(
            conversation=conversation,
            sender=buyer,
            content=initial_message
        )

        conv_serializer = ConversationSerializer(conversation, context={"request": request})
        return Response(conv_serializer.data, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class ConversationDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]

    def get(self, request, pk):
        conv = get_object_or_404(Conversation, pk=pk)
        self.check_object_permissions(request, conv)
        serializer = ConversationSerializer(conv, context={"request": request})
        return Response(serializer.data)


class ConversationMessagesView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]

    def get(self, request, pk):
        conv = get_object_or_404(Conversation, pk=pk)
        self.check_object_permissions(request, conv)

        # Mark messages sent by the other party as read
        conv.messages.filter(is_read=False).exclude(sender=request.user).update(
            is_read=True,
            read_at=timezone.now()
        )

        messages = conv.messages.all().select_related("sender")
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request, pk):
        conv = get_object_or_404(Conversation, pk=pk)
        self.check_object_permissions(request, conv)

        if conv.is_blocked:
            return Response(
                {"error": "This conversation has been blocked. Messages cannot be delivered."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = SendMessageSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        msg = Message.objects.create(
            conversation=conv,
            sender=request.user,
            content=serializer.validated_data["content"]
        )

        return Response(MessageSerializer(msg).data, status=status.HTTP_201_CREATED)


class BlockConversationView(APIView):
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]

    def post(self, request, pk):
        conv = get_object_or_404(Conversation, pk=pk)
        self.check_object_permissions(request, conv)

        conv.is_blocked = True
        conv.blocked_by = request.user
        conv.save(update_fields=["is_blocked", "blocked_by"])

        return Response({"message": "Conversation successfully blocked."}, status=status.HTTP_200_OK)
