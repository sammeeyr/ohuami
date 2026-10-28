import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class SupportEnquiry(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', _('Open')
        IN_PROGRESS = 'in_progress', _('In Progress')
        RESOLVED = 'resolved', _('Resolved')
        CLOSED = 'closed', _('Closed')

    ticket_number = models.CharField(max_length=50, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='support_tickets')
    name = models.CharField(max_length=150)
    email = models.EmailField()
    phone = models.CharField(max_length=30, blank=True, default='')
    subject = models.CharField(max_length=200)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.OPEN)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Support Enquiry')
        verbose_name_plural = _('Support Enquiries')
        ordering = ['-created_at']

    def __str__(self):
        return f"Ticket #{self.ticket_number} - {self.subject}"

    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = f"SUP-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)


class ChatMessage(models.Model):
    session_id = models.CharField(max_length=100, db_index=True)
    sender = models.CharField(max_length=20, default='customer') # 'customer' or 'agent'
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"[{self.sender}] {self.text[:30]}"
