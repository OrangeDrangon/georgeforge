"""
George Forge Test
"""

# Django
from django.test import TestCase


class TestGeorgeForge(TestCase):
    """
    TestGeorgeForge
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Test setup
        :return:
        :rtype:
        """

        super().setUpClass()

    def test_example(self):
        """
        Dummy test function
        :return:
        :rtype:
        """

        self.assertEqual(True, True)
