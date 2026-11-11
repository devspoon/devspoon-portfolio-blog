import logging
from django.conf import settings
from django.shortcuts import render, redirect

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


# 400(Error)
def bad_request_page(request, exception=None):
    logger.debug("http 400 error")
    # render()는 별도 응답을 새로 만든다. 위에서 status_code를 세팅한 응답은
    # 버려지므로 status를 render()에 직접 넘겨야 실제 400가 나간다.
    context = {"status_code": 400}
    return render(request, "errors/error.html", context=context, status=400)


# 403(Error)
def permission_denied_page(request, exception=None):
    logger.debug("http 403 error")
    # render()는 별도 응답을 새로 만든다. 위에서 status_code를 세팅한 응답은
    # 버려지므로 status를 render()에 직접 넘겨야 실제 403가 나간다.
    context = {"status_code": 403}
    return render(request, "errors/error.html", context=context, status=403)


# 404(Error)
def page_not_found_page(request, exception=None):
    logger.debug("http 404 error")
    # render()는 별도 응답을 새로 만든다. 위에서 status_code를 세팅한 응답은
    # 버려지므로 status를 render()에 직접 넘겨야 실제 404가 나간다.
    context = {"status_code": 404}
    return render(request, "errors/error.html", context=context, status=404)


# 500(Error)
def server_error_page(request, exception=None):
    logger.debug("http 500 error")
    # render()는 별도 응답을 새로 만든다. 위에서 status_code를 세팅한 응답은
    # 버려지므로 status를 render()에 직접 넘겨야 실제 500가 나간다.
    context = {"status_code": 500}
    return render(request, "errors/error.html", context=context, status=500)


# CSRF(Error)
def csrf_failure(request, reason=""):
    logger.debug("CSRF error")
    return redirect("home:index")
