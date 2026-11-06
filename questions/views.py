from django.http import Http404
from django.shortcuts import render

from core.utils import paginate

from .mock import ANSWERS, QUESTIONS


def index(request):
    page = paginate(QUESTIONS, request, per_page=5)
    return render(request, 'questions/index.html', {'page': page})


def hot(request):
    hot_questions = sorted(QUESTIONS, key=lambda q: q['rating'], reverse=True)
    page = paginate(hot_questions, request, per_page=5)
    return render(request, 'questions/hot.html', {'page': page})


def tag(request, tag):
    tag_questions = [q for q in QUESTIONS if tag in q['tags']]
    page = paginate(tag_questions, request, per_page=5)
    return render(request, 'questions/tag.html', {'page': page, 'tag': tag})


def question(request, question_id):
    if not 1 <= question_id <= len(QUESTIONS):
        raise Http404
    question = QUESTIONS[question_id - 1]
    page = paginate(ANSWERS, request, per_page=3)
    return render(request, 'questions/question.html', {'question': question, 'page': page})


def ask(request):
    return render(request, 'questions/ask.html')
