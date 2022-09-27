from mbook_backend.settings import REST_FRAMEWORK


def custom_pagination(request):
    offset = request.GET.get("page")
    limit = request.GET.get("size")
    if offset is None:
        offset = 1
    if limit is None:
        limit = REST_FRAMEWORK.get("PAGE_SIZE")
    offset = (int(offset) - 1) * int(limit)
    limit = int(offset) + int(limit)
    return limit, offset
