# Generated by Django 4.2.19 on 2025-03-12 06:13

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('analysis', '0009_analysisresultscache'),
    ]

    operations = [
        migrations.CreateModel(
            name='AnalysisRasterOutput',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, help_text='Unique identifier for the raster.', primary_key=True, serialize=False)),
                ('name', models.TextField()),
                ('size', models.BigIntegerField(default=0)),
                ('status', models.CharField(max_length=255)),
                ('generate_start_time', models.DateTimeField(blank=True, null=True)),
                ('generate_end_time', models.DateTimeField(blank=True, null=True)),
                ('status_logs', models.JSONField(blank=True, default=dict, null=True)),
                ('analysis', models.JSONField(default=dict)),
            ],
        ),
        migrations.AddField(
            model_name='useranalysisresults',
            name='raster_outputs',
            field=models.ManyToManyField(related_name='analysis_results', to='analysis.analysisrasteroutput'),
        ),
    ]
