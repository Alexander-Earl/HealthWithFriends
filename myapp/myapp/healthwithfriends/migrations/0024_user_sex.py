# Generated by Django 4.0.2 on 2022-03-28 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthwithfriends', '0023_exercise'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='sex',
            field=models.BooleanField(default=True),
            preserve_default=False,
        ),
    ]