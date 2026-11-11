# ConnectionHardwareStats.MultipleObjectsReturned: get() returned more than one ConnectionHardwareStats -- it returned 2!

**Issue ID:** 7563908033
**Short ID:** PYTHON-DJANGO-7H
**Project:** python-django
**Date:** Aug 5, 2026 11:32:04 PM UTC

## Tags

- **environment:** production
- **handled:** no
- **interface_type:** exception
- **level:** error
- **mechanism:** django
- **runtime:** CPython 3.12.4
- **runtime.name:** CPython
- **server_name:** 41ebdf1bd311
- **transaction:** /wp.php
- **url:** http://devspoon.com/wp.php
- **user:** ip:20.100.178.111

## Exception

### Exception 1
**Type:** ConnectionHardwareStats.MultipleObjectsReturned
**Handled:** No
**Value:** get() returned more than one ConnectionHardwareStats -- it returned 2!

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
  "clone": "<QuerySet [<ConnectionHardwareStats: ConnectionHardwareStats object (8971)>, <ConnectionHardwareStats: ConnectionHardwareStats object (8972)>]>",
  "kwargs": {
    "created_at__date": "datetime.date(2026, 8, 5)"
  },
  "limit": "21",
  "num": "2",
  "self": "<QuerySet from django.db.models.query at 0x713d16962900>"
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
  "self": "<QuerySet from django.db.models.query at 0x713d16962900>"
}

=======
 __call__ in custom_middlewares/middlewares/statistics.py [Line 64] (In app)
                today = timezone.now().date()
                # 오늘 날짜의 통계 가져오기
                (
                    stats,
                    created,
                ) = ConnectionHardwareStats.objects.select_for_update().get_or_create(  <-- SUSPECT LINE
                    created_at__date=today
                )
                # 사용자 에이전트에 따라 카운트 업데이트
                if request.user_agent.is_mobile:
                    stats.mobile = F("mobile") + 1
---
Variable values:
{
  "request": "<WSGIRequest: GET '/wp.php'>",
  "self": "<custom_middlewares.middlewares.statistics.ConnectionHardwareStatsMiddleware object at 0x713d1d18ba10>",
  "today": "datetime.date(2026, 8, 5)"
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
  "exc": "MultipleObjectsReturned('get() returned more than one ConnectionHardwareStats -- it returned 2!')",
  "get_response": "<custom_middlewares.middlewares.statistics.ConnectionHardwareStatsMiddleware object at 0x713d1d18b980>",
  "request": "<WSGIRequest: GET '/wp.php'>"
}

=======
```

## Breadcrumbs

- **default** `query` [info]
  SELECT connection_hardware_stats.id, connection_hardware_stats.mobile,
         connection_hardware_stats.tablet, connection_hardware_stats.pc, connection_hardware_stats.bot,
         connection_hardware_stats.created_at
  FROM connection_hardware_stats
  WHERE (connection_hardware_stats.created_at AT TIME ZONE %s)::date = %s
  LIMIT 21
  FOR
  UPDATE

## Request

GET http://devspoon.com/wp.php
