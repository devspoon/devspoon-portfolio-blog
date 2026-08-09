# ConnectionMethodStats.MultipleObjectsReturned: get() returned more than one ConnectionMethodStats -- it returned 2!

**Issue ID:** 7563408362
**Short ID:** PYTHON-DJANGO-7G
**Project:** python-django
**Date:** Aug 5, 2026 11:37:09 PM UTC

## Tags

- **browser:** ClaudeBot 1.0
- **browser.name:** ClaudeBot
- **device:** Desktop
- **device.family:** Spider
- **environment:** production
- **handled:** no
- **interface_type:** exception
- **level:** error
- **mechanism:** django
- **runtime:** CPython 3.12.4
- **runtime.name:** CPython
- **server_name:** 41ebdf1bd311
- **transaction:** /bbs/board.php
- **url:** http://devspoon.com/bbs/board.php
- **user:** ip:216.73.216.125

## Exception

### Exception 1
**Type:** ConnectionMethodStats.MultipleObjectsReturned
**Handled:** No
**Value:** get() returned more than one ConnectionMethodStats -- it returned 2!

#### Stacktrace

```
 get in django/db/models/query.py [Line 640] (Not in app)
            return clone._result_cache[0]
        if not num:
            raise self.model.DoesNotExist(
                "%s matching query does not exist." % self.model._meta.object_name
            )
        raise self.model.MultipleObjectsReturned(  <-- SUSPECT LINE
            "get() returned more than one %s -- it returned %s!"
            % (
                self.model._meta.object_name,
                num if not limit or num < limit else "more than %s" % (limit - 1),
            )
---
Variable values:
{
  "args": [],
  "clone": "<QuerySet [<ConnectionMethodStats: ConnectionMethodStats object (717)>, <ConnectionMethodStats: ConnectionMethodStats object (716)>]>",
  "kwargs": {
    "created_at__date": "datetime.date(2026, 8, 5)"
  },
  "limit": "21",
  "num": "2",
  "self": "<QuerySet from django.db.models.query at 0x713d16841490>"
}

=======
 get_or_create in django/db/models/query.py [Line 916] (Not in app)
        """
        # The get() needs to be targeted at the write database in order
        # to avoid potential transaction consistency problems.
        self._for_write = True
        try:
            return self.get(**kwargs), False  <-- SUSPECT LINE
        except self.model.DoesNotExist:
            params = self._extract_model_params(defaults, **kwargs)
            # Try to create an object using passed params.
            try:
                with transaction.atomic(using=self.db):
---
Variable values:
{
  "defaults": "None",
  "kwargs": {
    "created_at__date": "datetime.date(2026, 8, 5)"
  },
  "self": "<QuerySet from django.db.models.query at 0x713d16841490>"
}

=======
 stats in custom_middlewares/middlewares/statistics.py [Line 24] (In app)
        with transaction.atomic():
            # 오늘 날짜의 통계 가져오기 (잠금)
            (
                stats,
                created,
            ) = ConnectionMethodStats.objects.select_for_update().get_or_create(  <-- SUSPECT LINE
                created_at__date=today
            )

            # 운영체제에 따라 카운트 업데이트
            if "Windows" in os_info:
---
Variable values:
{
  "os_info": "'Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko; compatible; ClaudeBot/1.0; +claudebot@anthropic.com)'",
  "self": "<custom_middlewares.middlewares.statistics.ConnectionMethodStatsMiddleware object at 0x713d1d18bd40>",
  "today": "datetime.date(2026, 8, 5)"
}

=======
 __call__ in custom_middlewares/middlewares/statistics.py [Line 45] (In app)
            stats.save()  # 변경 사항 저장

    def __call__(self, request):
        if "HTTP_USER_AGENT" in request.META:
            if "admin" not in request.path:
                self.stats(request.META["HTTP_USER_AGENT"])  <-- SUSPECT LINE

        response = self.get_response(request)

        return response

---
Variable values:
{
  "request": "<WSGIRequest: GET '/bbs/board.php?bo_table=free&wr_id=1718'>",
  "self": "<custom_middlewares.middlewares.statistics.ConnectionMethodStatsMiddleware object at 0x713d1d18bd40>"
}

=======
 inner in django/core/handlers/exception.py [Line 55] (Not in app)
    else:

        @wraps(get_response)
        def inner(request):
            try:
                response = get_response(request)  <-- SUSPECT LINE
            except Exception as exc:
                response = response_for_exception(request, exc)
            return response

        return inner
---
Variable values:
{
  "exc": "MultipleObjectsReturned('get() returned more than one ConnectionMethodStats -- it returned 2!')",
  "get_response": "<custom_middlewares.middlewares.statistics.ConnectionMethodStatsMiddleware object at 0x713d1d18bcb0>",
  "request": "<WSGIRequest: GET '/bbs/board.php?bo_table=free&wr_id=1718'>"
}

=======
```

## Breadcrumbs

- **default** `query` [info]
  SELECT connection_method_stats.id, connection_method_stats.win, connection_method_stats.mac,
         connection_method_stats.iph, connection_method_stats.android, connection_method_stats.oth,
         connection_method_stats.created_at
  FROM connection_method_stats
  WHERE (connection_method_stats.created_at AT TIME ZONE %s)::date = %s
  LIMIT 21
  FOR
  UPDATE

## Request

GET http://devspoon.com/bbs/board.php
