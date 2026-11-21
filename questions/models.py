from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse


class TagManager(models.Manager):
    def popular(self):
        return self.annotate(num_questions=models.Count('questions')).order_by('-num_questions')


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True, db_index=True, verbose_name='Название тега')

    objects = TagManager()

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class QuestionManager(models.Manager):
    def get_base_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related('author', 'author__profile')
            .prefetch_related('tags')
            .annotate(annotated_answers_count=models.Count('answers', distinct=True))
        )

    def new(self):
        return self.get_base_queryset().order_by('-created_at')

    def hot(self):
        return self.get_base_queryset().order_by('-rating', '-created_at')

    def by_tag(self, tag_name):
        return self.get_base_queryset().filter(tags__name=tag_name).order_by('-created_at')


class Question(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name='Автор',
    )
    title = models.CharField(max_length=255, verbose_name='Заголовок')
    text = models.TextField(verbose_name='Текст вопроса')
    tags = models.ManyToManyField(Tag, related_name='questions', blank=True, verbose_name='Теги')
    rating = models.IntegerField(default=0, db_index=True, verbose_name='Рейтинг')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    objects = QuestionManager()

    class Meta:
        verbose_name = 'Вопрос'
        verbose_name_plural = 'Вопросы'
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('question', kwargs={'question_id': self.pk})

    @property
    def date(self):
        return self.created_at.strftime('%d-%b-%y %H:%M')

    @property
    def answers_count(self):
        if hasattr(self, 'annotated_answers_count'):
            return self.annotated_answers_count
        return self.answers.count()

    @property
    def vote(self):
        return ''


class Answer(models.Model):
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Вопрос',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='answers',
        verbose_name='Автор',
    )
    text = models.TextField(verbose_name='Текст ответа')
    is_correct = models.BooleanField(default=False, verbose_name='Правильный ответ')
    rating = models.IntegerField(default=0, db_index=True, verbose_name='Рейтинг')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Ответ'
        verbose_name_plural = 'Ответы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Ответ к "{self.question.title[:30]}" от {self.author.username}'

    @property
    def date(self):
        return self.created_at.strftime('%d-%b-%y %H:%M')

    @property
    def correct(self):
        return self.is_correct

    @property
    def vote(self):
        return ''


class QuestionLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='question_likes',
        verbose_name='Пользователь',
    )
    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Вопрос',
    )
    value = models.SmallIntegerField(default=1, verbose_name='Значение (+1/-1)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата оценки')

    class Meta:
        verbose_name = 'Оценка вопроса'
        verbose_name_plural = 'Оценки вопросов'
        unique_together = ('user', 'question')

    def __str__(self):
        return f'{self.user.username} -> вопрос #{self.question_id}: {self.value}'


class AnswerLike(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='answer_likes',
        verbose_name='Пользователь',
    )
    answer = models.ForeignKey(
        Answer,
        on_delete=models.CASCADE,
        related_name='likes',
        verbose_name='Ответ',
    )
    value = models.SmallIntegerField(default=1, verbose_name='Значение (+1/-1)')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата оценки')

    class Meta:
        verbose_name = 'Оценка ответа'
        verbose_name_plural = 'Оценки ответов'
        unique_together = ('user', 'answer')

    def __str__(self):
        return f'{self.user.username} -> ответ #{self.answer_id}: {self.value}'
