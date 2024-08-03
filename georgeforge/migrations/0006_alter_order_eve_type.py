# Generated by Django 4.2.13 on 2024-08-02 23:19

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("eveuniverse", "0010_alter_eveindustryactivityduration_eve_type_and_more"),
        ("georgeforge", "0005_alter_forsale_eve_type_order"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="eve_type",
            field=models.ForeignKey(
                limit_choices_to={"published": 1},
                on_delete=django.db.models.deletion.CASCADE,
                to="eveuniverse.evetype",
                verbose_name="EVE Type",
            ),
        ),
    ]
