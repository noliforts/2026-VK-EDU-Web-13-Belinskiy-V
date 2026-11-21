from django import forms
from django.core.exceptions import ValidationError

from .models import Answer, Question, Tag


class QuestionForm(forms.ModelForm):
    tags = forms.CharField(
        label='Теги',
        required=False,
        widget=forms.TextInput(
            attrs={'class': 'input', 'placeholder': 'табак, зажигалки, курилка'}
        ),
        help_text='Теги через запятую, не больше 5.',
    )

    class Meta:
        model = Question
        fields = ('title', 'text')
        widgets = {
            'title': forms.TextInput(attrs={'class': 'input', 'placeholder': 'Как это сделать?'}),
            'text': forms.Textarea(attrs={'class': 'input', 'rows': 10, 'placeholder': 'Опишите проблему подробно.'}),
        }

    def clean_tags(self):
        raw_tags = self.cleaned_data.get('tags', '')
        tag_names = [t.strip().lower() for t in raw_tags.split(',') if t.strip()]
        if len(tag_names) > 5:
            raise ValidationError('Не больше 5 тегов.')
        return tag_names

    def save(self, author=None, commit=True):
        question = super().save(commit=False)
        if author:
            question.author = author
        if commit:
            question.save()
            tag_names = self.cleaned_data.get('tags', [])
            tag_objs = []
            for name in tag_names:
                tag, _ = Tag.objects.get_or_create(name=name)
                tag_objs.append(tag)
            question.tags.set(tag_objs)
        return question


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ('text',)
        widgets = {
            'text': forms.Textarea(attrs={'class': 'input', 'rows': 5, 'placeholder': 'Введите ваш ответ'}),
        }

    def clean_text(self):
        text = self.cleaned_data.get('text', '').strip()
        if len(text) < 5:
            raise ValidationError('Ответ должен содержать не менее 5 символов.')
        return text

    def save(self, question, author, commit=True):
        answer = super().save(commit=False)
        answer.question = question
        answer.author = author
        if commit:
            answer.save()
        return answer
