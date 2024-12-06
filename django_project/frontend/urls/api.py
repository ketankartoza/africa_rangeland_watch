# coding=utf-8
"""
Africa Rangeland Watch (ARW).

.. note:: ARW Frontend API urls.
"""

from django.urls import path
from rest_framework.routers import DefaultRouter

from frontend.api_views.base_map import BaseMapAPI, MapConfigAPI
from frontend.api_views.landscape import LandscapeViewSet
from frontend.api_views.layers import LayerAPI, UploadLayerAPI

router = DefaultRouter()
router.register(r'landscapes', LandscapeViewSet, basename='landscapes')

# BaseMap APIs
base_map_urls = [
    path(
        'base-map/',
        BaseMapAPI.as_view(),
        name='base-map'
    ),
    path(
        'map-config/',
        MapConfigAPI.as_view(),
        name='map-config'
    )
]

# Layers APIs
layers_urls = [
    path(
        'layer/',
        LayerAPI.as_view(),
        name='layer'
    ),
    path(
        'upload-layer/',
        UploadLayerAPI.as_view(),
        name='upload-layer'
    )
]

urlpatterns = base_map_urls + layers_urls + router.urls + [
    # Custom route for vector tiles
    path(
        'landscapes/vector_tile/<int:z>/<int:x>/<int:y>/',
        LandscapeViewSet.as_view({'get': 'vector_tile'}),
        name='landscape-vector-tile'
    ),
]
