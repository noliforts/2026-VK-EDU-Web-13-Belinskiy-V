from django.shortcuts import render


def index(request):
    return render(request, 'index.html')


def question(request, question_id):
    return render(request, 'question.html')


def ask(request):
    return render(request, 'ask.html')


def profile(request):
    return render(request, 'profile.html')


def login(request):
    return render(request, 'login.html')


def signup(request):
    return render(request, 'signup.html')


def rules(request):
    return render(request, 'rules.html')


def help(request):
    return render(request, 'help.html')
