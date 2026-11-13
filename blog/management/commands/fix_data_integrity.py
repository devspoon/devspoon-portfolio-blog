from django.core.management.base import BaseCommand
from django.db import transaction
from django.db.models import Count

from blog.models.blog import BlogPost, BooksPost, OnlineStudyPost, OpenSourcePost, ProjectPost
from blog.models.like import BlogLike, BooksLike, OnlineStudyLike, OpenSourceLike, ProjectLike
from board.models.board import Notice, Reactivation, Visiter

# (좋아요 연결 모델, 글 FK 이름)
LIKE_MODELS = (
    (ProjectLike, "projects"),
    (OnlineStudyLike, "online_study"),
    (BlogLike, "blogs"),
    (OpenSourceLike, "open_sources"),
    (BooksLike, "books"),
)
LIKED_POST_MODELS = (ProjectPost, OnlineStudyPost, BlogPost, OpenSourcePost, BooksPost)
POST_MODELS = LIKED_POST_MODELS + (Notice, Visiter, Reactivation)


def duplicate_ids(rows):
    """(pk, user_id, post_id)를 만든 순서대로 받아, (사용자, 글)마다 첫 행을 빼고 나머지 pk를 돌려준다.

    사용자나 글이 비어 있는 행은 제약 대상이 아니므로 건드리지 않는다.
    """
    seen = set()
    duplicates = []
    for pk, user_id, post_id in rows:
        if user_id is None or post_id is None:
            continue
        if (user_id, post_id) in seen:
            duplicates.append(pk)
        else:
            seen.add((user_id, post_id))
    return duplicates


class Command(BaseCommand):
    help = (
        "좋아요 (사용자, 글) 중복을 가장 먼저 만든 행 1개만 남기고 지우고, like_count를 실제 좋아요 수로, "
        "table_name을 모델 클래스 이름으로 맞춘다. 좋아요 unique 제약 migration 전에 실행한다. "
        "여러 번 실행해도 결과가 같다 (docs/crp/groups/phase4-data-integrity)."
    )

    def add_arguments(self, parser):
        parser.add_argument("--dry-run", action="store_true", help="변경 없이 대상만 출력한다.")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        if dry_run:
            self.stdout.write(self.style.WARNING("dry-run: 변경하지 않는다."))

        for like_model, fk in LIKE_MODELS:
            self.dedupe_likes(like_model, fk, dry_run)
        for model in LIKED_POST_MODELS:
            self.fix_like_count(model, dry_run)
        for model in POST_MODELS:
            self.fix_table_name(model, dry_run)

    def dedupe_likes(self, like_model, fk, dry_run):
        rows = like_model.objects.order_by("created_at", "pk").values_list("pk", "users_id", f"{fk}_id")
        ids = duplicate_ids(rows)
        self.stdout.write(f"{like_model._meta.db_table}: 중복 좋아요 {len(ids)}건 삭제")
        if ids and not dry_run:
            with transaction.atomic():
                like_model.objects.filter(pk__in=ids).delete()

    def fix_like_count(self, model, dry_run):
        # distinct 사용자 수 = 중복을 지운 뒤의 행 수. dry-run에서도 같은 값을 보여 준다.
        wrong = [
            (pk, actual)
            for pk, stored, actual in model.objects.annotate(
                actual=Count("like_user_set", distinct=True)
            ).values_list("pk", "like_count", "actual")
            if stored != actual
        ]
        self.stdout.write(f"{model._meta.db_table}: like_count 바로잡기 {len(wrong)}건")
        if wrong and not dry_run:
            with transaction.atomic():
                for pk, actual in wrong:
                    model.objects.filter(pk=pk).update(like_count=actual)

    def fix_table_name(self, model, dry_run):
        wrong = model.objects.exclude(table_name=model.__name__)
        self.stdout.write(f"{model._meta.db_table}: table_name 맞추기 {wrong.count()}건")
        if not dry_run:
            wrong.update(table_name=model.__name__)
