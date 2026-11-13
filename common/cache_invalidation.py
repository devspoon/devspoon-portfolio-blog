"""캐시 무효화를 한 곳에서 한다 (docs/crp/groups/phase3-cache-redesign, ADR-003).

모델 시그널(post_save·post_delete, mptt node_moved)에서 무효화를 transaction.on_commit으로
미룬다. 커밋 전에 지우면 그 사이 읽은 요청이 옛 값을 다시 캐시할 수 있고, 롤백된 쓰기는
지울 이유가 없다. 시그널이 없는 queryset.update() 경로(admin 일괄 액션)는
invalidate_queryset()을 직접 부른다. 연결은 HomeConfig.ready()에서 한다.
"""
from django.apps import apps
from django.core.cache import cache
from django.db import transaction
from django.db.models.signals import m2m_changed, post_delete, post_save
from mptt.signals import node_moved

from common.components.django_redis_cache_components import (
    INDEX_KEY,
    MAIN_MENU_KEY,
    SITE_INFO_KEY,
    all_portfolio_keys,
    invalidate_replies,
    replies_prefix,
)

# index(최신 글·프로젝트)에 나오는 모델
INDEX_MODELS = {
    "blog.BlogPost",
    "blog.BooksPost",
    "blog.OnlineStudyPost",
    "blog.OpenSourcePost",
    "blog.ProjectPost",
    "portfolio.AboutProjects",
}
# portfolio 화면·경력 JSON에 나오는 모델. 프로젝트 목록이 ProjectPost 제목을, 기술 스택 그림이
# 블로그 글 5종의 공개 글 수(태그별)를 보여 준다.
BLOG_POST_MODELS = {
    "blog.BlogPost",
    "blog.BooksPost",
    "blog.OnlineStudyPost",
    "blog.OpenSourcePost",
    "blog.ProjectPost",
}
PORTFOLIO_MODELS = {
    "portfolio.Portfolio",
    "portfolio.PersonalInfo",
    "portfolio.PortfolioSummary",
    "portfolio.WorkExperience",
    "portfolio.EducationStudy",
    "portfolio.InterestedIn",
    "portfolio.AboutProjects",
} | BLOG_POST_MODELS
FIXED_KEYS = {
    "home.MainMenu": MAIN_MENU_KEY,
    "home.SiteInfo": SITE_INFO_KEY,
}
# 댓글 모델 → 글을 가리키는 FK 이름
REPLY_MODELS = {
    "blog.BlogPostReply": "post",
    "blog.BooksPostReply": "post",
    "blog.OnlineStudyPostReply": "post",
    "blog.OpenSourcePostReply": "post",
    "blog.ProjectPostReply": "post",
    "board.NoticeReply": "board",
    "board.VisiterReply": "board",
    "board.ReactivationReply": "board",
}


def _keys_for(label):
    keys = []
    if label in INDEX_MODELS:
        keys.append(INDEX_KEY)
    if label in PORTFOLIO_MODELS:
        keys.extend(all_portfolio_keys())
    if label in FIXED_KEYS:
        keys.append(FIXED_KEYS[label])
    return keys


def _post_model_of(reply_model):
    return reply_model._meta.get_field(REPLY_MODELS[reply_model._meta.label]).related_model


def invalidate(model, post_pks=()):
    """model의 쓰기가 커밋되면 관련 캐시를 지운다. 댓글 모델이면 post_pks 글의 댓글 목록도."""
    keys = _keys_for(model._meta.label)
    post_model = _post_model_of(model) if model._meta.label in REPLY_MODELS else None
    post_pks = set(post_pks) if post_model else set()

    def run():
        if keys:
            cache.delete_many(keys)
        for pk in post_pks:
            invalidate_replies(post_model, pk)

    if keys or post_pks:
        transaction.on_commit(run)


def invalidate_queryset(queryset):
    """queryset.update()처럼 시그널이 없는 쓰기 뒤에 부른다."""
    model = queryset.model
    fk = REPLY_MODELS.get(model._meta.label)
    post_pks = queryset.values_list(f"{fk}_id", flat=True) if fk else ()
    invalidate(model, post_pks)


def clear_model(model):
    """admin의 "캐시 전체 삭제" 액션용. 관리자가 수동으로 실행하므로 패턴 삭제(SCAN)를 허용한다."""
    label = model._meta.label
    keys = _keys_for(label)
    if keys:
        cache.delete_many(keys)
    if label in REPLY_MODELS:
        cache.delete_pattern(f"{replies_prefix(_post_model_of(model))}:*")
    elif any(_post_model_of(apps.get_model(r)) is model for r in REPLY_MODELS):
        cache.delete_pattern(f"{replies_prefix(model)}:*")


def _on_write(sender, instance, **kwargs):
    fk = REPLY_MODELS.get(sender._meta.label)
    invalidate(sender, [getattr(instance, f"{fk}_id")] if fk else ())


def connect():
    labels = INDEX_MODELS | PORTFOLIO_MODELS | set(FIXED_KEYS) | set(REPLY_MODELS)
    for label in labels:
        model = apps.get_model(label)
        uid = f"cache-invalidation:{label}"
        post_save.connect(_on_write, sender=model, dispatch_uid=uid)
        post_delete.connect(_on_write, sender=model, dispatch_uid=uid)
    # mptt 드래그 이동은 save()를 거치지 않는다.
    node_moved.connect(_on_write, sender=apps.get_model("home.MainMenu"), dispatch_uid="cache-invalidation:menu-move")
    # 태그는 글을 저장한 뒤 tag_set에 붙는다. 기술 스택 그림(portfolio)의 태그별 글 수가 바뀐다.
    for label in BLOG_POST_MODELS:
        through = apps.get_model(label).tag_set.through
        m2m_changed.connect(_on_tags_changed, sender=through, dispatch_uid=f"cache-invalidation:tags:{label}")


def _on_tags_changed(sender, instance, action, **kwargs):
    if action in ("post_add", "post_remove", "post_clear"):
        invalidate(apps.get_model("portfolio.PersonalInfo"))  # portfolio 키 전체(언어별)
