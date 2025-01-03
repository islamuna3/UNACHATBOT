# Generated by Django 5.1 on 2024-08-20 07:51

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Homepage', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SuggestedQuestion',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('question', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
