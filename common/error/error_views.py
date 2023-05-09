from django.http import HttpResponse
from django.shortcuts import render


# 400(Error)
def bad_request_page(request, exception=None):
    response = HttpResponse()
    response.status_code = 400  # Or any other HTTP status code
    context = {"status_code": response.status_code}
    return render(request, "errors/error.html", context=context)


# 404(Error)
def page_not_found_page(request, exception=None):
    response = HttpResponse()
    response.status_code = 404  # Or any other HTTP status code
    context = {"status_code": response.status_code}
    return render(request, "errors/error.html", context=context)


# 500(Error)
def server_error_page(request, exception=None):
    response = HttpResponse()
    response.status_code = 500  # Or any other HTTP status code
    context = {"status_code": response.status_code}
    return render(request, "errors/error.html", context=context)
