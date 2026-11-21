from django.shortcuts import get_object_or_404, render

from core.utils import paginate

from .models import Question, Tag


def index(request):
    questions = Question.objects.new()
    page = paginate(questions, request, per_page=10)
    return render(request, 'questions/index.html', {'page': page})


def hot(request):
    questions = Question.objects.hot()
    page = paginate(questions, request, per_page=10)
    return render(request, 'questions/hot.html', {'page': page})


def tag(request, tag):
    tag_obj = get_object_or_404(Tag, name=tag)
    questions = Question.objects.by_tag(tag_obj.name)
    page = paginate(questions, request, per_page=10)
    return render(request, 'questions/tag.html', {'page': page, 'tag': tag_obj.name})


def question(request, question_id):
    question_item = get_object_or_404(
        Question.objects.select_related('author', 'author__profile'),
        pk=question_id,
    )
    answers = question_item.answers.select_related('author', 'author__profile').order_by('-created_at')
    page = paginate(answers, request, per_page=5)
    return render(request, 'questions/question.html', {'question': question_item, 'page': page})


def ask(request):
    return render(request, 'questions/ask.html')
