from django.urls import path

from . import views
from .feeds import LatestPostsFeed


app_name = 'blog'

urlpatterns = [
    path('', views.post_list_view, name='post-list'),
    path('search/', views.post_search_view, name='post-search'),
    path('feed/', LatestPostsFeed(), name='post-feed'),
    path('tag/<slug:tag_slug>', views.post_list_view, name='post-list-by-tag'),
    # path('', views.PostListView.as_view(), name='post-list'),
    path('<int:year>/<int:month>/<int:day>/<slug:post>/', views.post_detail_view, name='post-detail'),
    path('<int:post_id>/share/', views.post_share_view, name='post-share')
]