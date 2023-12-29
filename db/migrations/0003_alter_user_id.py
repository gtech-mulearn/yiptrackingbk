# Generated by Django 4.2.6 on 2023-12-29 10:57

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('db', '0002_user_delete_customuser'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='id',
            field=models.CharField(default=uuid.uuid4, max_length=100, primary_key=True, serialize=False, unique=True),
        ),
    ]