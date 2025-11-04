import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from apps.campus.models import University, School
from apps.users.models import Profile
from apps.posts.models import Post, Tag, PostLike, Bookmark
from apps.comments.models import Comment
from apps.social.models import Follow
from apps.notifications.models import Notification
from apps.opportunities.models import ExchangeProgram, Internship

print('🗑️  清空数据...')
Bookmark.objects.all().delete()
PostLike.objects.all().delete()
Comment.objects.all().delete()
Notification.objects.all().delete()
Post.objects.all().delete()
Tag.objects.all().delete()
Follow.objects.all().delete()
ExchangeProgram.objects.all().delete()
Internship.objects.all().delete()
Profile.objects.all().delete()
School.objects.all().delete()
University.objects.all().delete()
print('✅ 数据已清空！')
