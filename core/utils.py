from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator


def paginate(objects_list, request, per_page=10):
    paginator = Paginator(objects_list, per_page)
    try:
        return paginator.page(request.GET.get('page'))
    except (PageNotAnInteger, EmptyPage):
        # мусор в параметре или страница за пределами: показываем первую
        return paginator.page(1)
