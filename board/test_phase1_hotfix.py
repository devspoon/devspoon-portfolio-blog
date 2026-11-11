"""1단계 핫픽스 회귀 테스트 — board 게시판 3종 (docs/crp/groups/phase1-hotfix).

board 앱은 tests.py 모듈이 있어 tests/ 패키지를 만들 수 없으므로 앱 루트에 둔다.
"""
import pytest
from django.core.cache import cache
from django.test import Client
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
