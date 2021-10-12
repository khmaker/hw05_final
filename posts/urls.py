# coding=utf-8
from django.urls import path

from posts.views import (
    AddCommentView, CreatePostView, FollowIndexView, GroupView, IndexView,
    PostDeleteView, PostUpdateView, PostView, ProfileFollowView,
    ProfileUnfollowView,
    ProfileView,
)

urlpatterns = [
    path(
        '',
        IndexView.as_view(), name='index'
        ),
    path(
        'group/<slug:slug>/',
        GroupView.as_view(), name='group_posts'
        ),
    path(
        'new/',
        CreatePostView.as_view(), name='new_post'
        ),
    path(
        'follow/',
        FollowIndexView.as_view(), name='follow_index'
        ),
    path(
        '<str:username>/follow/',
        ProfileFollowView.as_view(), name='profile_follow'
        ),
    path(
        '<str:username>/unfollow/',
        ProfileUnfollowView.as_view(), name='profile_unfollow'
        ),
    path(
        '<str:username>/',
        ProfileView.as_view(), name='profile'
        ),
    path(
        '<str:username>/<int:post_id>/',
        PostView.as_view(), name='post'
        ),
    path(
        '<str:username>/<int:post_id>/edit/',
        PostUpdateView.as_view(), name='post_edit'
        ),
    path(
        '<str:username>/<int:post_id>/delete/',
        PostDeleteView.as_view(), name='post_delete'
        ),
    path(
        '<str:username>/<int:post_id>/comment',
        AddCommentView.as_view(), name='add_comment'
        ),
]
