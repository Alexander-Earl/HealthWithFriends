# Generated by Django 3.2.7 on 2022-01-30 17:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('healthwithfriends', '0003_auto_20220130_1743'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='preferences',
            field=models.OneToOneField(default=1, on_delete=django.db.models.deletion.CASCADE, to='healthwithfriends.userpreferences'),
            preserve_default=False,
        ),
    ]