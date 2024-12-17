from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    Organisation,
    UserProfile,
    OrganisationInvitation,
    UserOrganisations
)
from django.conf import settings
from django.template.loader import render_to_string
import json
from django.core.mail import EmailMultiAlternatives
from django.shortcuts import get_object_or_404



@admin.action(description="Approve selected join/add requests")
def approve_join_request(modeladmin, request, queryset):
    """
    Admin action to approve join/add requests.
    Creates organisations for 'add_organisation' requests and assigns roles.
    """
    for invitation in queryset:
        if invitation.request_type == "add_organisation":
            # Parse metadata from the invitation
            metadata = json.loads(invitation.metadata or "{}")
            organisation_name = metadata.get("organisationName", "")

            # Create the organisation
            organisation = Organisation.objects.create(name=organisation_name)

            # Assign the inviter as the organisation manager
            inviter = invitation.inviter
            user_profile = get_object_or_404(UserProfile, user=inviter)
            UserOrganisations.objects.create(
                user_profile=user_profile,
                organisation=organisation,
                user_type='manager'
            )

            # Notify the inviter
            email_body = render_to_string(
                "organization_manager_notification.html",
                {
                    "user": inviter,
                    "organisation": organisation,
                    "support_email": "support@kartoza.com",
                    "platform_url": settings.DJANGO_BACKEND_URL,
                },
            )
            try:
                email = EmailMultiAlternatives(
                    subject="Your Role as Organisation Manager",
                    body="",
                    from_email=settings.NO_REPLY_EMAIL,
                    to=[inviter.email],
                )
                email.attach_alternative(email_body, "text/html")
                email.send()
            except Exception as e:
                modeladmin.message_user(
                    request,
                    f"Failed to send email: {str(e)}",
                    level="error",
                )


            modeladmin.message_user(
                request,
                f"Organisation '{organisation.name}' created and request "
                "approved.",
            )
            return

        elif invitation.request_type == "join_organisation":
            # Process join requests
            inviter = invitation.inviter
            user_profile = get_object_or_404(UserProfile, user=inviter)
            organisation = invitation.organisation

            UserOrganisations.objects.create(
                user_profile=user_profile,
                organisation=organisation,
                user_type='member'
            )

            email_body = render_to_string(
                "accepted_organization_request.html",
                {
                    "user": inviter,
                    "organisation": organisation,
                    "link": settings.DJANGO_BACKEND_URL,
                },
            )
            try:
                email = EmailMultiAlternatives(
                    subject="Your join request has been approved",
                    body="",
                    from_email=settings.NO_REPLY_EMAIL,
                    to=[inviter.email],
                )
                email.attach_alternative(email_body, "text/html")
                email.send()
            except Exception as e:
                modeladmin.message_user(
                    request,
                    f"Failed to send email: {str(e)}",
                    level="error",
                )


            modeladmin.message_user(
                request, "Individual has been added."
            )
            return





class OrganisationInvitationAdmin(admin.ModelAdmin):
    list_display = ('email', 'request_type', 'organisation', 'inviter')
    actions = [approve_join_request]
    list_filter = ('organisation', 'request_type')
    search_fields = ('email', 'organisation__name', 'inviter__username')


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "User Profile"
    fk_name = "user"
    fields = (
        'country',
        'created_at', 'updated_at', 'organisations_list',
        'profile_image'
    )
    readonly_fields = ('created_at', 'updated_at', 'organisations_list')

    def organisations_list(self, obj):
        """
        Custom method to display the organisations and roles associated with
        the user.
        """
        orgs_with_roles = UserOrganisations.objects.filter(
            user_profile=obj.user)
        return ", ".join(
            [
                f"{org.organisation.name} - {org.user_type}"
                for org in orgs_with_roles
            ]
        )

    organisations_list.short_description = "Organisations & Roles"




class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)

    list_display = ('username', 'email', 'first_name', 'last_name',
                    'is_staff', 'get_user_role')
    list_select_related = ('profile',)
    search_fields = ('username', 'email', 'first_name', 'last_name')

    def get_user_role(self, instance):
        """Return user role."""
        return instance.profile.user_role

    get_user_role.short_description = 'User Role'

    def get_inline_instances(self, request, obj=None):
        """Return inline instances."""
        if not obj:
            return []
        return super(UserAdmin, self).get_inline_instances(request, obj)



class UserOrganisationsAdmin(admin.ModelAdmin):
    list_display = ('user_profile', 'organisation', 'user_type')
    search_fields = ('user_profile__user__username', 'organisation__name')
    list_filter = ('user_type', 'organisation')
    raw_id_fields = ('organisation',)
    # autocomplete_fields = ('organisation',)

    def get_queryset(self, request):
        return super().get_queryset(request)




@admin.register(Organisation)
class OrganisationAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at', 'updated_at')
    search_fields = ('name',)
    ordering = ('name',)
    readonly_fields = ('created_at', 'updated_at')



admin.site.register(UserOrganisations, UserOrganisationsAdmin)

admin.site.unregister(User)
admin.site.register(User, UserAdmin)
admin.site.unregister(OrganisationInvitation)
admin.site.register(OrganisationInvitation, OrganisationInvitationAdmin)
