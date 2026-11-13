"""4단계 데이터 정합성 회귀 테스트 (docs/crp/groups/phase4-data-integrity)."""
import pytest
from django.contrib import admin
from django.db import IntegrityError, transaction
from django.test import Client
from django.urls import reverse

from blog.models.blog import BlogPost, BooksPost, OnlineStudyPost, OpenSourcePost, ProjectPost, Tag
from blog.models.like import BlogLike, BooksLike, OnlineStudyLike, OpenSourceLike, ProjectLike
from board.models.board import Notice, Reactivation, Visiter
from users.models import User

pytestmark = [pytest.mark.django_db]

# (URL 이름공간, 게시판 이름, 글 모델, 추가 필드)
BLOG = [
    ("blog", "project", ProjectPost, {"dev_lang": "python", "version": "1.0"}),
    ("blog", "online_study", OnlineStudyPost, {"dev_lang": "python"}),
    ("blog", "blog", BlogPost, {}),
    ("blog", "opensource", OpenSourcePost, {"dev_lang": "python"}),
    ("blog", "books", BooksPost, {"dev_lang": "python"}),
]
BOARD = [
    ("board", "notice", Notice, {}),
    ("board", "visiter", Visiter, {}),
    ("board", "reactivation", Reactivation, {}),
]
ALL = BLOG + BOARD
# (좋아요 연결 모델, 글 FK 이름) — BLOG와 같은 순서
LIKES = [
    (ProjectLike, "projects"),
    (OnlineStudyLike, "online_study"),
    (BlogLike, "blogs"),
    (OpenSourceLike, "open_sources"),
    (BooksLike, "books"),
]
BLOG_WITH_LIKES = [b + l for b, l in zip(BLOG, LIKES)]


def ids(rows):
    return [r[1] for r in rows]


@pytest.fixture
def author():
    return User.objects.create_user(
        username="author", email="author@example.com", nickname="author", password="pw", verified=True
    )


def logged_in(user):
    client = Client()
    client.force_login(user)
    return client


def detail_url(ns, name, pk):
    return reverse(f"{ns}:{name}_detail", kwargs={"pk": pk})


# --- F-001: 검색 결과 링크는 글을 만든 경로와 무관하다 ---

# 지금 DB에 들어 있을 수 있는 값: 빈 값(ORM·복사), DB 테이블 이름(admin), 모듈 이름(게시판 기본값), 클래스 이름(뷰)
def stored_values(model):
    return ["", model._meta.db_table, "board.models.board", model.__name__]


@pytest.mark.parametrize("ns,name,model,extra", ALL, ids=ids(ALL))
def test_keyword_search_links_every_post_whatever_its_stored_table_name(ns, name, model, extra, author):
    posts = []
    for value in stored_values(model):
        post = model.objects.create(author=author, title=f"needle {value}", content="c", **extra)
        model.objects.filter(pk=post.pk).update(table_name=value)  # save()를 거치지 않은 옛 데이터
        posts.append(post)

    html = Client().get(reverse("home:search_queryset"), {"keyword": "needle"}).content.decode()

    for post in posts:
        assert f'href="{detail_url(ns, name, post.pk)}"' in html, post.title


@pytest.mark.parametrize("ns,name,model,extra", BLOG, ids=ids(BLOG))
def test_tag_search_links_every_post_whatever_its_stored_table_name(ns, name, model, extra, author):
    tag = Tag.objects.create(tag="needle")
    post = model.objects.create(author=author, title="t", content="c", **extra)
    post.tag_set.add(tag)
    model.objects.filter(pk=post.pk).update(table_name=model._meta.db_table)

    html = Client().get(reverse("home:search_queryset"), {"tag": "needle"}).content.decode()

    assert f'href="{detail_url(ns, name, post.pk)}"' in html


@pytest.mark.parametrize("ns,name,model,extra", ALL, ids=ids(ALL))
def test_saving_a_post_stores_its_class_name(ns, name, model, extra, author):
    post = model.objects.create(author=author, title="t", content="c", table_name="wrong", **extra)
    assert post.table_name == model.__name__

    model_admin = admin.site._registry.get(model) or _any_admin(model)
    post.table_name = ""
    model_admin.save_model(None, post, None, True)
    post.refresh_from_db()
    assert post.table_name == model.__name__


def _any_admin(model):
    from django.contrib.admin.sites import all_sites

    import blog.admin  # noqa: F401  등록 보장
    import board.admin  # noqa: F401

    for site in all_sites:
        if model in site._registry:
            return site._registry[model]
    raise LookupError(model)


# --- F-002: 좋아요 (사용자, 글)은 유일하다 ---


