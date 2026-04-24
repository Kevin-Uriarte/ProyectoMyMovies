from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class RegisterViewTests(TestCase):
    def test_register_creates_user_and_logs_in(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'nuevo_usuario',
                'password': 'PasswordSeguro123!',
                'password_confirmation': 'PasswordSeguro123!',
            }
        )

        self.assertRedirects(response, reverse('index'), fetch_redirect_response=False)
        self.assertTrue(User.objects.filter(username='nuevo_usuario').exists())

        self.assertEqual(int(self.client.session['_auth_user_id']), User.objects.get(username='nuevo_usuario').id)

    def test_register_rejects_existing_username(self):
        User.objects.create_user(username='repetido', password='PasswordSeguro123!')

        response = self.client.post(
            reverse('register'),
            {
                'username': 'repetido',
                'password': 'PasswordSeguro123!',
                'password_confirmation': 'PasswordSeguro123!',
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Ese nombre de usuario ya está registrado.')
        self.assertEqual(User.objects.filter(username='repetido').count(), 1)

    def test_register_rejects_password_mismatch(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'otro_usuario',
                'password': 'PasswordSeguro123!',
                'password_confirmation': 'PasswordDistinto123!',
            }
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Las contraseñas no coinciden.')
        self.assertFalse(User.objects.filter(username='otro_usuario').exists())
