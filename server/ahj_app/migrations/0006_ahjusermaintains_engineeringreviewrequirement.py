# Generated by Django 3.1.3 on 2021-03-16 21:18

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ahj_app', '0005_ahjdocumentsubmissionmethoduse_ahjpermitissuemethoduse_documentsubmissionmethod_permitissuemethod'),
    ]

    operations = [
        migrations.CreateModel(
            name='EngineeringReviewRequirement',
            fields=[
                ('EngineeringReviewRequirementID', models.AutoField(db_column='EngineeringReviewRequirementID', primary_key=True, serialize=False)),
                ('Description', models.CharField(blank=True, db_column='Description', max_length=255)),
                ('EngineeringReviewType', models.CharField(choices=[('', ''), ('StructuralEngineer', 'Structural Engineer'), ('ElectricalEngineer', 'Electrical Engineer'), ('PVEngineer', 'PV Engineer'), ('MasterElectrician', 'Master Electrician'), ('FireMarshal', 'Fire Marshal'), ('EnvironmentalEngineer', 'Environmental Engineer')], db_column='EngineeringReviewType', max_length=21)),
                ('RequirementLevel', models.CharField(choices=[('', ''), ('Required', 'Required'), ('Optional', 'Optional'), ('ConditionallyRequired', 'Conditionally Required')], db_column='RequirementLevel', max_length=21)),
                ('RequirementNotes', models.CharField(blank=True, db_column='RequirementNotes', max_length=255)),
                ('StampType', models.CharField(choices=[('', ''), ('Wet', 'Wet'), ('Digital', 'Digital'), ('Notary', 'Notary'), ('None', 'None')], db_column='StampType', max_length=7)),
                ('AHJPK', models.ForeignKey(db_column='AHJPK', on_delete=django.db.models.deletion.DO_NOTHING, to='ahj_app.ahj')),
            ],
            options={
                'db_table': 'EngineeringReviewRequirement',
                'managed': True,
            },
        ),
        migrations.CreateModel(
            name='AHJUserMaintains',
            fields=[
                ('MaintainerID', models.AutoField(db_column='MaintainerID', primary_key=True, serialize=False)),
                ('MaintainerStatus', models.IntegerField(db_column='MaintainerStatus')),
                ('AHJPK', models.ForeignKey(db_column='AHJPK', on_delete=django.db.models.deletion.DO_NOTHING, to='ahj_app.ahj')),
                ('UserID', models.ForeignKey(db_column='UserID', on_delete=django.db.models.deletion.DO_NOTHING, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'AHJUserMaintains',
                'managed': True,
                'unique_together': {('AHJPK', 'UserID')},
            },
        ),
    ]
