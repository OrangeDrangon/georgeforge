"""Hook into Alliance Auth"""

# Django
from allianceauth import hooks
from allianceauth.services.hooks import MenuItemHook
from allianceauth.services.hooks import UrlHook
from django.utils.translation import gettext_lazy as _

from georgeforge import urls

# Alliance Auth
# George Forge


class GeorgeForgeMenuItem(MenuItemHook):
    """This class ensures only authorized users will see the menu entry"""

    def __init__(self):
        # setup menu entry for sidebar
        MenuItemHook.__init__(
            self,
            _("George Forge"),
            "fas fa-cube fa-fw",
            "georgeforge:store",
            navactive=["georgeforge:"],
        )

    def render(self, request):
        """Render the menu item

        :param request:

        """

        if request.user.has_perm("georgeforge.place_order"):
            return MenuItemHook.render(self, request)

        return ""


@hooks.register("menu_item_hook")
def register_menu():
    """Register the menu item"""

    return GeorgeForgeMenuItem()


@hooks.register("url_hook")
def register_urls():
    """Register app urls"""

    return UrlHook(urls, "georgeforge", r"^georgeforge/")
