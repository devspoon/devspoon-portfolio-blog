import logging

from django.conf import settings
from django.db import DatabaseError, IntegrityError, transaction
from django.db.models import F
from django.utils import timezone

from ..models import ConnectionHardwareStats, ConnectionMethodStats

logger = logging.getLogger(getattr(settings, "COMMON_LOGGER", "django"))

DEFAULT_EXCLUDED_PATH_PREFIXES = (
    "/admin/",
    "/static/",
    "/media/",
    "/silk/",
    "/__debug__/",
    "/favicon.ico",
    "/robots.txt",
    "/sitemap.xml",
    "/sitemap-",
)


def increment_daily_counter(model, field_name: str) -> None:
    """일자별 집계 row의 카운터 1개를 원자적으로 증가시킨다.

    `get_or_create(created_at__date=...)`는 생성 시 조회 조건을 컬럼에 반영할 수
    없어 같은 날짜 row가 중복 생성되고, 한 번 중복이 생기면 이후 모든 요청에서
    `MultipleObjectsReturned`가 발생했다. `stat_date` 유니크 컬럼을 집계키로 쓰고
    UPDATE -> (없으면) INSERT -> (경합 시) UPDATE 순서로 처리해 중복을 구조적으로
    막는다. UPDATE 한 문장이 원자적이므로 select_for_update 잠금이 필요 없다.
    """
    today = timezone.localdate()

    updated = model.objects.filter(stat_date=today).update(
        **{field_name: F(field_name) + 1}
    )
    if updated:
        return

    try:
        # 유니크 제약 위반이 바깥 트랜잭션을 깨뜨리지 않도록 savepoint로 감싼다.
        with transaction.atomic():
            model.objects.create(stat_date=today, **{field_name: 1})
    except IntegrityError:
        # 다른 요청이 먼저 오늘 row를 만든 경우. 유니크 제약이 중복을 막아준다.
        model.objects.filter(stat_date=today).update(
            **{field_name: F(field_name) + 1}
        )


class BaseStatsMiddleware:
    """통계 미들웨어 공통 동작.

    통계 집계는 부가 기능이므로 DB 오류가 사용자 요청 실패로 번지지 않게 한다.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        self.excluded_prefixes = tuple(
            getattr(
                settings,
                "STATS_EXCLUDED_PATH_PREFIXES",
                DEFAULT_EXCLUDED_PATH_PREFIXES,
            )
        )

    def is_excluded(self, request) -> bool:
        return request.path_info.startswith(self.excluded_prefixes)

    def __call__(self, request):
        if not self.is_excluded(request):
            try:
                self.record(request)
            except DatabaseError as error:
                logger.warning(
                    "failed to record connection stats",
                    extra={
                        "middleware": self.__class__.__name__,
                        "path": request.path_info,
                        "error": str(error),
                    },
                )

        return self.get_response(request)

    def record(self, request) -> None:  # pragma: no cover - 하위 클래스에서 구현
        raise NotImplementedError


class ConnectionMethodStatsMiddleware(BaseStatsMiddleware):
    """운영체제별 일일 접속 통계."""

    @staticmethod
    def resolve_field(os_info: str) -> str:
        if "Windows" in os_info:
            return "win"
        if "mac" in os_info:
            return "mac"
        if "iPhone" in os_info:
            return "iph"
        if "Android" in os_info:
            return "android"
        return "oth"

    def record(self, request) -> None:
        os_info = request.META.get("HTTP_USER_AGENT")
        if not os_info:
            return

        increment_daily_counter(ConnectionMethodStats, self.resolve_field(os_info))


class ConnectionHardwareStatsMiddleware(BaseStatsMiddleware):
    """기기 종류별 일일 접속 통계."""

    @staticmethod
    def resolve_field(user_agent) -> str | None:
        if user_agent.is_mobile:
            return "mobile"
        if user_agent.is_tablet:
            return "tablet"
        if user_agent.is_pc:
            return "pc"
        if user_agent.is_bot:
            return "bot"
        return None

    def record(self, request) -> None:
        user_agent = getattr(request, "user_agent", None)
        if user_agent is None:
            return

        field_name = self.resolve_field(user_agent)
        if field_name is None:
            return

        increment_daily_counter(ConnectionHardwareStats, field_name)
