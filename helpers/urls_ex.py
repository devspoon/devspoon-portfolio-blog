from django.urls import path, include
from . import views

from mainapp.main import views as main_views
from mainapp.video import views as video_views

main_patterns = [
    path('',main_views.main),
    path('signup/', main_views.signup, name='signup'),
    path('signin/', main_views.signin, name='signin'),
]

video_patterns = [
    path('', video_views.swipe),
    path('show/', video_views.show, name='show'),
    path('detail/<int:id>', video_views.detail, name='detail'),
    path('like/', video_views.like, name='like'),
]

urlpatterns = [
    path('main/', include(main_patterns)),
    path('video/', include(video_patterns)),
]