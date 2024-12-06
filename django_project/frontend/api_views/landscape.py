# coding=utf-8
"""
Africa Rangeland Watch (ARW).

.. note:: Landscape APIs
"""
from django.http import Http404, HttpResponse
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.viewsets import mixins, GenericViewSet

from analysis.models import Landscape, LandscapeCommunity
from core.pagination import Pagination
from frontend.serializers.landscape import LandscapeSerializer
from layers.models import InputLayer
from layers.utils import querying_vector_tile


class LandscapeViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    GenericViewSet
):
    """Activity ViewSet."""

    permission_classes = (AllowAny,)
    serializer_class = LandscapeSerializer
    queryset = Landscape.objects.all()
    pagination_class = Pagination
    throttle_classes = []  # Apply globally for all actions

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.
        """
        context = super().get_serializer_context()
        nrt_layers = InputLayer.objects.filter(
            group__name='near-real-time'
        )
        context['nrt_layers'] = [str(layer.uuid) for layer in nrt_layers]
        return context

    def get_throttles(self):
        """Get throttle classes."""
        throttles = super().get_throttles()
        if self.action == 'vector_tile':
            throttles = []
        return throttles

    @action(detail=False, methods=["get"])
    def vector_tile(self, request, z, x, y):
        """Return vector tile of landscape."""
        tiles = querying_vector_tile(
            LandscapeCommunity._meta.db_table,
            field_names=[
                'id', 'landscape_id', 'community_id', 'community_name'
            ],
            z=z, x=x, y=y
        )

        # If no tile 404
        if not len(tiles):
            raise Http404()
        return HttpResponse(tiles, content_type="application/x-protobuf")
