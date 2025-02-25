from django.urls import path
from .views import (
    DashboardCreateView,
    DashboardListCreateView,
    DashboardRetrieveUpdateDestroyView,
    DashboardShareView,
)


urlpatterns = [
    path(
        'dashboards/',
        DashboardListCreateView.as_view(),
        name='dashboard-list-create'
    ),
    path(
        'dashboards/<uuid:pk>/',
        DashboardRetrieveUpdateDestroyView.as_view(),
        name='dashboard-detail'
    ),
    path(
        'dashboards/<uuid:pk>/share/',
        DashboardShareView.as_view(),
        name='dashboard-share'
    ),
    path(
        'dashboards/create/',
        DashboardCreateView.as_view(),
        name='dashboard-create'
    ),
]
