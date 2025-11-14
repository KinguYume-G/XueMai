import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.notifications.models import Notification
from apps.notifications.serializers import NotificationSerializer
from apps.users.models import User

print('=' * 60)
print('第三阶段：验证Gao用户的通知数据和序列化')
print('=' * 60)

# 获取Gao用户
gao = User.objects.get(id=12)
print(f'\n[用户] {gao.username} (ID: {gao.id}, {gao.email})')

# 查询通知
notifications = Notification.objects.filter(user=gao).select_related('sender', 'related_post').order_by('-created_at')
total_count = notifications.count()

print(f'\n[数据] 总通知数: {total_count}条')

# 按类型统计
like_count = notifications.filter(type='like').count()
comment_count = notifications.filter(type='comment').count()
follow_count = notifications.filter(type='follow').count()
system_count = notifications.filter(type='system').count()
unread_count = notifications.filter(is_read=False).count()

print(f'[数据] 类型分布:')
print(f'  - 点赞: {like_count}条 (期望5条) {"[OK]" if like_count == 5 else "[FAIL]"}')
print(f'  - 评论: {comment_count}条 (期望2条) {"[OK]" if comment_count == 2 else "[FAIL]"}')
print(f'  - 关注: {follow_count}条 (期望2条) {"[OK]" if follow_count == 2 else "[FAIL]"}')
print(f'  - 系统: {system_count}条 (期望2条) {"[OK]" if system_count == 2 else "[FAIL]"}')
print(f'  - 未读: {unread_count}条')

# 测试序列化
print(f'\n[序列化] 测试序列化器...')
serializer = NotificationSerializer(notifications, many=True)
serialized_data = serializer.data
serialized_count = len(serialized_data)

print(f'[序列化] 序列化后数量: {serialized_count}条 {"[OK]" if serialized_count == total_count else "[FAIL]"}')

# 检查前2条序列化数据
if serialized_count >= 2:
    print(f'\n[序列化] 前2条通知的序列化数据:')
    for i in range(min(2, serialized_count)):
        print(f'\n--- 通知 {i+1} ---')
        notif_data = serialized_data[i]
        print(json.dumps(notif_data, indent=2, ensure_ascii=False))

        # 验证关键字段
        print(f'\n[验证] 关键字段检查:')
        print(f'  - id字段: {notif_data.get("id")}')
        print(f'  - type字段: {notif_data.get("type")}')
        print(f'  - notification_type字段: {notif_data.get("notification_type")}')
        print(f'  - message字段存在: {"message" in notif_data} [OK]' if "message" in notif_data else '  - message字段存在: False [FAIL]')
        if "message" in notif_data:
            print(f'  - message内容: {notif_data["message"]}')
        print(f'  - sender字段存在: {"sender" in notif_data}')
        print(f'  - is_read字段: {notif_data.get("is_read")}')
        print(f'  - time_ago字段: {notif_data.get("time_ago")}')

# 总结
print(f'\n' + '=' * 60)
print('[总结] 验证结果:')
print('=' * 60)

all_checks_passed = (
    total_count == 11 and
    like_count == 5 and
    comment_count == 2 and
    follow_count == 2 and
    system_count == 2 and
    serialized_count == total_count and
    ("message" in serialized_data[0] if serialized_data else False)
)

if all_checks_passed:
    print('[OK] 所有检查通过！')
    print('[OK] 数据完整且正确')
    print('[OK] 序列化器工作正常')
    print('[OK] Gao用户可以查看所有通知')
else:
    print('[FAIL] 部分检查未通过，请查看上方详情')

print('=' * 60)
