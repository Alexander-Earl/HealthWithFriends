# Generated by Django 4.0.2 on 2022-02-20 23:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('healthwithfriends', '0018_alter_user_last_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='userpreferences',
            name='first_name',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='userpreferences',
            name='last_name',
            field=models.BooleanField(default=True),
        ),
    ]