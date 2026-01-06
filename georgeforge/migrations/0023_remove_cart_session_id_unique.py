# Generated manually

# Standard Library
import uuid

# Django
from django.db import migrations, models


def backfill_cart_session_ids(apps, schema_editor):
    Order = apps.get_model("georgeforge", "Order")

    for order in Order.objects.filter(cart_session_id__isnull=True):
        order.cart_session_id = str(uuid.uuid4())
        order.save(update_fields=["cart_session_id"])


def reverse_backfill(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("georgeforge", "0022_add_order_cart_session_id"),
    ]

    operations = [
        migrations.RunPython(backfill_cart_session_ids, reverse_backfill),
        migrations.AlterField(
            model_name="order",
            name="cart_session_id",
            field=models.CharField(
                blank=False,
                db_index=True,
                max_length=64,
                null=False,
                verbose_name="Cart Session ID",
            ),
        ),
    ]
