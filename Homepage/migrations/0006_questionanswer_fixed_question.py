# Generated by Django 5.1 on 2024-08-21 15:33

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Homepage', '0005_alter_fixedquestions_created_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='questionanswer',
            name='fixed_question',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='Homepage.fixedquestions'),
        ),
    ]