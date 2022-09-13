from hr_backend.settings import REST_FRAMEWORK


def default_pagination(request):
    """
    This function is created for validate limit and offset.
    """
    offset = request.GET.get("page")
    limit = request.GET.get("size")
    if offset is None:
        offset = 1
    if limit is None:
        limit = REST_FRAMEWORK.get("PAGE_SIZE")
    offset = (int(offset) - 1) * int(limit)
    limit = int(offset) + int(limit)
    return limit, offset
