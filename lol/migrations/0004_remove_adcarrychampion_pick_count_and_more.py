# Generated by Django 4.2.19 on 2025-03-04 01:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('lol', '0003_team_alter_match_blue_team_alter_match_red_team_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='adcarrychampion',
            name='pick_count',
        ),
        migrations.RemoveField(
            model_name='adcarrychampion',
            name='win_count',
        ),
        migrations.AlterField(
            model_name='adcarrychampion',
            name='champion',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='adc_champion', to='lol.champion'),
        ),
        migrations.AlterField(
            model_name='junglechampion',
            name='champion',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='jungle_champion', to='lol.champion'),
        ),
        migrations.AlterField(
            model_name='midchampion',
            name='champion',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='mid_champion', to='lol.champion'),
        ),
        migrations.AlterField(
            model_name='supportchampion',
            name='champion',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='support_champion', to='lol.champion'),
        ),
        migrations.AlterField(
            model_name='topchampion',
            name='champion',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='top_champion', to='lol.champion'),
        ),
    ]
