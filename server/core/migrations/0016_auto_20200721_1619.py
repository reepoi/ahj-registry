# Generated by Django 2.2.2 on 2020-07-21 16:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_vote'),
    ]

    operations = [
        migrations.AlterField(
            model_name='vote',
            name='VoteType',
            field=models.BooleanField(),
        ),
    ]
