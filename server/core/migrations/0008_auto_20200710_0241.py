# Generated by Django 2.2.2 on 2020-07-10 02:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_auto_20200708_2338'),
    ]

    operations = [
        migrations.AlterField(
            model_name='edit',
            name='PreviousValue',
            field=models.TextField(default=''),
        ),
    ]
