import logging
import datetime

from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.db.models import Q, F
#from django.core.cache import cache

from django.db.models import Exists, OuterRef
from board.models.board import Notice, Visiter, Reactivation
from blog.models.blog import ProjectPost, OnlineStudyPost, BlogPost, OpenSourcePost, BooksPost, Tag

logger = logging.getLogger(__name__)

class Search:
    def create_redis_cache_key(self,category, keyword, page_number):
        identifier = 'search'
        return "%s:%s:%s:%s" % (identifier,category, keyword, page_number)


    def get_keyword_search_query_set(self, instance, keyword):
        result = instance.activate_objects.get_data().filter(Q(title__icontains=str(keyword)) | Q(content__icontains=str(keyword))).distinct().values('pk', 'title','created_at','author__username','visit_count','table_name')

        return result

    def get_tag_search_query_set(self, instance, tag):
        result = instance.activate_objects.get_data().filter(tag_set__in = tag).distinct().values('pk', 'title','created_at','author__username','visit_count','table_name')

        return result

    def queryset_tag_search(self, tag, page_number, per_page):
        cache_key = self.create_redis_cache_key('queryset_tag',tag,page_number)
        # cached_data = cache.get(cache_key)
        # if cached_data:
        #     return cached_data
        #logger.debug("get_search_query_set queryset : {}".format(queryset))

        tag = Tag.objects.filter(tag=tag)

        #blog result
        project_queryset=self.get_tag_search_query_set(ProjectPost,tag)
        onlinestudy_queryset=self.get_tag_search_query_set(OnlineStudyPost,tag)
        blog_queryset=self.get_tag_search_query_set(BlogPost,tag)
        opensource_queryset=self.get_tag_search_query_set(OpenSourcePost,tag)
        books_queryset=self.get_tag_search_query_set(BooksPost,tag)

        result_queryset=project_queryset.union(onlinestudy_queryset,all=False)
        result_queryset=result_queryset.union(blog_queryset,all=False)
        result_queryset=result_queryset.union(opensource_queryset,all=False)
        result_queryset=result_queryset.union(books_queryset,all=False).order_by('-created_at')

        print('result_queryset : ',result_queryset)

        logger.debug("result_queryset : {}".format(result_queryset))

        paginator = Paginator(result_queryset, per_page)

        paging = paginator.get_page(page_number)

        logger.debug("paging : {}".format(paging))

        result = {
            'page_obj': paging,
            'board': result_queryset,
            'tag': tag,
        }

        #cache.set(cache_key, result, 60)

        return result


    def queryset_keyword_search(self, keyword, page_number, per_page):
        cache_key = self.create_redis_cache_key('queryset_keyword',keyword,page_number)
        # cached_data = cache.get(cache_key)
        # if cached_data:
        #     return cached_data
        #logger.debug("get_search_query_set queryset : {}".format(queryset))

        #board result
        notice_queryset=self.get_keyword_search_query_set(Notice, keyword)
        visiter_queryset=self.get_keyword_search_query_set(Visiter,keyword)
        reactivation_queryset=self.get_keyword_search_query_set(Reactivation,keyword)

        #blog result
        project_queryset=self.get_keyword_search_query_set(ProjectPost,keyword)
        onlinestudy_queryset=self.get_keyword_search_query_set(OnlineStudyPost,keyword)
        blog_queryset=self.get_keyword_search_query_set(BlogPost,keyword)
        opensource_queryset=self.get_keyword_search_query_set(OpenSourcePost,keyword)
        books_queryset=self.get_keyword_search_query_set(BooksPost,keyword)

        result_queryset=notice_queryset.union(visiter_queryset,all=False)
        result_queryset=result_queryset.union(reactivation_queryset,all=False)
        result_queryset=result_queryset.union(project_queryset,all=False)
        result_queryset=result_queryset.union(onlinestudy_queryset,all=False)
        result_queryset=result_queryset.union(blog_queryset,all=False)
        result_queryset=result_queryset.union(opensource_queryset,all=False)
        result_queryset=result_queryset.union(books_queryset,all=False).order_by('-created_at')

        logger.debug("result_queryset : {}".format(result_queryset))

        paginator = Paginator(result_queryset, per_page)

        pages = paginator.get_page(page_number)

        logger.debug("pages : {}".format(pages))

        result = {
            'page_obj': pages,
            'board': pages.object_list,
            'keyword': keyword,
        }
        
        print('result : ',result)

        #cache.set(cache_key, result, 60)

        return result