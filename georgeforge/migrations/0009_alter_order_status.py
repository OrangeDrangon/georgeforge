# Generated by Django 4.2.13 on 2024-08-03 00:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("georgeforge", "0008_order_status"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="status",
            field=models.IntegerField(
                choices=[
                    (10, "Pending"),
                    (20, "Awaiting Deposit"),
                    (30, "Building"),
                    (40, "Awaiting Final Payment"),
                    (50, "Delivered"),
                    (60, "Rejected"),
                ],
                verbose_name="Status",
            ),
        ),
    ]
