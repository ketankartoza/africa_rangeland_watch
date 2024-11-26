from django.urls import path
from . import views


urlpatterns = [
    path('organisation/<int:organisation_id>/',
         views.organisation_detail,
         name='organisation_detail'),
    path('api/organizations',
         views.fetch_organisation_data,
         name='fetch_organisation_data'),
    path(
        'api/organizations/member/delete/',
        views.delete_organisation_member,
        name='delete_member'),
    path(
        'api/organization/<int:organisation_id>/invite/',
        views.invite_to_organisation,
        name='invite_to_organisation'),
    path(
        'organisation/invite/accept/<int:invitation_id>/',
        views.accept_invite,
        name='organisation-invite-accept'
    ),
]
