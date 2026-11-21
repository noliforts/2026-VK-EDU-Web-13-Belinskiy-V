from django.contrib import admin

from .models import Answer, AnswerLike, Question, QuestionLike, Tag


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0
    raw_id_fields = ('author',)
    fields = ('author', 'text', 'is_correct', 'rating')


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    inlines = (AnswerInline,)
    list_display = ('title', 'author', 'rating', 'created_at')
    search_fields = ('title', 'text', 'author__username')
    list_filter = ('created_at',)
    raw_id_fields = ('author',)
    list_select_related = ('author',)
    filter_horizontal = ('tags',)


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'author', 'question', 'is_correct', 'rating', 'created_at')
    search_fields = ('text', 'author__username', 'question__title')
    list_filter = ('is_correct', 'created_at')
    raw_id_fields = ('author', 'question')
    list_select_related = ('author', 'question')


@admin.register(QuestionLike)
class QuestionLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'question', 'value', 'created_at')
    search_fields = ('user__username', 'question__title')
    list_filter = ('value', 'created_at')
    raw_id_fields = ('user', 'question')
    list_select_related = ('user', 'question')


@admin.register(AnswerLike)
class AnswerLikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'answer', 'value', 'created_at')
    search_fields = ('user__username',)
    list_filter = ('value', 'created_at')
    raw_id_fields = ('user', 'answer')
    list_select_related = ('user', 'answer')
