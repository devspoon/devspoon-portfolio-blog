"""1단계 핫픽스 회귀 테스트 — board 게시판 3종.

board 앱은 tests.py 모듈이 있어 tests/ 패키지를 만들 수 없으므로 앱 루트에 둔다.
"""
import pytest
from django.core.cache import cache
from django.db import connection
from django.test import Client
from django.test.utils import CaptureQueriesContext
from django.urls import reverse

from board.models.board import Notice, Reactivation, Visiter
from board.models.board_reply import NoticeReply, ReactivationReply, VisiterReply
from users.models import User

pytestmark = [pytest.mark.board, pytest.mark.django_db]

# (게시판 이름, 글 모델, 댓글 모델)
BOARDS = [
    ("notice", Notice, NoticeReply),
    ("visiter", Visiter, VisiterReply),
    ("reactivation", Reactivation, ReactivationReply),
]
BOARD_IDS = [board[0] for board in BOARDS]


def make_user(username):
    return User.objects.create_user(
        username=username,
        email=f"{username}@example.com",
        nickname=username,
        password="password",
        verified=True,
    )


def logged_in(user):
    client = Client()
    client.force_login(user)
    return client


@pytest.fixture
def author():
    return make_user("author")


@pytest.fixture
def other():
    return make_user("other")


# --- C2: 댓글 삭제가 롤백되지 않고 reply_count가 줄어든다 (F-005, INV-4) ---


@pytest.mark.parametrize("name,board_model,reply_model", BOARDS, ids=BOARD_IDS)
def test_deleting_a_reply_removes_it_and_decrements_reply_count(
    name, board_model, reply_model, author
):
    board = board_model.objects.create(
        author=author, title="t", content="c", reply_count=1
    )
    reply = reply_model.objects.create(author=author, comment="hi", board=board)

    reply.delete()

    assert not reply_model.objects.filter(pk=reply.pk).exists()
    board.refresh_from_db()
    assert board.reply_count == 0


@pytest.mark.parametrize("name,board_model,reply_model", BOARDS, ids=BOARD_IDS)
def test_reply_count_never_goes_below_zero(name, board_model, reply_model, author):
    board = board_model.objects.create(
        author=author, title="t", content="c", reply_count=0
    )
    reply = reply_model.objects.create(author=author, comment="hi", board=board)

    reply.delete()

    board.refresh_from_db()
    assert board.reply_count == 0


# --- C1: 상세 페이지의 작성자 여부는 요청자 기준이다 (F-001, INV-1·INV-3) ---


@pytest.mark.parametrize("name,board_model,reply_model", BOARDS, ids=BOARD_IDS)
def test_detail_owner_controls_follow_the_visitor_not_the_first_visitor(
    name, board_model, reply_model, author, other
):
    board = board_model.objects.create(author=author, title="t", content="c")
    url = reverse(f"board:{name}_detail", kwargs={"pk": board.pk})
    author_client = logged_in(author)

    assert author_client.get(url).context["user_auth"] is True
    assert logged_in(other).get(url).context["user_auth"] is False
    assert Client().get(url).context["user_auth"] is False
    assert author_client.get(url).context["user_auth"] is True

    assert cache.keys("*user_auth*") == []


# --- C1(댓글)·N1: 댓글 목록 (F-003·F-006·F-009, INV-1·INV-5, ADR-006) ---


def reply_list_url(name, board):
    # 화면 JS(static/js/blog_apis.js)는 항상 ?page=를 붙여 호출한다.
    return reverse(f"board:{name}_reply_list", kwargs={"pk": board.pk}) + "?page=1"


@pytest.mark.parametrize("name,board_model,reply_model", BOARDS, ids=BOARD_IDS)
def test_reply_list_owner_flag_follows_the_visitor(
    name, board_model, reply_model, author, other
):
    board = board_model.objects.create(author=author, title="t", content="c")
    reply_model.objects.create(author=author, comment="hi", board=board)
    url = reply_list_url(name, board)

    # 작성자가 먼저 불러 캐시를 채운다. 응답의 0번은 페이지 정보다.
    assert logged_in(author).get(url).json()[1]["user_auth"] is True

    assert logged_in(other).get(url).json()[1]["user_auth"] is False
    assert Client().get(url).json()[1]["user_auth"] is False


@pytest.mark.parametrize("name,board_model,reply_model", BOARDS, ids=BOARD_IDS)
def test_reply_list_owner_flag_does_not_depend_on_nickname(name, board_model, reply_model):
    # User.__str__은 nickname이다. nickname이 username과 달라도 작성자로 판정해야 한다.
    author = User.objects.create_user(
        username="author-login",
        email="author-login@example.com",
        nickname="Author Nick",
        password="password",
        verified=True,
    )
    board = board_model.objects.create(author=author, title="t", content="c")
    reply_model.objects.create(author=author, comment="hi", board=board)

    reply = logged_in(author).get(reply_list_url(name, board)).json()[1]

    assert reply["user_auth"] is True
    # 판정용 내부 값은 응답에 노출하지 않는다.
    assert "author_id" not in reply


def count_queries(client, url):
    with CaptureQueriesContext(connection) as queries:
        response = client.get(url)
    assert response.status_code == 200
    # 테스트 설정에서 켜진 django-silk가 확률적으로 자기 테이블을 정리하는 쿼리는 뺀다.
    return sum(
        1
        for query in queries.captured_queries
        if "silk_" not in query["sql"] and "SAVEPOINT" not in query["sql"]
    )


@pytest.mark.parametrize("name,board_model,reply_model", BOARDS, ids=BOARD_IDS)
def test_reply_list_query_count_does_not_grow_with_replies(
    name, board_model, reply_model, author
):
    def board_with_replies(count):
        board = board_model.objects.create(author=author, title="t", content="c")
        for _ in range(count):
            reply_model.objects.create(author=author, comment="hi", board=board)
        return reply_list_url(name, board)

    client = Client()
    # 첫 요청은 일자별 통계 row를 만드는 INSERT가 섞이므로 제외한다.
    count_queries(client, board_with_replies(0))

    assert count_queries(client, board_with_replies(1)) == count_queries(
        client, board_with_replies(5)
    )
