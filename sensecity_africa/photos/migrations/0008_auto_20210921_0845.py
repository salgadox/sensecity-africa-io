# Generated by Django 3.1.12 on 2021-09-21 06:45

from django.db import migrations
import location_field.models.spatial


class Migration(migrations.Migration):

    dependencies = [
        ('photos', '0007_photo_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='photo',
            name='location',
            field=location_field.models.spatial.LocationField(blank=True, null=True, srid=4326, verbose_name='Location'),
        ),
    ]