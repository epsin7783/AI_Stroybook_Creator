# Generated by Django 5.1.2 on 2024-11-05 08:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_scenario_recommendations'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenario',
            name='selected_story',
            field=models.TextField(blank=True, null=True, verbose_name='선택된 시나리오'),
        ),
        migrations.AddField(
            model_name='scenario',
            name='story_pages',
            field=models.JSONField(default=list, verbose_name='동화책 페이지'),
        ),
    ]