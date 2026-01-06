# Generated manually

# Django
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("georgeforge", "0021_alter_order_deliverysystem"),
    ]

    operations = [
        migrations.AddField(
            model_name="order",
            name="cart_session_id",
            field=models.CharField(
                blank=True,
                db_index=True,
                max_length=64,
                null=True,
                unique=True,
                verbose_name="Cart Session ID",
            ),
        ),
    ]
