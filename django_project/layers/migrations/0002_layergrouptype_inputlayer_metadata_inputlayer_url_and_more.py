# Generated by Django 4.2.15 on 2024-11-20 15:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('layers', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LayerGroupType',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='The name of the group type.', max_length=255, unique=True)),
            ],
        ),
        migrations.AddField(
            model_name='inputlayer',
            name='metadata',
            field=models.JSONField(blank=True, default=dict, help_text='Layer metadata.', null=True),
        ),
        migrations.AddField(
            model_name='inputlayer',
            name='url',
            field=models.URLField(blank=True, help_text='URL for the input layer.', null=True),
        ),
        migrations.AddField(
            model_name='inputlayer',
            name='group',
            field=models.ForeignKey(blank=True, help_text='Layer group type: baseline, near real time, etc.', null=True, on_delete=django.db.models.deletion.CASCADE, to='layers.layergrouptype'),
        ),
    ]