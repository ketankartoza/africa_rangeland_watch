from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required

from .forms import OrganisationInviteForm
from .models import (
    Organisation,
    OrganisationInvitation,
    UserProfile
)
from django.http import JsonResponse
import json
from invitations.utils import get_invitation_model
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


Invitation = get_invitation_model()



@login_required
def fetch_organisations(request):
    organisations = Organisation.objects.values("id", "name")
    return JsonResponse(list(organisations), safe=False)


@login_required
def join_organisation(request):
    """
    Handles requests to join an organisation. Sends an email notification
    to the manager of the organisation for approval.
    """
    data = json.loads(request.body)

    try:
        # Convert the selectedOrganisationId to an integer
        selected_org_id = int(data["selectedOrganisationId"])
        selected_org = Organisation.objects.get(id=selected_org_id)
    except ValueError:
        return JsonResponse(
            {"error": "Invalid organisation ID format."}, status=400
        )
    except Organisation.DoesNotExist:
        return JsonResponse(
            {"error": "Organisation does not exist."}, status=400
        )

    # Find a manager of the selected organisation
    try:
        manager_profile = UserProfile.objects.get(
            organisation=selected_org, user_type="organisation_manager"
        )
        manager_user = manager_profile.user
    except UserProfile.DoesNotExist:
        return JsonResponse(
            {"error": "No manager found for this organisation."}, status=400
        )

    # Manager's email
    manager_email = manager_user.email

    # Email content rendering
    link = (
        f"{settings.DJANGO_BACKEND_URL}/admin/base/organisationinvitation/"
        f"{selected_org.id}/change/"
    )
    email_body = render_to_string(
        "join_organization_request.html",
        {
            "user": request.user,
            "organisation": selected_org.name,
            "link": link,
        },
    )

    # Send the email to the manager
    try:
        email = EmailMultiAlternatives(
            subject="Request to join organisation",
            body="",  # Empty plain text content
            from_email=settings.NO_REPLY_EMAIL,
            to=[manager_email],
        )
        email.attach_alternative(email_body, "text/html")
        email.send()
    except Exception as e:
        return JsonResponse(
            {"error": f"Failed to send email: {str(e)}"}, status=500
        )

    try:
        OrganisationInvitation.objects.create(
            inviter=request.user,
            email=request.user.email,
            organisation=selected_org,
            request_type="join_organisation",
        )
    except Exception as e:
        return JsonResponse(
            {"error": f"Failed to create invitation: {str(e)}"}, status=500
        )

    return JsonResponse({"message": "Request sent successfully!"})



@login_required
def add_organisation(request):
    """
    Handles requests to add a new organisation. Sends an email notification
    to the admin for approval.
    """
    data = json.loads(request.body)

    # Create the organisation invitation
    OrganisationInvitation.objects.create(
        inviter=request.user,
        email=data.get("organisationEmail", ""),
        request_type="add_organisation",
        organisation=None,
        metadata=json.dumps(
            {
                "organisationName": data.get("organisationName", ""),
                "industry": data.get("industry", ""),
                "requester": {
                    "first_name": data.get("firstName", ""),
                    "last_name": data.get("lastName", ""),
                },
            }
        ),
    )

    # Get the email of the first superuser
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        return JsonResponse(
            {"error": "No admin user found to process the request."},
            status=500,
        )

    admin_email = admin_user.email

    # Render the email content
    email_body = render_to_string(
        "request_to_add_organization.html",
        {
            "requester": {
                "first_name": data.get("firstName", ""),
                "last_name": data.get("lastName", ""),
            },
            "organisation": {
                "name": data.get("organisationName", ""),
                "email": data.get("organisationEmail", ""),
                "industry": data.get("industry", ""),
            },
        },
    )

    # Prepare and send the email
    email = EmailMultiAlternatives(
        subject="New Organisation Request",
        body="",
        from_email=settings.NO_REPLY_EMAIL,
        to=[admin_email],
    )
    email.attach_alternative(email_body, "text/html")
    email.send()

    return JsonResponse({"message": "Request sent successfully!"})


