# Generated by Django 3.1.3 on 2021-03-16 02:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ahj_app', '0004_auto_20210312_2016'),
    ]

    operations = [
        migrations.CreateModel(
            name='DocumentSubmissionMethod',
            fields=[
                ('DocumentSubmissionMethodID', models.AutoField(db_column='DocumentSubmissionMethodID', primary_key=True, serialize=False)),
                ('Value', models.CharField(choices=[('', ''), ('Epermitting', 'Epermitting'), ('Email', 'Email'), ('InPerson', 'In Person'), ('SolarApp', 'SolarAPP')], db_column='Value', max_length=11, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='PermitIssueMethod',
            fields=[
                ('PermitIssueMethodID', models.AutoField(db_column='PermitIssueMethodID', primary_key=True, serialize=False)),
                ('Value', models.CharField(choices=[('', ''), ('Epermitting', 'Epermitting'), ('Email', 'Email'), ('InPerson', 'In Person'), ('SolarApp', 'SolarAPP')], db_column='Value', max_length=11, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='AHJPermitIssueMethodUse',
            fields=[
                ('UseID', models.AutoField(db_column='UseID', primary_key=True, serialize=False)),
                ('MethodStatus', models.IntegerField(db_column='MethodStatus')),
                ('AHJPK', models.ForeignKey(db_column='AHJPK', on_delete=django.db.models.deletion.DO_NOTHING, to='ahj_app.ahj')),
                ('PermitIssueMethodID', models.ForeignKey(db_column='PermitIssueMethodID', on_delete=django.db.models.deletion.DO_NOTHING, to='ahj_app.permitissuemethod')),
            ],
            options={
                'db_table': 'AHJPermitIssueMethodUse',
                'managed': True,
                'unique_together': {('AHJPK', 'PermitIssueMethodID')},
            },
        ),
        migrations.CreateModel(
            name='AHJDocumentSubmissionMethodUse',
            fields=[
                ('UseID', models.AutoField(db_column='UseID', primary_key=True, serialize=False)),
                ('MethodStatus', models.IntegerField(db_column='MethodStatus')),
                ('AHJPK', models.ForeignKey(db_column='AHJPK', on_delete=django.db.models.deletion.DO_NOTHING, to='ahj_app.ahj')),
                ('DocumentSubmissionMethodID', models.ForeignKey(db_column='DocumentSubmissionMethodID', on_delete=django.db.models.deletion.DO_NOTHING, to='ahj_app.documentsubmissionmethod')),
            ],
            options={
                'db_table': 'AHJDocumentSubmissionMethodUse',
                'managed': True,
                'unique_together': {('AHJPK', 'DocumentSubmissionMethodID')},
            },
        ),
    ]
