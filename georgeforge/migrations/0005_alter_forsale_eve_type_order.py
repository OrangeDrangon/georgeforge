# Generated by Django 4.2.13 on 2024-08-02 23:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("eveuniverse", "0010_alter_eveindustryactivityduration_eve_type_and_more"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("georgeforge", "0004_alter_forsale_eve_type"),
    ]

    operations = [
        migrations.AlterField(
            model_name="forsale",
            name="eve_type",
            field=models.ForeignKey(
                limit_choices_to={"eve_market_group__isnull": False, "published": 1},
                on_delete=django.db.models.deletion.CASCADE,
                to="eveuniverse.evetype",
                verbose_name="EVE Type",
            ),
        ),
        migrations.CreateModel(
            name="Order",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "price",
                    models.DecimalField(
                        decimal_places=2,
                        help_text="Cost per unit",
                        max_digits=15,
                        verbose_name="Price",
                    ),
                ),
                ("notes", models.TextField(verbose_name="Notes")),
                (
                    "eve_type",
                    models.ForeignKey(
                        limit_choices_to={
                            "eve_market_group__isnull": False,
                            "published": 1,
                        },
                        on_delete=django.db.models.deletion.CASCADE,
                        to="eveuniverse.evetype",
                        verbose_name="EVE Type",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.RESTRICT,
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Purchaser",
                    ),
                ),
            ],
        ),
    ]
