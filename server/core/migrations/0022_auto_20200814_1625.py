# Generated by Django 2.2.2 on 2020-08-14 16:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_auto_20200813_2103'),
    ]

    operations = [
        migrations.AddField(
            model_name='ahj',
            name='URL',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='contact',
            name='URL',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='engineeringreviewrequirement',
            name='RequirementLevelNotes',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='historicalahj',
            name='URL',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='historicalcontact',
            name='URL',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='historicalengineeringreviewrequirement',
            name='RequirementLevelNotes',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='contact',
            name='ContactType',
            field=models.CharField(blank=True, choices=[('Homeowner', 'Homeowner'), ('OffTaker', 'Off Taker'), ('Inspector', 'Inspector'), ('Engineer', 'Engineer'), ('Originator', 'Originator'), ('Installer', 'Installer'), ('Investor', 'Investor'), ('PermittingOfficial', 'Permitting Official'), ('FireMarshal', 'Fire Marshal'), ('ProjectManager', 'Project Manager'), ('Salesperson', 'Salesperson')], default='', max_length=45),
        ),
        migrations.AlterField(
            model_name='historicalcontact',
            name='ContactType',
            field=models.CharField(blank=True, choices=[('Homeowner', 'Homeowner'), ('OffTaker', 'Off Taker'), ('Inspector', 'Inspector'), ('Engineer', 'Engineer'), ('Originator', 'Originator'), ('Installer', 'Installer'), ('Investor', 'Investor'), ('PermittingOfficial', 'Permitting Official'), ('FireMarshal', 'Fire Marshal'), ('ProjectManager', 'Project Manager'), ('Salesperson', 'Salesperson')], default='', max_length=45),
        ),
    ]
