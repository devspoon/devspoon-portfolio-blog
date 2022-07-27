from django import template
from django.core.paginator import Page

register = template.Library()

@register.filter(name='slice_visible_pages')
def slice_visible_pages(paging: Page):
    min_page = int((paging.number - 1) / 10) * 10 + 1
    min_page = max(min_page, 1)
    max_page = min(min_page + 9, paging.paginator.num_pages)
    return range(min_page, max_page + 1)

'''
reference : https://steemit.com/kr-dev/@nhj12311/ewbgg
reference : https://zepinos.tistory.com/28

full count of item = countlist
full count of page = countPage  # ex) # 1,2,3 ... 10
current page number = page

page = 5
countPage = 10

startPage = ((page - 1) / countPage) * countPage + 1
endPage = startPage + countPage -1

'''
