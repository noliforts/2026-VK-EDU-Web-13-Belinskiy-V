from django.db import DatabaseError

from core.models import Profile
from questions.models import Tag


def sidebar(request):
    """Данные для сайдбара, он есть на каждой странице."""
    try:
        popular_tags = Tag.objects.popular()[:10]
        best_members = Profile.objects.select_related('user')[:10]
    except (DatabaseError, Exception):
        popular_tags = []
        best_members = []

    return {
        'popular_tags': popular_tags,
        'best_members': best_members,
    }
