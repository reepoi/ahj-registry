# Generated by Django 2.2.2 on 2020-07-11 04:27

import core.models
from django.conf import settings
from django.db import migrations, models
import simple_history.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_auto_20200710_0248'),
    ]

    operations = [

        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('Address', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.Address')),
                ('Altitude', models.DecimalField(decimal_places=6, max_digits=15, null=True)),
                ('Description', models.TextField(blank=True)),
                ('Elevation', models.DecimalField(decimal_places=6, max_digits=15, null=True)),
                ('Latitude', models.DecimalField(decimal_places=6, max_digits=8, null=True)),
                ('LocationDeterminationMethod', models.CharField(blank=True, choices=[('GPS', 'GPS'), ('Survey', 'Survey'), ('AerialImage', 'Aerial Image'), ('EngineeringReport', 'Engineering Report'), ('AddressGeocoding', 'Address Geocoding'), ('Unknown', 'Unknown')], default='', max_length=45)),
                ('LocationType', models.CharField(blank=True, choices=[('DeviceSpecific', 'Device Specific'), ('SiteEntrance', 'Site Entrance'), ('GeneralProximity', 'General Proximity'), ('Warehouse', 'Warehouse')], default='', max_length=45)),
                ('Longitude', models.DecimalField(decimal_places=6, max_digits=9, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='HistoricalLocation',
            fields=[
                ('id', models.IntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('Altitude', models.DecimalField(decimal_places=6, max_digits=15, null=True)),
                ('Description', models.TextField(blank=True)),
                ('Elevation', models.DecimalField(decimal_places=6, max_digits=15, null=True)),
                ('Latitude', models.DecimalField(decimal_places=6, max_digits=8, null=True)),
                ('LocationDeterminationMethod', models.CharField(blank=True, choices=[('GPS', 'GPS'), ('Survey', 'Survey'), ('AerialImage', 'Aerial Image'), ('EngineeringReport', 'Engineering Report'), ('AddressGeocoding', 'Address Geocoding'), ('Unknown', 'Unknown')], default='', max_length=45)),
                ('LocationType', models.CharField(blank=True, choices=[('DeviceSpecific', 'Device Specific'), ('SiteEntrance', 'Site Entrance'), ('GeneralProximity', 'General Proximity'), ('Warehouse', 'Warehouse')], default='', max_length=45)),
                ('Longitude', models.DecimalField(decimal_places=6, max_digits=9, null=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField()),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('Address', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.Address')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical location',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': 'history_date',
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.AlterField(
            model_name='edit',
            name='FieldName',
            field=models.CharField(default='', max_length=45),
        ),
        migrations.AlterField(
            model_name='edit',
            name='Value',
            field=models.TextField(default=''),
        ),
    ]