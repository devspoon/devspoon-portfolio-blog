import logging
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import render, redirect

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


# 400(Error)
def bad_request_page(request, exception=None):
    logger.debug("http 400 error")
    response = HttpResponse()
    response.status_code = 400  # Or any other HTTP status code
    context = {"status_code": response.status_code}
    return render(request, "errors/error.html", context=context)


# 403(Error)
def permission_denied_page(request, exception=None):
    logger.debug("http 403 error")
    response = HttpResponse()
    response.status_code = 403  # Or any other HTTP status code
    context = {"status_code": response.status_code}
    return render(request, "errors/error.html", context=context)


# 404(Error)
def page_not_found_page(request, exception=None):
    logger.debug("http 404 error")
    response = HttpResponse()
    response.status_code = 404  # Or any other HTTP status code
    context = {"status_code": response.status_code}
    return render(request, "errors/error.html", context=context)


# 500(Error)
def server_error_page(request, exception=None):
    logger.debug("http 500 error")
    response = HttpResponse()
    response.status_code = 500  # Or any other HTTP status code
    context = {"status_code": response.status_code}
    return render(request, "errors/error.html", context=context)


# CSRF(Error)
def csrf_failure(request, exception=None):
    logger.debug("CSRF error")
    return redirect("home:index")
