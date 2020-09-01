from django.urls import path

from . import views


urlpatterns = [
        path('',
             views.IndexView.as_view(), name='index'),
        path('group/<slug:slug>/',
             views.GroupView.as_view(), name='group_posts'),
        path('new/',
             views.CreatePostView.as_view(), name='new_post'),
        path('follow/',
             views.FollowIndexView.as_view(), name='follow_index'),
        path('<str:username>/follow/',
             views.ProfileFollowView.as_view(), name='profile_follow'),
        path('<str:username>/unfollow/',
             views.ProfileUnfollowView.as_view(), name='profile_unfollow'),
        path('<str:username>/',
             views.ProfileView.as_view(), name='profile'),
        path('<str:username>/<int:post_id>/',
             views.PostView.as_view(), name='post'),
        path('<str:username>/<int:post_id>/edit/',
             views.PostUpdateView.as_view(), name='post_edit'),
        path('<str:username>/<int:post_id>/delete/',
             views.PostDeleteView.as_view(), name='post_delete'),
        path('<str:username>/<int:post_id>/comment',
             views.AddCommentView.as_view(), name='add_comment'),
]
