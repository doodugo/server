# Generated by Django 5.0.12 on 2025-03-04 02:36

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lol', '0004_remove_adcarrychampion_pick_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='sets',
            field=models.IntegerField(default=0),
        ),
    ]
