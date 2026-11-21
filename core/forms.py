import os

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

ALLOWED_AVATAR_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.webp', '.gif']
MAX_AVATAR_SIZE = 2 * 1024 * 1024  # 2 МБ


def validate_avatar_file(avatar):
    if not avatar:
        return avatar
    ext = os.path.splitext(avatar.name)[1].lower()
    if ext not in ALLOWED_AVATAR_EXTENSIONS:
        raise ValidationError(
            f'Недопустимый формат файла. Разрешены только: {", ".join(ALLOWED_AVATAR_EXTENSIONS)}.'
        )
    if avatar.size > MAX_AVATAR_SIZE:
        raise ValidationError('Размер файла не должен превышать 2 МБ.')
    return avatar


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Логин',
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Введите ваш логин'}),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'input'}),
    )

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                raise ValidationError('Неверный логин или пароль!')
            if not self.user_cache.is_active:
                raise ValidationError('Данный аккаунт заблокирован.')
        return cleaned_data

    def get_user(self):
        return self.user_cache


class SignupForm(forms.ModelForm):
    nickname = forms.CharField(
        label='Никнейм',
        required=False,
        widget=forms.TextInput(attrs={'class': 'input', 'placeholder': 'Иван Иванов'}),
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={'class': 'input'}),
    )
    password2 = forms.CharField(
        label='Повторите пароль',
        widget=forms.PasswordInput(attrs={'class': 'input'}),
    )
    avatar = forms.ImageField(
        label='Аватар',
        required=False,
        widget=forms.FileInput(attrs={'class': 'input'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'input', 'placeholder': 'ivanov'}),
            'email': forms.EmailInput(attrs={'class': 'input', 'placeholder': 'ivanov@mail.ru'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Пользователь с таким логином уже существует.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('Email обязателен для заполнения.')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Этот email уже занят.')
        return email

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        return validate_avatar_file(avatar)

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password2')

        if p1 and p2:
            if p1 != p2:
                self.add_error('password2', 'Пароли не совпадают.')
            else:
                user_instance = User(
                    username=cleaned_data.get('username', ''),
                    email=cleaned_data.get('email', ''),
                )
                validate_password(p1, user=user_instance)

        return cleaned_data

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
        )
        profile = user.profile
        if self.cleaned_data.get('nickname'):
            profile.rank = self.cleaned_data['nickname']
        if self.cleaned_data.get('avatar'):
            profile.avatar = self.cleaned_data['avatar']
        profile.save()
        return user


class ProfileEditForm(forms.ModelForm):
    nickname = forms.CharField(
        label='Никнейм',
        required=False,
        widget=forms.TextInput(attrs={'class': 'input'}),
    )
    avatar = forms.ImageField(
        label='Аватар',
        required=False,
        widget=forms.FileInput(attrs={'class': 'input'}),
    )

    class Meta:
        model = User
        fields = ('email',)
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'profile'):
            self.fields['nickname'].initial = self.instance.profile.rank

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError('Email обязателен для заполнения.')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Этот email уже занят другим пользователем.')
        return email

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        return validate_avatar_file(avatar)

    def save(self, commit=True):
        user = super().save(commit=commit)
        profile = user.profile
        if 'nickname' in self.cleaned_data:
            profile.rank = self.cleaned_data['nickname']
        if self.cleaned_data.get('avatar'):
            profile.avatar = self.cleaned_data['avatar']
        profile.save()
        return user
