from .mock import MEMBERS, TAGS


def sidebar(request):
    """Данные для сайдбара, он есть на каждой странице."""
    return {'popular_tags': TAGS, 'best_members': MEMBERS}
