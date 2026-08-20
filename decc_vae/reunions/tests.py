from django.test import TestCase


class SmokeTest(TestCase):
    def test_login_page(self):
        response = self.client.get("/login/")
        self.assertEqual(response.status_code, 200)
