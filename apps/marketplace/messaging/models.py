from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Conversation(models.Model):
    """
    Direct communication thread between a buyer and a seller regarding a specific marketplace listing.
    Enforces participant isolation, spam prevention, and blocking rules.
    """
    listing = models.ForeignKey(
        "listings.Listing",
        on_delete=models.CASCADE,
        related_name="conversations",
        verbose_name=_("listing")
    )
    buyer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="buyer_conversations",
        verbose_name=_("buyer / initiator")
    )
    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="seller_conversations",
        verbose_name=_("seller / recipient")
    )

    is_blocked = models.BooleanField(_("is blocked"), default=False)
    blocked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="blocked_conversations",
        verbose_name=_("blocked by")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, db_index=True)

    class Meta:
        db_table = "messaging_conversation"
        verbose_name = _("Conversation")
        verbose_name_plural = _("Conversations")
        unique_together = ("listing", "buyer")
        ordering = ["-updated_at"]
        indexes = [
            models.Index(fields=["buyer", "-updated_at"], name="idx_conv_buyer_updated"),
            models.Index(fields=["seller", "-updated_at"], name="idx_conv_seller_updated"),
        ]

    def __str__(self):
        return f"Chat for '{self.listing.title}': Buyer ({self.buyer}) <-> Seller ({self.seller})"

    def clean(self):
        super().clean()
        if self.buyer == self.seller:
            raise ValidationError(
                _("You cannot start a conversation with yourself regarding your own listing."),
                code="self_messaging_prohibited"
            )
        # Ensure seller matches listing.seller if listing is saved
        if hasattr(self, "listing") and self.listing and self.listing.seller:
            if self.seller != self.listing.seller:
                self.seller = self.listing.seller

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    @property
    def last_message(self):
        return self.messages.order_by("-created_at").first()

    def get_recipient(self, user):
        """Returns the other participant in the conversation relative to the given user"""
        return self.seller if user == self.buyer else self.buyer


class Message(models.Model):
    """
    Individual chat message inside a conversation thread.
    Maintains delivery status, read receipts, and prevents unauthorized messaging.
    """
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name=_("conversation")
    )
    sender = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sent_messages",
        verbose_name=_("sender")
    )
    content = models.TextField(_("content"), max_length=4000)

    is_read = models.BooleanField(_("is read"), default=False, db_index=True)
    read_at = models.DateTimeField(_("read at"), null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = "messaging_message"
        verbose_name = _("Message")
        verbose_name_plural = _("Messages")
        ordering = ["created_at"]
        indexes = [
            models.Index(fields=["conversation", "created_at"], name="idx_msg_conv_created"),
            models.Index(fields=["conversation", "is_read"], name="idx_msg_conv_isread"),
        ]

    def __str__(self):
        return f"Message #{self.id} from {self.sender} at {self.created_at:%Y-%m-%d %H:%M}"

    def clean(self):
        super().clean()
        if hasattr(self, "conversation") and self.conversation:
            if self.conversation.is_blocked:
                raise ValidationError(
                    _("This conversation has been blocked. Messages cannot be sent."),
                    code="conversation_blocked"
                )
            if self.sender not in (self.conversation.buyer, self.conversation.seller):
                raise ValidationError(
                    _("You are not a participant in this conversation thread."),
                    code="unauthorized_sender"
                )

    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
        # Touch the conversation's updated_at timestamp so active threads surface to the top
        Conversation.objects.filter(pk=self.conversation_id).update(updated_at=timezone.now())
