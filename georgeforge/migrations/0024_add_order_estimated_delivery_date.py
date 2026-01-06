# Generated migration for estimated_delivery_date field

# Django
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("georgeforge", "0023_remove_cart_session_id_unique"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="estimated_delivery_date",
            field=models.DateField(
                blank=True,
                help_text="Estimated date when the order will be delivered",
                null=True,
                verbose_name="Estimated Delivery Date",
            ),
        ),
    ]
