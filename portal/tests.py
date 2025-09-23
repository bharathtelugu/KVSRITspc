from django.test import TestCase, Client
from django.urls import reverse

class LoginPageTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')

    def test_login_page_loads_correctly(self):
        """Test that the login page loads with a 200 status code"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)

    def test_login_page_uses_correct_template(self):
        """Test that the login page uses the correct template"""
        response = self.client.get(self.login_url)
        self.assertTemplateUsed(response, 'portal/login.html')
        self.assertTemplateUsed(response, 'portal/base.html')

    def test_login_page_content(self):
        """Test that the login page contains the expected content"""
        response = self.client.get(self.login_url)
        self.assertContains(response, 'Login to Your Account')
        self.assertContains(response, '<form method="POST"')
        self.assertContains(response, 'csrfmiddlewaretoken')
        self.assertContains(response, 'type="submit"')