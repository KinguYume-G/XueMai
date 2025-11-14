import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.notifications.models import Notification
from apps.users.models import User

print('=' * 60)
print('第二阶段：将通知转移到真正的Gao用户')
print('=' * 60)

# 获取用户
jeffrey = User.objects.get(id=14)  # 当前有11条通知的用户
gao = User.objects.get(id=12)  # 真正的Gao用户

print(f'\n[INFO] 源用户: {jeffrey.username} (ID: {jeffrey.id}, {jeffrey.email})')
print(f'[INFO] 目标用户: {gao.username} (ID: {gao.id}, {gao.email})')

# 查询Jeffrey的通知
jeffrey_notifications = Notification.objects.filter(user=jeffrey)
count_before = jeffrey_notifications.count()

print(f'\n[INFO] Jeffrey当前有 {count_before} 条通知')
print(f'[INFO] Gao当前有 {Notification.objects.filter(user=gao).count()} 条通知')

# 执行转移
print('\n[执行] 开始转移通知...')
updated_count = jeffrey_notifications.update(user=gao)

print(f'[OK] 成功转移 {updated_count} 条通知')

# 验证转移结果
jeffrey_count_after = Notification.objects.filter(user=jeffrey).count()
gao_count_after = Notification.objects.filter(user=gao).count()

print(f'\n[验证] 转移后:')
print(f'  - Jeffrey的通知数: {jeffrey_count_after}条')
print(f'  - Gao的通知数: {gao_count_after}条')

# 按类型统计Gao的通知
like_count = Notification.objects.filter(user=gao, type='like').count()
comment_count = Notification.objects.filter(user=gao, type='comment').count()
follow_count = Notification.objects.filter(user=gao, type='follow').count()
system_count = Notification.objects.filter(user=gao, type='system').count()
unread_count = Notification.objects.filter(user=gao, is_read=False).count()

print(f'\n[统计] Gao用户的通知分布:')
print(f'  - 点赞: {like_count}条')
print(f'  - 评论: {comment_count}条')
print(f'  - 关注: {follow_count}条')
print(f'  - 系统: {system_count}条')
print(f'  - 未读: {unread_count}条')

# 显示前5条通知
print(f'\n[预览] Gao用户的前5条通知:')
gao_notifs = Notification.objects.filter(user=gao).select_related('sender', 'related_post').order_by('-created_at')[:5]
for i, notif in enumerate(gao_notifs, 1):
    sender_name = notif.sender.username if notif.sender else '系统'
    read_status = '已读' if notif.is_read else '未读'
    print(f'{i}. [{read_status}] {notif.type} - {sender_name}: {notif.content[:50]}...')

print('\n' + '=' * 60)
print('[完成] 通知转移成功！')
print('=' * 60)
