import logging
from django.conf import settings
from django.shortcuts import render, redirect

logger = logging.getLogger(getattr(settings, "BLOG_LOGGER", "django"))


# 400(Error)
def bad_request_page(request, exception=None):
    logger.debug("http 400 error")
    return render(request, "errors/error.html", {"status_code": 400}, status=400)


# 403(Error)
def permission_denied_page(request, exception=None):
    logger.debug("http 403 error")
    return render(request, "errors/error.html", {"status_code": 403}, status=403)


# 404(Error)
def page_not_found_page(request, exception=None):
    logger.debug("http 404 error")
    return render(request, "errors/error.html", {"status_code": 404}, status=404)


# 500(Error)
def server_error_page(request, exception=None):
    logger.debug("http 500 error")
    return render(request, "errors/error.html", {"status_code": 500}, status=500)


# CSRF(Error)
def csrf_failure(request, reason=""):
    logger.debug("CSRF error")
    return redirect("home:index")
