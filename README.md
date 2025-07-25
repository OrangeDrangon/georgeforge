# George Forge ![PyPI - Version](https://img.shields.io/pypi/v/allianceauth-georgeforge?style=for-the-badge&link=https%3A%2F%2Fpypi.org%2Fproject%2Fallianceauth-georgeforge)

An app for george. I guess other people can use it if they want.

## Settings

Both are optional. Forge categories has somewhat reasonable defaults (could
probably be tuned) and the webhook can be unset.

```python
# Georgeforge
FORGE_CATEGORIES = [4,6,7,8,18,20,63,66] # Item categories you wish to sell
INDUSTRY_ADMIN_WEBHOOK = "https://discord.com/api/webhooks/1/abcd" # Webhook to
post orders to
```

## Installation

```bash
python manage.py migrate
python manage.py collectstatic --no-input
python manage.py georgeforge_eveuniverse_load
```
