# apps/users/services.py
from django.core.cache import cache

from .models import User


class UserService:
    """用户业务逻辑（保持View层简洁）"""

    @staticmethod
    def follow_user(follower: User, followee: User) -> dict:
        """关注用户的业务逻辑"""
        if follower == followee:
            raise ValueError("不能关注自己")

        # 创建关注关系
        # ... 业务逻辑

        # 清除缓存
        cache.delete(f"user_following_{follower.id}")

        return {"message": "关注成功", "status": "success"}
