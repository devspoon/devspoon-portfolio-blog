## django-extensions
- pip install django-extensions
- pip install "ipython[notebook]"
- python manage.py shell_plus --notebook

> jupyter notebook 최상단에 에러 발생을 막기 위한 코드 삽입
> 에러 : SynchronousOnlyOperation: You cannot call this from an async context - use a thread or sync_to_async.
- os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"