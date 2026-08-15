# Social URLs
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'follows', views.FollowViewSet, basename='follow')

urlpatterns = [
    # 关注系统
    path('follow/', views.follow_user, name='follow-user'),
    path('follow/<int:user_id>/', views.unfollow_user, name='unfollow-user'),

    # 聊天联系人列表
    path('chat/following/', views.get_following_list, name='chat-following'),
    path('chat/followers/', views.get_followers_list, name='chat-followers'),
    path('chat/friends/', views.get_friends_list, name='chat-friends'),
    path('chat/groups/', views.get_groups_list, name='chat-groups'),

    # 好友申请
    path('chat/friend-requests/', views.get_friend_requests, name='chat-friend-requests'),
    path('chat/friend-request/', views.send_friend_request, name='send-friend-request'),
    path('chat/friend-request/<int:pk>/accept/', views.accept_friend_request, name='accept-friend-request'),
    path('chat/friend-request/<int:pk>/reject/', views.reject_friend_request, name='reject-friend-request'),

    # 聊天消息
    path('chat/messages/', views.get_messages, name='chat-messages'),
    path('chat/messages/send/', views.send_message, name='send-message'),
    path('chat/messages/mark-read/', views.mark_messages_as_read, name='mark-messages-read'),
    path('chat/unread-count/', views.get_unread_count, name='unread-count'),
    path('chat/presence/<int:user_id>/', views.get_user_presence, name='user-presence'),

    # 搜索
    path('chat/search/', views.search_users, name='search-users'),

    # Router URLs
    path('', include(router.urls)),
]
