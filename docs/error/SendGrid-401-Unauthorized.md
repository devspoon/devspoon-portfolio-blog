# Error sending email to ['[email]']: HTTP Error 401: Unauthorized

**Issue ID:** 7290693077
**Short ID:** PYTHON-DJANGO-7C
**Project:** python-django
**Date:** Jul 12, 2026 11:28:05 AM UTC

## Tags

- **environment:** production
- **interface_type:** contexts
- **level:** error
- **logger:** utils.email.async_send_email
- **runtime:** CPython 3.12.4
- **runtime.name:** CPython
- **server_name:** 41ebdf1bd311

## Breadcrumbs

- **log** `gunicorn.access` [info]
  172.18.0.6 - - [12/Jul/2026:09:22:59 +0000] "GET /site/phpinfo.php HTTP/1.0" 200 31507 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
- **log** `gunicorn.access` [info]
  172.18.0.6 - - [12/Jul/2026:09:22:59 +0000] "GET /wp-admin/phpinfo.php HTTP/1.0" 200 31507 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
- **log** `gunicorn.access` [info]
  172.18.0.6 - - [12/Jul/2026:09:23:00 +0000] "GET /includes/phpinfo.php HTTP/1.0" 200 31507 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
- **log** `gunicorn.access` [info]
  172.18.0.6 - - [12/Jul/2026:10:30:24 +0000] "GET /search/queryset/?tag=e-commerce HTTP/1.0" 200 35744 "-" "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
- **log** `gunicorn.access` [info]
  172.18.0.6 - - [12/Jul/2026:10:51:29 +0000] "GET /blog/opensource/detail/4/5 HTTP/1.0" 200 31507 "-" "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
- **log** `gunicorn.access` [info]
  172.18.0.6 - - [12/Jul/2026:11:02:42 +0000] "GET /blog/opensource/detail/4/3 HTTP/1.0" 200 31507 "-" "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.0.3 Mobile/15E148 Safari/604.1"
