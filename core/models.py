from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name='Пользователь',
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        default='core/img/avatar.png',
        blank=True,
        verbose_name='Аватар',
    )
    rank = models.CharField(
        max_length=50,
        default='прохожий',
        blank=True,
        verbose_name='Ранг в курилке',
    )

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return f'{self.user.username} ({self.rank})'

    @property
    def name(self):
        return self.user.username


# Для прозрачной совместимости с существующими шаблонами (author.name / author.rank)
User.add_to_class('name', property(lambda u: u.username))
User.add_to_class('rank', property(lambda u: u.profile.rank if hasattr(u, 'profile') else 'прохожий'))


@receiver(post_save, sender=User)
def create_or_save_user_profile(sender, instance, created, **kwargs):
    if created and not hasattr(instance, 'profile'):
        Profile.objects.create(user=instance)
