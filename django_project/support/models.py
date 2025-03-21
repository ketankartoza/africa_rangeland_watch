from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings
from django.template.loader import render_to_string
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives

from alerts.models import AlertSetting, Indicator
import logging

from base.models import UserProfile


logger = logging.getLogger(__name__)


def get_support_staff_emails():
    """
    Returns a list of emails for users marked as support staff.
    """
    support_staff_profiles = UserProfile.objects.filter(is_support_staff=True)
    support_staff_emails = [
        profile.user.email for profile in support_staff_profiles
    ]

    if not support_staff_emails:
        logger.warning("No support staff found to send the email.")

    return support_staff_emails


class IssueType(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name





class Ticket(models.Model):
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('resolved', 'Resolved'),
        ('pending', 'Pending'),
    ]
    title = models.CharField(max_length=255)
    issue_type = models.ForeignKey(
        IssueType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        help_text="The type of issue for the ticket"
    )
    description = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='open'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    assigned_to = models.ForeignKey(
        User,
        related_name="assigned_tickets",
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    email = models.EmailField()
    alert_setting = models.ForeignKey(
        AlertSetting,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        help_text='The alert setting associated with this ticket.'
    )
    indicator = models.ForeignKey(
        Indicator,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tickets',
        help_text='The indicator related to this ticket.'
    )
    file_attachment = models.FileField(
        upload_to='ticket_attachments/',
        null=True,
        blank=True
    )
    resolution_summary = models.TextField(
        null=True,
        blank=True,
        help_text=(
            "Summary of the resolution provided by the admin when the ticket "
            "is resolved."
        )
    )


    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if self.status == 'resolved' and not self.resolution_summary:
            raise ValidationError(
                "A resolution summary is required when marking the ticket as"
                " resolved."
            )
        super().save(*args, **kwargs)

    def send_ticket_submission_email(self):
        """Send an email to the support admin when a ticket is submitted."""
        subject = f"New Support Ticket: {self.title}"
        context = {
            'ticket': self,
            'django_backend_url': settings.DJANGO_BACKEND_URL,
        }
        html_message = render_to_string(
            'new_ticket_notification.html',
            context
        )
        support_staff_emails = get_support_staff_emails()

        if not support_staff_emails:
            logger.warning("No support staff found to send the email.")

        email = EmailMultiAlternatives(
            subject=subject,
            body="",
            from_email=settings.NO_REPLY_EMAIL,
            to=support_staff_emails,
        )
        email.attach_alternative(html_message, "text/html")
        try:
            email.send()
        except Exception as e:
            logger.error(
                f"Failed to send ticket submission email for ticket"
                f"{self.id}: {e}"
            )

    def send_status_update_email(self):
        """Email the user when the status of their ticket is updated."""
        status_titles = {
            'open': 'Ticket Opened',
            'in_progress': 'Ticket In Progress',
            'resolved': 'Ticket Resolved',
            'pending': 'Ticket Pending',
        }

        subject = f"{
            status_titles.get(self.status, 'Ticket Update')
        }: {self.title}"
        context = {
            'title': subject,
            'ticket': self,
            'django_backend_url': settings.DJANGO_BACKEND_URL,
        }
        html_message = render_to_string('ticket_status_update.html', context)

        email = EmailMultiAlternatives(
            subject=subject,
            body="",  # No plain text content
            from_email=settings.NO_REPLY_EMAIL,
            to=[self.email],
        )
        email.attach_alternative(html_message, "text/html")
        try:
            email.send()
        except Exception as e:
            logger.error(
                f"Failed to send status update email for ticket {self.id}: {e}"
            )

    def send_ticket_details_email(self):
        """Send ticket details to the user."""
        subject = f"Support Ticket Details: {self.id}"
        context = {
            'ticket': self,
            'django_backend_url': settings.DJANGO_BACKEND_URL,
        }
        html_message = render_to_string('ticket_details.html', context)

        email = EmailMultiAlternatives(
            subject=subject,
            body="",  # No plain text content
            from_email=settings.NO_REPLY_EMAIL,
            to=[self.email],
        )
        email.attach_alternative(html_message, "text/html")
        try:
            email.send()
        except Exception as e:
            logger.error(
                f"Failed to send ticket details email for ticket"
                f"{self.id}: {e}"
            )

    def send_alert_email(self):
        """Send an email when a ticket is associated with an alert."""
        if self.alert_setting and self.alert_setting.email_alert:
            subject = f"Alert: {self.title}"
            context = {
                'ticket': self,
                'django_backend_url': settings.DJANGO_BACKEND_URL,
            }
            html_message = render_to_string(
                'alert_ticket_notification.html',
                context
            )

            email = EmailMultiAlternatives(
                subject=subject,
                body="",  # No plain text content
                from_email=settings.NO_REPLY_EMAIL,
                to=[self.email],
            )
            email.attach_alternative(html_message, "text/html")
            try:
                email.send()
            except Exception as e:
                logger.error(
                    f"Failed to send alert email for ticket {self.id}: {e}"
                )
