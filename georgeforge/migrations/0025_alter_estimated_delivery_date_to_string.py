# Generated migration

# Django
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("georgeforge", "0024_add_order_estimated_delivery_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="order",
            name="estimated_delivery_date",
            field=models.CharField(
                blank=True,
                help_text="Estimated date when the order will be delivered",
                max_length=50,
                null=True,
                verbose_name="Estimated Delivery Date",
            ),
        ),
    ]
