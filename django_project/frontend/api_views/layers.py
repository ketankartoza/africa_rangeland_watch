# coding=utf-8
"""
Africa Rangeland Watch (ARW).

.. note:: Layer APIs
"""

import os
from django.core.files.storage import FileSystemStorage
from django.http import FileResponse
from django.conf import settings
from django.urls import reverse
from django.core.files.uploadedfile import TemporaryUploadedFile
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from cloud_native_gis.models import Layer, LayerUpload
from cloud_native_gis.utils.main import id_generator
from django.shortcuts import get_object_or_404
from cloud_native_gis.utils.fiona import (
    FileType,
    validate_shapefile_zip,
    validate_collection_crs,
    delete_tmp_shapefile,
    open_fiona_collection
)

from layers.models import InputLayer, DataProvider, LayerGroupType
from frontend.serializers.layers import LayerSerializer
from layers.tasks.import_layer import (
    import_layer,
    detect_file_type_by_extension
)


class LayerAPI(APIView):
    """API to return list of Layer."""

    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """Fetch list of Layer."""
        layers = InputLayer.objects.exclude(
            group__name='user-defined'
        )
        if self.request.user.is_authenticated:
            layers = layers.union(
                InputLayer.objects.filter(
                    group__name='user-defined',
                    created_by=request.user
                ).exclude(
                    url__isnull=True
                )
            )
        return Response(
            status=200,
            data=LayerSerializer(
                layers,
                many=True
            ).data
        )


class UploadLayerAPI(APIView):
    """API to upload a layer."""

    permission_classes = [IsAuthenticated]

    def _check_file_type(self, filename: str) -> str:
        """Check file type from upload filename.

        :param filename: filename of uploaded file
        :type filename: str
        :return: file type
        :rtype: str
        """
        if filename.lower().endswith('.zip'):
            return FileType.SHAPEFILE
        return ''

    def _check_shapefile_zip(self, file_obj: any) -> str:
        """Validate if zip shapefile has complete files.

        :param file_obj: file object
        :type file_obj: file
        :return: list of error
        :rtype: str
        """
        _, error = validate_shapefile_zip(file_obj)
        if error:
            return (
                'Missing required file(s) inside zip file: \n- ' +
                '\n- '.join(error)
            )
        return ''

    def _remove_temp_files(self, file_obj_list: list) -> None:
        """Remove temporary files.

        :param file_obj: list temporary files
        :type file_obj: list
        """
        for file_obj in file_obj_list:
            if isinstance(file_obj, TemporaryUploadedFile):
                if os.path.exists(file_obj.temporary_file_path()):
                    os.remove(file_obj.temporary_file_path())
            elif isinstance(file_obj, str):
                delete_tmp_shapefile(file_obj)

    def _on_validation_error(self, error: str, file_obj_list: list):
        """Handle when there is error on validation."""
        self._remove_temp_files(file_obj_list)
        raise ValidationError({
            'Invalid uploaded file': error
        })

    def post(self, request):
        """Post file."""
        file = None
        file_url = request.data.get('file_url', None)
        if request.FILES:
            file = request.FILES['file']
        elif file_url is None:
            raise ValidationError({
                'Invalid uploaded file': 'Missing required file!'
            })

        tmp_file_obj_list = [file]

        # validate uploaded file
        file_type = self._check_file_type(file.name)
        if file_type == '':
            self._on_validation_error(
                'Unrecognized file type! Please upload the zip of shapefile!',
                tmp_file_obj_list
            )

        if file_type == FileType.SHAPEFILE:
            validate_shp_file = self._check_shapefile_zip(file)
            if validate_shp_file != '':
                self._on_validation_error(
                    validate_shp_file, tmp_file_obj_list)

        # open fiona collection
        collection = open_fiona_collection(file, file_type)
        tmp_file_obj_list.append(collection.path)

        is_valid_crs, crs = validate_collection_crs(collection)
        if not is_valid_crs:
            collection.close()
            self._on_validation_error(
                f'Incorrect CRS type: {crs}! Please use epsg:4326 (WGS84)!',
                tmp_file_obj_list
            )

        # close collection
        collection.close()

        # remove temporary uploaded file if any
        self._remove_temp_files(tmp_file_obj_list)

        # create layer
        layer = Layer.objects.create(
            created_by=request.user
        )
        # create InputLayer
        input_layer = InputLayer.objects.create(
            uuid=layer.unique_id,
            name=str(layer.unique_id),
            data_provider=DataProvider.objects.get(name='User defined'),
            group=LayerGroupType.objects.get(name='user-defined'),
            created_by=request.user,
            updated_by=request.user
        )

        instance = LayerUpload(
            created_by=request.user, layer=layer
        )
        instance.emptying_folder()

        # Save files
        if file:
            FileSystemStorage(
                location=instance.folder
            ).save(file.name, file)
            input_layer.name = file.name
            input_layer.layer_type = detect_file_type_by_extension(
                file.name
            )
            input_layer.save()
        instance.save()

        # trigger task import the layer
        import_layer.delay(layer.unique_id, instance.id, file_url)

        return Response(
            status=200,
            data={
                'id': str(layer.unique_id),
                'layer_id': str(layer.id),
                'upload_id': str(instance.id)
            }
        )


class PMTileLayerAPI(APIView):
    """API to fix PMTile generation."""

    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        """Post PMTile file to be saved in layer directory."""
        instance = get_object_or_404(
            LayerUpload,
            id=kwargs.get('upload_id')
        )
        layer = instance.layer
        input_layer = get_object_or_404(
            InputLayer,
            uuid=layer.unique_id
        )

        # Save files
        if request.FILES:
            pmtiles_filename = f"{id_generator()}.pmtiles"
            layer.is_ready = True
            layer.pmtile.save(
                pmtiles_filename,
                request.FILES['file'],
                save=True
            )

            # update url in InputLayer
            base_url = settings.DJANGO_BACKEND_URL
            if base_url.endswith('/'):
                base_url = base_url[:-1]
            if layer.pmtile:
                input_layer.url = (
                    f'pmtiles://{base_url}' +
                    reverse('serve-pmtiles', kwargs={
                        'layer_uuid': layer.unique_id,
                    })
                )
            else:
                input_layer.url = base_url + layer.tile_url

            input_layer.save()

        return Response('OK')

    def get(self, request, *args, **kwargs):
        """Get shapefile from LayerUpload."""
        instance = get_object_or_404(
            LayerUpload,
            id=kwargs.get('upload_id')
        )

        shapefile_path = None
        for file in instance.files:
            if file.endswith('.zip'):
                shapefile_path = instance.filepath(file)
                break

        if shapefile_path is None or not os.path.exists(shapefile_path):
            return Response(
                status=404,
                data='Missing uploaded zip shapefile!'
            )

        response = FileResponse(
            open(shapefile_path, 'rb'),
            as_attachment=True,
            filename=f'{id_generator()}.zip'
        )

        return response
