from django.contrib.auth.decorators import login_required
from django.db import models
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from core.utils import paginate

from .forms import AnswerForm, QuestionForm
from .models import Answer, AnswerLike, Question, QuestionLike, Tag


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

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f'/login/?next=/question/{question_id}/')
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            ans = answer_form.save(question=question_item, author=request.user)
            # Расчет страницы, на которую попал новый ответ
            per_page = 5
            total_answers = question_item.answers.count()
            target_page = max(1, (total_answers + per_page - 1) // per_page)
            return redirect(f'{question_item.get_absolute_url()}?page={target_page}#answer-{ans.id}')
    else:
        answer_form = AnswerForm()

    answers = question_item.answers.select_related('author', 'author__profile').order_by('created_at')
    page = paginate(answers, request, per_page=5)
    return render(
        request,
        'questions/question.html',
        {'question': question_item, 'page': page, 'form': answer_form},
    )


@login_required
def ask(request):
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            q = form.save(author=request.user)
            return redirect(q.get_absolute_url())
    else:
        form = QuestionForm()

    return render(request, 'questions/ask.html', {'form': form})


# --- AJAX эндпоинты ---

@require_POST
def vote_question(request, question_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Необходима авторизация'}, status=401)

    question_item = get_object_or_404(Question, pk=question_id)
    vote_type = request.POST.get('type')
    if vote_type not in ['like', 'dislike', 'up', 'down']:
        return JsonResponse({'error': 'Неверный тип голоса'}, status=400)

    val = 1 if vote_type in ['like', 'up'] else -1
    like, created = QuestionLike.objects.get_or_create(
        user=request.user,
        question=question_item,
        defaults={'value': val},
    )
    if not created:
        if like.value == val:
            like.delete()
        else:
            like.value = val
            like.save()

    total = QuestionLike.objects.filter(question=question_item).aggregate(s=models.Sum('value'))['s'] or 0
    question_item.rating = total
    question_item.save(update_fields=['rating'])

    return JsonResponse({'status': 'ok', 'new_rating': question_item.rating})


@require_POST
def vote_answer(request, answer_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Необходима авторизация'}, status=401)

    answer_item = get_object_or_404(Answer, pk=answer_id)
    vote_type = request.POST.get('type')
    if vote_type not in ['like', 'dislike', 'up', 'down']:
        return JsonResponse({'error': 'Неверный тип голоса'}, status=400)

    val = 1 if vote_type in ['like', 'up'] else -1
    like, created = AnswerLike.objects.get_or_create(
        user=request.user,
        answer=answer_item,
        defaults={'value': val},
    )
    if not created:
        if like.value == val:
            like.delete()
        else:
            like.value = val
            like.save()

    total = AnswerLike.objects.filter(answer=answer_item).aggregate(s=models.Sum('value'))['s'] or 0
    answer_item.rating = total
    answer_item.save(update_fields=['rating'])

    return JsonResponse({'status': 'ok', 'new_rating': answer_item.rating})


@require_POST
def mark_correct_answer(request, question_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Необходима авторизация'}, status=401)

    question_item = get_object_or_404(Question, pk=question_id)
    if request.user != question_item.author:
        return JsonResponse({'error': 'Только автор вопроса может выбирать правильный ответ'}, status=403)

    answer_id = request.POST.get('answer_id')
    answer_item = get_object_or_404(Answer, pk=answer_id, question=question_item)

    if answer_item.is_correct:
        answer_item.is_correct = False
        answer_item.save(update_fields=['is_correct'])
    else:
        question_item.answers.filter(is_correct=True).update(is_correct=False)
        answer_item.is_correct = True
        answer_item.save(update_fields=['is_correct'])

    return JsonResponse({'status': 'ok', 'is_correct': answer_item.is_correct})
