import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer
from apps.users.models import User

print('=' * 60)
print('第一阶段：诊断Gao用户的通知数据')
print('=' * 60)

# 1. 获取Gao用户
users_with_email = User.objects.filter(email='g0184036940@gmail.com')
user_count = users_with_email.count()

print(f'\n[INFO] 找到{user_count}个使用该邮箱的用户:')
for u in users_with_email:
    notif_count_temp = Notification.objects.filter(user=u).count()
    print(f'  - ID: {u.id}, Username: {u.username}, 通知数: {notif_count_temp}')

# 优先选择username为"Gao"的用户，如果没有则选择通知最多的
try:
    gao = users_with_email.get(username='Gao')
    print(f'\n[OK] 使用username为Gao的用户: ID {gao.id}')
except User.DoesNotExist:
    # 如果没有username为Gao的，选择通知数最多的
    gao = users_with_email.first()
    print(f'\n[WARNING] 未找到username为Gao的用户，使用第一个: {gao.username} (ID: {gao.id})')
except User.MultipleObjectsReturned:
    # 多个Gao用户，选择ID最大的（最新的）
    gao = users_with_email.filter(username='Gao').order_by('-id').first()
    print(f'\n[WARNING] 找到多个Gao用户，使用最新的: ID {gao.id}')

# 2. 查询该用户的通知数量
gao_notifications = Notification.objects.filter(user=gao).select_related('sender', 'related_post')
notif_count = gao_notifications.count()
print(f'\n[INFO] 数据库中Gao的通知数: {notif_count}条')

# 3. 显示前3条通知的详细信息
if notif_count > 0:
    print('\n[INFO] 前3条通知详情:')
    for i, notif in enumerate(gao_notifications[:3], 1):
        print(f'\n  [{i}] ID: {notif.id}')
        print(f'      类型: {notif.type}')
        print(f'      标题: {notif.title}')
        print(f'      内容: {notif.content[:60]}...' if len(notif.content) > 60 else f'      内容: {notif.content}')
        print(f'      发送者: {notif.sender.username if notif.sender else "系统"}')
        print(f'      是否已读: {"是" if notif.is_read else "否"}')
else:
    print('\n[WARNING] Gao用户没有任何通知！')

# 4. 使用序列化器序列化
serializer = NotificationSerializer(gao_notifications, many=True)
serialized_data = serializer.data
serialized_count = len(serialized_data)

print(f'\n[INFO] 序列化后的通知数: {serialized_count}条')

# 5. 检查序列化数据格式
if serialized_count > 0:
    first_notif = serialized_data[0]
    print('\n[INFO] 第一条通知的序列化数据:')
    print(json.dumps(first_notif, indent=2, ensure_ascii=False))

    # 检查关键字段
    print('\n[检查] 关键字段存在性:')
    print(f'  - message字段存在: {"message" in first_notif}')
    if "message" in first_notif:
        print(f'  - message内容: {first_notif["message"]}')
    print(f'  - notification_type字段存在: {"notification_type" in first_notif}')
    print(f'  - sender字段存在: {"sender" in first_notif}')
    print(f'  - is_read字段存在: {"is_read" in first_notif}')
    print(f'  - time_ago字段存在: {"time_ago" in first_notif}')

# 6. 按类型统计
like_count = gao_notifications.filter(type='like').count()
comment_count = gao_notifications.filter(type='comment').count()
follow_count = gao_notifications.filter(type='follow').count()
system_count = gao_notifications.filter(type='system').count()
unread_count = gao_notifications.filter(is_read=False).count()

print('\n[INFO] 按类型统计:')
print(f'  - 点赞(like): {like_count}条')
print(f'  - 评论(comment): {comment_count}条')
print(f'  - 关注(follow): {follow_count}条')
print(f'  - 系统(system): {system_count}条')
print(f'  - 未读通知: {unread_count}条')

# 7. 诊断结论
print('\n' + '=' * 60)
print('诊断结论:')
print('=' * 60)

if notif_count == 0:
    print('[问题] Gao用户没有通知数据')
    print('[建议] 执行情况A：需要转移或创建通知数据')

    # 检查其他用户的通知
    print('\n[检查] 查找其他用户的通知:')
    all_users = User.objects.all()
    for user in all_users:
        count = Notification.objects.filter(user=user).count()
        if count > 0:
            print(f'  - {user.username} ({user.email}): {count}条通知')

elif notif_count < 11:
    print(f'[问题] Gao用户只有{notif_count}条通知，期望11条')
    print('[建议] 执行情况A：需要补充通知数据')

elif notif_count == 11:
    if serialized_count != 11:
        print('[问题] 序列化数据不完整')
        print('[建议] 执行情况B：检查序列化器')
    elif "message" not in first_notif:
        print('[问题] 序列化数据缺少message字段')
        print('[建议] 执行情况B：修复序列化器')
    else:
        print('[OK] 数据和序列化都正常')
        print('[建议] 检查前端或API视图（情况C）')

        # 额外检查：验证每种类型的数量
        if like_count != 5 or comment_count != 2 or follow_count != 2 or system_count != 2:
            print(f'\n[警告] 通知类型分布不符合预期:')
            print(f'  - 点赞应为5条，实际{like_count}条')
            print(f'  - 评论应为2条，实际{comment_count}条')
            print(f'  - 关注应为2条，实际{follow_count}条')
            print(f'  - 系统应为2条，实际{system_count}条')
else:
    print(f'[警告] Gao用户有{notif_count}条通知，超过预期的11条')

print('=' * 60)
