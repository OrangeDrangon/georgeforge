# Generated by Django 4.2.13 on 2024-08-03 00:03

# Django
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    """ """

    dependencies = [
        ("eveuniverse", "0010_alter_eveindustryactivityduration_eve_type_and_more"),
        ("georgeforge", "0006_alter_order_eve_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="description",
            field=models.TextField(
                blank=True, max_length=4096, verbose_name="Description"
            ),
        ),
        migrations.AlterField(
            model_name="forsale",
            name="description",
            field=models.TextField(
                blank=True, max_length=4096, verbose_name="Description"
            ),
        ),
        migrations.AlterField(
            model_name="forsale",
            name="eve_type",
            field=models.ForeignKey(
                limit_choices_to={"published": 1},
                on_delete=django.db.models.deletion.CASCADE,
                to="eveuniverse.evetype",
                verbose_name="EVE Type",
            ),
        ),
        migrations.AlterField(
            model_name="order",
            name="notes",
            field=models.TextField(max_length=4096, verbose_name="Notes"),
        ),
    ]
