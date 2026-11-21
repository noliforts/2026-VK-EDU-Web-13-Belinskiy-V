from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('hot/', views.hot, name='hot'),
    path('tag/<str:tag>/', views.tag, name='tag'),
    path('question/<int:question_id>/', views.question, name='question'),
    path('ask/', views.ask, name='ask'),
    path('question/<int:question_id>/vote/', views.vote_question, name='vote_question'),
    path('answer/<int:answer_id>/vote/', views.vote_answer, name='vote_answer'),
    path('question/<int:question_id>/correct_answer/', views.mark_correct_answer, name='mark_correct_answer'),
]
