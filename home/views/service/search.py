import logging

from django.conf import settings
from django.core.paginator import Paginator
from django.db.models import Q

from blog.models.blog import (
    BlogPost,
    BooksPost,
    OnlineStudyPost,
    OpenSourcePost,
    ProjectPost,
    Tag,
)
from board.models.board import Notice, Reactivation, Visiter

logger = logging.getLogger(getattr(settings, "HOME_LOGGER", "django"))


class Search:
    def get_keyword_search_query_set(self, instance, keyword):
        result = (
            instance.activate_objects.get_data()
            .filter(
                Q(title__icontains=str(keyword)) | Q(content__icontains=str(keyword))
            )
            .distinct()
            .values(
                "pk",
                "title",
                "created_at",
                "author__username",
                "visit_count",
                "table_name",
            )
        )

        return result

    def get_tag_search_query_set(self, instance, tag):
        result = (
            instance.activate_objects.get_data()
            .filter(tag_set__in=tag)
            .distinct()
            .values(
                "pk",
                "title",
                "created_at",
                "author__username",
                "visit_count",
                "table_name",
            )
        )

        return result

    def queryset_tag_search(self, tag, page_number, per_page):
        tag = Tag.objects.filter(tag=tag)

        # blog result
        project_queryset = self.get_tag_search_query_set(ProjectPost, tag)
        onlinestudy_queryset = self.get_tag_search_query_set(OnlineStudyPost, tag)
        blog_queryset = self.get_tag_search_query_set(BlogPost, tag)
        opensource_queryset = self.get_tag_search_query_set(OpenSourcePost, tag)
        books_queryset = self.get_tag_search_query_set(BooksPost, tag)

        result_queryset = project_queryset.union(onlinestudy_queryset, all=False)
        result_queryset = result_queryset.union(blog_queryset, all=False)
        result_queryset = result_queryset.union(opensource_queryset, all=False)
        result_queryset = result_queryset.union(books_queryset, all=False).order_by(
            "-created_at"
        )

        print("result_queryset : ", result_queryset)

        logger.debug("result_queryset : {}".format(result_queryset))

        paginator = Paginator(result_queryset, per_page)

        paging = paginator.get_page(page_number)

        logger.debug("paging : {}".format(paging))

        result = {
            "page_obj": paging,
            "board": result_queryset,
            "tag": tag,
        }

        return result

    def queryset_keyword_search(self, keyword, page_number, per_page):
        # board result
        notice_queryset = self.get_keyword_search_query_set(Notice, keyword)
        visiter_queryset = self.get_keyword_search_query_set(Visiter, keyword)
        reactivation_queryset = self.get_keyword_search_query_set(Reactivation, keyword)

        # blog result
        project_queryset = self.get_keyword_search_query_set(ProjectPost, keyword)
        onlinestudy_queryset = self.get_keyword_search_query_set(
            OnlineStudyPost, keyword
        )
        blog_queryset = self.get_keyword_search_query_set(BlogPost, keyword)
        opensource_queryset = self.get_keyword_search_query_set(OpenSourcePost, keyword)
        books_queryset = self.get_keyword_search_query_set(BooksPost, keyword)

        result_queryset = notice_queryset.union(visiter_queryset, all=False)
        result_queryset = result_queryset.union(reactivation_queryset, all=False)
        result_queryset = result_queryset.union(project_queryset, all=False)
        result_queryset = result_queryset.union(onlinestudy_queryset, all=False)
        result_queryset = result_queryset.union(blog_queryset, all=False)
        result_queryset = result_queryset.union(opensource_queryset, all=False)
        result_queryset = result_queryset.union(books_queryset, all=False).order_by(
            "-created_at"
        )

        logger.debug("result_queryset : {}".format(result_queryset))

        paginator = Paginator(result_queryset, per_page)

        pages = paginator.get_page(page_number)

        logger.debug("pages : {}".format(pages))

        result = {
            "page_obj": pages,
            "board": pages.object_list,
            "keyword": keyword,
        }

        return result
