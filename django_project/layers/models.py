import uuid
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver
from cloud_native_gis.models.layer import Layer


class DataProvider(models.Model):
    """
    Model to store information about data providers.
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="The name of the data provider."
    )

    file = models.FileField(
        upload_to='data_providers/files/',
        blank=True,
        null=True,
        help_text=(
            "File associated with the data provider, if applicable."
        )
    )

    url = models.URLField(
        blank=True,
        null=True,
        help_text=(
            "URL for the data provider's website or dataset."
        )
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Data Provider"
        verbose_name_plural = "Data Providers"
        ordering = ['name']

    def __str__(self):
        return self.name


class InputLayerType(models.TextChoices):
    """Enum for specifying types of input layers."""

    VECTOR = 'vector', 'Vector'
    RASTER = 'raster', 'Raster'


class LayerGroupType(models.Model):
    """Model to represent layer group type."""

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text="The name of the group type."
    )

    def __str__(self):
        return self.name


class InputLayer(models.Model):
    """
    Model to represent data layers.
    """

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the input layer."
    )

    name = models.CharField(
        max_length=255,
        help_text="Name of the input layer."
    )

    layer_type = models.CharField(
        max_length=50,
        choices=InputLayerType.choices,
        default=InputLayerType.VECTOR,
        help_text="Type of the input layer (e.g., vector, raster)."
    )

    data_provider = models.ForeignKey(
        DataProvider,
        on_delete=models.CASCADE,
        related_name="input_layers",
        help_text="The data provider associated with this layer."
    )

    url = models.URLField(
        blank=True,
        null=True,
        help_text="URL for the input layer."
    )

    group = models.ForeignKey(
        LayerGroupType,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        help_text="Layer group type: baseline, near real time, etc."
    )

    metadata = models.JSONField(
        default=dict,
        blank=True,
        null=True,
        help_text="Layer metadata."
    )

    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="created_layers",
        help_text="User who created this input layer."
    )

    updated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="updated_layers",
        help_text="User who last updated this input layer."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Input Layer"
        verbose_name_plural = "Input Layers"
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_vis_params(self):
        """Convert metadata to GEE vis params."""
        return {
            'min': self.metadata['minValue'],
            'max': self.metadata['maxValue'],
            'palette': self.metadata['colors'],
            'opacity': self.metadata['opacity']
        }


class DataFeedSetting(models.Model):
    """
    Model to store settings for data feeds.
    """

    FREQUENCY_CHOICES = [
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]

    uuid = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the data feed setting."
    )

    provider = models.ForeignKey(
        DataProvider,
        on_delete=models.CASCADE,
        related_name="data_feed_settings",
        help_text=(
            "The data provider associated with this data feed setting."
        )
    )

    frequency = models.CharField(
        max_length=20,
        choices=FREQUENCY_CHOICES,
        default='weekly',
        help_text="Frequency of data feed updates."
    )

    enable_alert = models.BooleanField(
        default=False,
        help_text="Enable or disable alerts for this data feed."
    )

    email_alert = models.BooleanField(
        default=False,
        help_text="Enable email alerts for this data feed."
    )

    in_app_alert = models.BooleanField(
        default=False,
        help_text="Enable in-app alerts for this data feed."
    )

    last_sync_timestamp = models.DateTimeField(
        blank=True,
        null=True,
        help_text="Timestamp of the last successful sync."
    )

    last_sync_status = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Status message of the last sync operation."
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Data Feed Setting"
        verbose_name_plural = "Data Feed Settings"
        ordering = ['provider', 'frequency']

    def __str__(self):
        return f"{self.provider.name} Feed - {self.frequency}"


@receiver(post_delete, sender=InputLayer)
def input_layer_on_delete(sender, instance: InputLayer, using, **kwargs):
    """Delete layer in cloud_native_gis."""
    layer = Layer.objects.filter(
        unique_id=instance.uuid
    ).first()
    if layer is None:
        return
    layer.delete()
