from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='JohnDoe',
                                             email='doe.j@cia.gov',
                                             password='qwe123RTY')
        self.client.force_login(self.user)

    def test_user_presence_in_db(self):
        self.assertIn(self.user, User.objects.all())

    def test_user_profile(self):
        """
        После регистрации пользователя создается
        его персональная страница (profile)
        """
        r = self.client.get(reverse('profile',
                                    kwargs={'username': self.user.username}))
        self.assertEqual(r.status_code, 200)
        self.assertIsInstance(r.context['author'], User)
        self.assertEqual(r.context['author'], self.user)

    def test_404(self):
        """
        Возвращает ли сервер код 404, если страница не найдена.
        """
        username = self.user.username
        r = self.client.get(reverse('profile',
                                    kwargs={'username': username}))
        self.assertEqual(r.status_code, 200)
        self.user.delete()
        r = self.client.get(reverse('profile',
                                    kwargs={'username': username}))
        self.assertEqual(r.status_code, 404)

    def tearDown(self):
        self.client.logout()
