# Generated by Django 4.2.13 on 2024-07-27 10:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('frugalooAPI', '0011_financelog'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageLog',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('user_id', models.CharField(max_length=255)),
                ('question', models.CharField(max_length=255)),
                ('sql_query', models.TextField()),
            ],
        ),
    ]
