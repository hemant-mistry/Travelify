# Generated by Django 4.2.13 on 2024-07-08 16:03

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('frugalooAPI', '0002_usertripinfo_generated_plan_usertripinfo_trip_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertripinfo',
            name='generated_plan',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='usertripinfo',
            name='trip_id',
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
    ]