@login_required
def delete_organisation_member(request):
    """
    View to remove a member from an organization by clearing the
    `organisation` field in UserProfile.
    """
    if request.method != "DELETE":
        return JsonResponse(
            {"error": "Invalid HTTP method. Use DELETE."},
            status=405
        )

    try:
        body = json.loads(request.body)
        organisation_id = body.get("organisation_id")
        user_email = body.get("user_email")

        if not organisation_id or not user_email:
            return JsonResponse(
                {"error": "Organisation ID and User Email are required."},
                status=400
            )

        organisation = get_object_or_404(Organisation, id=organisation_id)
        user_profile = get_object_or_404(UserProfile, user__email=user_email)

        if request.user.profile.user_type != "organisation_manager":
            return JsonResponse(
                {"error": "You don't have permission to remove members."},
                status=403
            )
        if user_profile.organisation != organisation:
            return JsonResponse(
                {"error": "User is not a member of this organization."},
                status=400
            )

        user_profile.organisation = None
        user_profile.save()

        return JsonResponse(
            {"message": "Member removed successfully."},
            status=200
        )

    except Exception as e:
        return JsonResponse(
            {"error": "An error occurred.", "details": str(e)},
            status=500
        )


@login_required
def fetch_organisation_data(request):
    """
    Fetch organization data based on the user's role and type.
    Includes members and invitations at the organization level.
    """
    try:
        user_profile = request.user.profile

        # Fetch all organizations the user belongs to
        organisations = Organisation.objects.filter(members=user_profile)

        if not organisations.exists():
            return JsonResponse(
                {"error": "User is not part of any organizations."},
                status=403
            )

        data = {}
        for org in organisations:
            members = list(
                org.members.exclude(user=request.user).values(
                    "user__email", "user_role"
                )
            )

            invitations = []
            invitations = list(
                org.custom_invitations.values("email", "accepted")
            )

            is_manager = org.members.filter(
                user=request.user,
                user_type='organisation_manager'
            ).exists()


            data[org.name] = {
                "org_id": org.id,
                "members": members,
                "invitations": invitations,
                "is_manager": is_manager
            }

        return JsonResponse(data, status=200)

    except AttributeError as e:
        return JsonResponse(
            {
                "error": "User profile is not set up correctly.",
                "details": str(e)
            },
            status=500
        )
    except Exception as e:
        return JsonResponse(
            {"error": "An unexpected error occurred.", "details": str(e)},
            status=500
        )


@login_required
def invite_to_organisation(request, organisation_id):
    """View to invite a user to an organisation."""
    try:
        # Ensure the organisation exists
        organisation = get_object_or_404(Organisation, id=organisation_id)

        if request.method != 'POST':
            return JsonResponse(
                {"error": "Invalid HTTP method. Use POST."},
                status=405
            )

        # Parse JSON payload
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON payload."}, status=400)

        form = OrganisationInviteForm(data)
        if not form.is_valid():
            return JsonResponse(
                {"error": "Form validation failed", "details": form.errors},
                status=400
            )

        email = form.cleaned_data["email"]
        message = data.get("message", "")

        # Check if the user has permission to invite
        user_profile = get_object_or_404(UserProfile, user=request.user)
        if (
                user_profile.user_type != 'organisation_manager' or
                user_profile.organisation != organisation
        ):
            return JsonResponse(
                {"error": "You do not have permission to invite users."},
                status=403
            )

        invitation = OrganisationInvitation.objects.filter(
            email=email,
            organisation=organisation
        ).first()
        if not invitation:
            invitation = OrganisationInvitation.objects.create(
                email=email,
                inviter=request.user,
                organisation=organisation
            )

            # Send the invitation
            try:
                invitation.send_invitation(
                    request=request,
                    custom_message=message
                )
                return JsonResponse({"success": True}, status=200)
            except Exception as e:
                return JsonResponse(
                    {
                        "error": "Failed to send invitation.",
                        "details": str(e)
                    }, status=500)

    except Organisation.DoesNotExist:
        return JsonResponse({"error": "Organisation not found."}, status=404)
    except Exception as e:
        print(str(e))
        return JsonResponse(
            {
                "error": "An unexpected error occurred",
                "details": str(e)
            }, status=500)




@login_required
def organisation_detail(request, organisation_id):
    """View to display the details of an organisation."""
    organisation = get_object_or_404(Organisation, id=organisation_id)
    return render(request,
                  'organisation_detail.html',
                  {'organisation': organisation})



def accept_invite(request, invitation_id):
    invitation = get_object_or_404(OrganisationInvitation, id=invitation_id)

    try:
        user = User.objects.get(email=invitation.email)
    except User.DoesNotExist:
        return redirect(f"{reverse('home')}?register_first=true")

    user_profile = UserProfile.objects.get(user=user)

    if user_profile.organisation == invitation.organisation:
        return JsonResponse(
            {
                "error": "You are already a member of this organization."
            },
            status=400
        )

    user_profile.organisation = invitation.organisation
    user_profile.save()

    return redirect(f"{reverse('home')}?invitation_accepted=true")
