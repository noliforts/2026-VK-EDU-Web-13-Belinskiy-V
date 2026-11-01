from django.shortcuts import render


def index(request):
    return render(request, 'index.html', {'is_auth': True})


def question(request, question_id):
    return render(request, 'question.html', {'is_auth': True})


def ask(request):
    return render(request, 'ask.html', {'is_auth': True})


def profile(request):
    return render(request, 'profile.html', {'is_auth': True})


def login(request):
    return render(request, 'login.html')


def signup(request):
    return render(request, 'signup.html')


def rules(request):
    return render(request, 'rules.html')


def help(request):
    return render(request, 'help.html')
