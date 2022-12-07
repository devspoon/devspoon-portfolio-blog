from django.contrib import admin
from django.contrib.admin import AdminSite

class BoardAdminSite(AdminSite):
    site_header = "Board Admin"
    site_title = "Board Admin Portal"
    index_title = "Welcome to Board Admin Portal"

board_admin_site = BoardAdminSite(name='board_admin')