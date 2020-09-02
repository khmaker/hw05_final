from django.contrib.auth import get_user_model
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver

User = get_user_model()


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста',
                            help_text='Напишите что-нибудь содержательное')
    pub_date = models.DateTimeField(auto_now_add=True,
                                    verbose_name='Дата публикации',
                                    db_index=True
                                    )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='posts',
                               verbose_name='Автор поста',
                               )
    group = models.ForeignKey('Group',
                              on_delete=models.SET_NULL,
                              blank=True,
                              null=True,
                              related_name='posts',
                              verbose_name='Группа',
                              help_text='Здесь можно выбрать группу',
                              )
    image = models.ImageField(upload_to='posts/',
                              blank=True,
                              null=True,
                              help_text='Здесь можно загрузить картинку',
                              verbose_name='Картинка', )

    class Meta:
        ordering = ('-pub_date',)


@receiver(post_delete, sender=Post)
def submission_delete(sender, instance, **kwargs):
    instance.image.delete(False)


class Group(models.Model):
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(null=False, unique=True)
    description = models.TextField(verbose_name='Описание группы')

    def __str__(self):
        return self.title


class Comment(models.Model):
    created = models.DateTimeField(auto_now_add=True,
                                   verbose_name='Дата публикации',
                                   db_index=True
                                   )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='comments',
                               verbose_name='Автор комментария',
                               )
    post = models.ForeignKey(Post,
                             on_delete=models.CASCADE,
                             related_name='comments',
                             blank=True,
                             help_text='Здесь можно оставить комментарий',
                             verbose_name='Комментарий')
    text = models.TextField(blank=True,
                            verbose_name='Текст комментария',
                            help_text='Напишите что-нибудь содержательное')

    class Meta:
        ordering = ('-created',)


class Follow(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE,
                             related_name='follower',
                             verbose_name='Подписчик',
                             )
    author = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='following',
                               verbose_name='Подписки',
                               )

    class Meta:
        unique_together = ['user', 'author']