@pytest.mark.parametrize("ns,name,model,extra,like_model,fk", BLOG_WITH_LIKES, ids=ids(BLOG))
def test_duplicate_like_rows_are_rejected_by_the_database(ns, name, model, extra, like_model, fk, author):
    post = model.objects.create(author=author, title="t", content="c", **extra)
    like_model.objects.create(users=author, **{fk: post})

    with pytest.raises(IntegrityError), transaction.atomic():
        like_model.objects.create(users=author, **{fk: post})


# --- F-003: 좋아요 토글 ---


def like(client, ns, name, pk):
    response = client.get(reverse(f"{ns}:{name}_like", kwargs={"pk": pk}))
    assert response.status_code == 200
    return response.json()


@pytest.mark.parametrize("ns,name,model,extra,like_model,fk", BLOG_WITH_LIKES, ids=ids(BLOG))
def test_like_toggle_keeps_one_row_and_a_matching_count(ns, name, model, extra, like_model, fk, author):
    post = model.objects.create(author=author, title="t", content="c", **extra)
    client = logged_in(author)

    for expected in [1, 0, 1, 0, 1]:
        body = like(client, ns, name, post.pk)
        post.refresh_from_db()
        assert like_model.objects.filter(**{fk: post}).count() == expected
        assert post.like_count == expected == body["like_count"]


@pytest.mark.parametrize("ns,name,model,extra,like_model,fk", BLOG_WITH_LIKES, ids=ids(BLOG))
def test_like_toggle_repairs_a_count_that_drifted(ns, name, model, extra, like_model, fk, author):
    # 옛 중복 추가·삭제로 like_count가 실제 행 수와 어긋난 상태
    post = model.objects.create(author=author, title="t", content="c", like_count=0, **extra)
    like_model.objects.create(users=author, **{fk: post})
    client = logged_in(author)

    body = like(client, ns, name, post.pk)  # 이미 좋아요 상태 → 취소

    post.refresh_from_db()
    assert like_model.objects.filter(**{fk: post}).count() == 0
    assert post.like_count == 0 == body["like_count"]
    assert body["message"] == "Like canceled"


# --- 정리 명령 fix_data_integrity (ADR-004, INV-4) ---
# 테스트 DB에는 이미 unique 제약이 있어 중복 행을 만들 수 없다. 중복 고르기는 함수로 확인하고,
# 실제 중복 삭제는 제약 migration 전의 dev DB(PostgreSQL)로 리허설한다(run-log 4단계).


def test_duplicate_ids_keeps_the_first_row_of_each_user_post_pair():
    from blog.management.commands.fix_data_integrity import duplicate_ids

    rows = [
        (1, 10, 100),
        (2, 10, 100),  # 중복
        (3, 11, 100),
        (4, 10, 101),
        (5, 10, 100),  # 중복
        (6, None, 100),  # 비어 있는 행은 건드리지 않는다
        (7, None, 100),
        (8, 12, None),
    ]
    assert duplicate_ids(rows) == [2, 5]


def run_fix(*args):
    from io import StringIO

    from django.core.management import call_command

    out = StringIO()
    call_command("fix_data_integrity", *args, stdout=out)
    return out.getvalue()


@pytest.mark.parametrize("ns,name,model,extra,like_model,fk", BLOG_WITH_LIKES, ids=ids(BLOG))
def test_fix_data_integrity_repairs_counts_and_table_names(ns, name, model, extra, like_model, fk, author):
    other = User.objects.create_user(username="other", email="o@example.com", nickname="other", password="pw")
    post = model.objects.create(author=author, title="t", content="c", **extra)
    like_model.objects.create(users=author, **{fk: post})
    like_model.objects.create(users=other, **{fk: post})
    model.objects.filter(pk=post.pk).update(like_count=7, table_name="")
    board = Notice.objects.create(author=author, title="n", content="c")
    Notice.objects.filter(pk=board.pk).update(table_name="board.models.board")

    run_fix("--dry-run")
    post.refresh_from_db()
    board.refresh_from_db()
    assert (post.like_count, post.table_name, board.table_name) == (7, "", "board.models.board")

    run_fix()
    post.refresh_from_db()
    board.refresh_from_db()
    assert (post.like_count, post.table_name, board.table_name) == (2, model.__name__, "Notice")
    assert like_model.objects.filter(**{fk: post}).count() == 2  # 중복이 아닌 좋아요는 지우지 않는다

    second = run_fix()
    assert "중복 좋아요 0건" in second and "바로잡기 0건" in second and "맞추기 0건" in second
    assert not any(f" {n}건" in second for n in range(1, 10))
