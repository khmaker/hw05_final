import os

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.core.cache.backends import locmem
from django.test import Client, TestCase
from django.urls import reverse
from PIL import Image

from posts.models import Follow, Group, Post

User = get_user_model()


class PostTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='JohnDoe',
                                             email='doe.j@cia.gov',
                                             password='qwe123RTY')

        self.group = Group.objects.create(slug='CIA',
                                          title='CIA',
                                          description='CIA')

    def test_new_post_unauthorized_access(self):
        """
        Неавторизованный посетитель не может опубликовать пост
        (его редиректит на страницу входа)
        """
        r = self.client.get(reverse('new_post'))
        self.assertNotEqual(r.status_code, 200)
        self.assertRedirects(r, '/auth/login/?next=/new/')

    def test_new_post_authorized_access(self):
        """
        Авторизованный посетитель имеет доступ к странице /new/
        """
        self.client.force_login(self.user)
        r = self.client.get(reverse('new_post'))
        self.assertEqual(r.status_code, 200)

    def check_text_presence_at_urls(self, message, urls):
        """
        Проверяем наличие message на страницах
        """
        cache.clear()
        for url in urls:
            r = self.client.get(url)
            self.assertContains(r, message)

    def test_post_add(self):
        """
        Авторизованный пользователь может опубликовать пост (new).
        После публикации поста новая запись появляется
        на главной странице сайта (index),
        на персональной странице пользователя (profile),
        и на отдельной странице поста (post)
        """
        self.message = 'Secret Information'
        self.client.force_login(self.user)
        self.client.post(reverse('new_post'), data={
                'group': self.group.id,
                'text': self.message,
                })
        self.post = Post.objects.get(author=self.user, text=self.message)
        urls = (reverse('index'),
                reverse('profile', kwargs={'username': self.user.username}),
                reverse('post', kwargs={
                        'username': self.user.username,
                        'post_id': self.post.id
                        }))
        self.check_text_presence_at_urls(self.message, urls)

    def test_post_edit(self):
        """
        Авторизованный пользователь может отредактировать свой пост
        и его содержимое изменится на всех связанных страницах
        """
        self.test_post_add()
        edited_message = 'Top Secret Information'
        r = self.client.post(reverse('post_edit',
                                     kwargs={
                                             'username': self.user.username,
                                             'post_id': self.post.id
                                             }),
                             {'text': edited_message}, follow=True)
        self.assertRedirects(r, reverse('post',
                                        kwargs={
                                                'username': self.user.username,
                                                'post_id': self.post.id
                                                }))
        urls = (reverse('index'),
                reverse('profile',
                        kwargs={'username': self.user.username}),
                reverse('post', kwargs={
                        'username': self.user.username,
                        'post_id': self.post.id
                        }))
        self.check_text_presence_at_urls(edited_message, urls)

    def test_post_image_presence(self):
        """
        проверяю страницу конкретной записи с картинкой:
        на странице есть тег <img> проверяю, что на главной странице,
        на странице профайла и на странице группы пост с картинкой
        отображается корректно, с тегом <img>
        """
        img = Image.new('RGB', (1, 1))
        img.save('test.jpeg', 'jpeg')
        self.test_post_add()
        with open('test.jpeg', 'rb') as image:
            self.client.post(reverse('post_edit',
                                     kwargs={
                                             'username': self.user.username,
                                             'post_id': self.post.id
                                             }),
                             data={
                                     'group': self.group.id,
                                     'text': 'image here',
                                     'image': image
                                     })
        os.remove('test.jpeg')
        urls = (reverse('index'),
                reverse('profile',
                        kwargs={'username': self.user.username}),
                reverse('post', kwargs={
                        'username': self.user.username,
                        'post_id': self.post.id
                        }),
                reverse('group_posts', kwargs={'slug': self.group.slug}))
        self.check_text_presence_at_urls('<img', urls)

    def test_file_type_protection(self):
        """
        проверка защиты от загрузки «неправильных» файлов
        """
        self.test_post_add()
        with open('test.txt', 'w') as file:
            file.write('Caramba!')
        with open('test.txt', 'rb') as text:
            r = self.client.post(
                    reverse('post_edit',
                            kwargs={
                                    'username': self.user.username,
                                    'post_id': self.post.id
                                    }
                            ),
                    data={'text': 'text here', 'image': text}
                    )
        os.remove('test.txt')
        self.assertFormError(r,
                             'form',
                             'image',
                             'Загрузите правильное изображение. '
                             'Файл, который вы загрузили, '
                             'поврежден или не является изображением.')

    def test_cache(self):
        self.test_post_add()
        self.assertTrue(locmem._caches[''])
        cache.clear()
        self.assertFalse(locmem._caches[''])

    def tearDown(self):
        Post.objects.all().delete()


class FollowTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='JohnDoe',
                                             email='doe.j@cia.gov',
                                             password='qwe123RTY')

        self.author = User.objects.create_user(username='Ping',
                                               email='pingj@cia.gov',
                                               password='qwe123RTY')

        self.pong = User.objects.create_user(username='Pong',
                                             email='Pongj@cia.gov',
                                             password='qwe123RTY')

    def test_follow(self):
        """
        Авторизованный пользователь может подписываться
        на других пользователей
        """
        self.client.force_login(self.user)
        self.assertEqual(0,
                         Follow.objects.filter(
                                 author=self.author.id).all().count())
        r = self.client.get(reverse('profile_follow',
                                    kwargs={'username': self.author.username}))
        self.assertEquals(r.status_code, 302)
        self.assertEqual(1,
                         Follow.objects.filter(
                                 author=self.author.id).all().count())

    def test_unfollow(self):
        """
        Авторизованный пользователь может удалять из подписок
        других пользователей
        """
        self.test_follow()
        r = self.client.get(reverse('profile_unfollow',
                                    kwargs={'username': self.author.username}))
        self.assertEquals(r.status_code, 302)
        self.assertEqual(0,
                         Follow.objects.filter(
                                 author=self.author.id).all().count())

    def create_post(self, message):
        self.client.force_login(self.author)
        self.client.post(reverse('new_post'), data={'text': message})

    def test_post_appearance_in_follow(self):
        """
        Новая запись пользователя появляется в ленте тех, кто на него подписан
        и не появляется в ленте тех, кто не подписан на него.
        """
        message = 'Hello, world!'

        self.client.force_login(self.pong)
        r = self.client.get(reverse('follow_index'))
        self.assertNotContains(r, message)
        self.client.force_login(self.user)
        r = self.client.get(reverse('follow_index'))
        self.assertNotContains(r, message)

        self.create_post(message)

        self.test_follow()

        r = self.client.get(reverse('follow_index'))
        self.assertContains(r, message)
        self.client.force_login(self.pong)
        r = self.client.get(reverse('follow_index'))
        self.assertNotContains(r, message)

    def test_comments_accessibility(self):
        """
        Только авторизированный пользователь может комментировать посты.
        """
        message = 'Hello, world!'
        self.create_post(message)
        self.client.force_login(self.user)
        post = Post.objects.filter(text=message).first()
        r = self.client.get(reverse('add_comment', kwargs={
                'username': post.author.username, 'post_id': post.id
                }))
        self.assertEquals(r.status_code, 200)
        self.client.logout()
        r = self.client.get(reverse('add_comment', kwargs={
                'username': post.author.username, 'post_id': post.id
                }))
        self.assertEquals(r.status_code, 302)

