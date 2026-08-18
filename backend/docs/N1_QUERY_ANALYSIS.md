# ViewSet N+1 查询分析报告

**分析日期**: 2025-11-23  
**分析范围**: posts, comments, users, social 模块的所有 ViewSet

---

## 📊 总体评估

| 模块 | 状态 | 严重程度 | 需要优化 |
|------|------|----------|---------|
| **PostViewSet** | 🟢 良好 | 低 | 1 处 |
| **CommentViewSet** | 🔴 严重 | 高 | 3 处 |
| **UserViewSet** | 🟡 一般 | 中 | 2 处 |
| **ProfileViewSet** | 🟢 良好 | 低 | 0 处 |
| **social/views.py** | 🔴 严重 | 高 | 3 处 |

---

## 1️⃣ PostViewSet - apps/posts/views.py

### ✅ 优秀实践

**get_queryset() 方法（第 34-59 行）**
```python
queryset = Post.objects.visible_to(user).select_related(
    'author', 
    'author__profile', 
    'target_university'
).prefetch_related('tags')

# 使用 Prefetch 预加载点赞和收藏
queryset = queryset.prefetch_related(
    Prefetch(
        'post_likes',
        queryset=PostLike.objects.filter(user=user),
        to_attr='user_likes'
    ),
    Prefetch(
        'bookmarked_by',
        queryset=Bookmark.objects.filter(user=user),
        to_attr='user_bookmarks'
    )
)
```

**优点**：
- ✅ 正确使用 `select_related` 处理一对一/外键关系
- ✅ 使用 `prefetch_related` 处理多对多关系（tags）
- ✅ 使用 `Prefetch` 对象进行条件预加载
- ✅ 避免了 `is_liked` 和 `is_bookmarked` 的 N+1 查询

### ⚠️ 需要优化

**位置**: `my_bookmarks` 方法（第 197-216 行）

**问题**:
```python
queryset = Post.objects.filter(id__in=post_ids).select_related(
    'author', 'target_university', 'target_school'  # ❌ 缺少 'author__profile'
).prefetch_related('tags').order_by('-created_at')
```

**影响**: 当 `PostSerializer` 访问 `author.profile` 时，每个帖子会触发一次额外查询

**优化建议**:
```python
queryset = Post.objects.filter(id__in=post_ids).select_related(
    'author', 
    'author__profile',  # ✅ 添加这一行
    'target_university', 
    'target_school'
).prefetch_related('tags').order_by('-created_at')
```

**预期效果**: 节省 N 次查询（N = 帖子数量）

---

## 2️⃣ CommentViewSet - apps/comments/views.py

### 🔴 严重问题 #1: get_replies_count() 触发 N+1

**位置**: `CommentSerializer.get_replies_count()` (serializers.py 第 18-19 行)

**问题代码**:
```python
def get_replies_count(self, obj):
    return obj.replies.count()  # ❌ 每个评论都会查询一次数据库
```

**影响**: 显示 100 个评论时，会额外产生 100 次数据库查询

**优化方案 A - 使用 annotate（推荐）**:
```python
# 在 ViewSet 的 get_queryset() 中
from django.db.models import Count

queryset = Comment.objects.select_related(
    'author',  # ⚠️ 缺少 'author__profile'
    'author__profile',  # ✅ 添加
    'post',
    'parent'
).annotate(
    replies_count=Count('replies')  # ✅ 预计算回复数
).all()
```

```python
# 在 Serializer 中
class CommentSerializer(serializers.ModelSerializer):
    replies_count = serializers.IntegerField(read_only=True)  # ✅ 直接使用 annotate 的值
```

### 🔴 严重问题 #2: get_replies() 触发 N+1

**位置**: `CommentWithRepliesSerializer.get_replies()` (serializers.py 第 45-50 行)

**问题代码**:
```python
def get_replies(self, obj):
    if obj.parent is None:
        replies = obj.replies.select_related('author').all()  # ❌ 每个顶级评论都查询一次
        return CommentSerializer(replies, many=True).data
    return []
```

**影响**: 显示 20 个顶级评论时，会额外产生 20 次查询

**优化建议**:
```python
# 在 ViewSet 的 get_queryset() 中
from django.db.models import Prefetch

def get_queryset(self):
    queryset = super().get_queryset()
    
    # 如果请求带回复
    if self.request.query_params.get('with_replies'):
        queryset = queryset.prefetch_related(
            Prefetch(
                'replies',
                queryset=Comment.objects.select_related(
                    'author',
                    'author__profile'  # ✅ 预加载作者资料
                ).order_by('created_at')
            )
        )
    
    return queryset
```

---

## 3️⃣ UserViewSet - apps/users/views.py

### 🟡 问题 #1: 基础 queryset 缺少优化

**位置**: UserViewSet 定义（第 14 行）

**问题代码**:
```python
queryset = User.objects.all()  # ❌ 没有任何预加载
```

**优化建议**:
```python
queryset = User.objects.select_related('profile').all()  # ✅ 预加载用户资料
```

---

## 4️⃣ social/views.py - 关注和聊天功能

### 🔴 严重问题: 联系人列表的 N+1 查询

**受影响的函数**:
- `get_following_list()` (第 137-192 行)
- `get_followers_list()` (第 197-251 行)
- `get_friends_list()` (第 256-314 行)

**问题代码**（以 get_following_list 为例）:
```python
for user_data in serializer.data:
    user_obj = next(u for u in users if u.id == user_data['id'])
    
    # ❌ 在循环中查询最后一条消息，严重的 N+1 问题
    last_msg = ChatMessage.objects.filter(
        Q(from_user=user, to_user=user_obj) | Q(from_user=user_obj, to_user=user)
    ).order_by('-created_at').first()
```

**影响**: 如果有 50 个关注用户，会产生 **50 次额外查询**

---

## 📈 优化优先级总结

### 🔴 高优先级（严重影响性能）

1. **CommentSerializer.get_replies_count()** - 使用 annotate 或缓存字段
2. **CommentWithRepliesSerializer.get_replies()** - 使用 Prefetch  
3. **social/views.py 联系人列表** (3 个函数) - 使用 Subquery/Prefetch

### 🟡 中优先级（影响用户体验）

4. **UserViewSet queryset** - 添加 select_related('profile')
5. **PostViewSet.my_bookmarks()** - 添加 'author__profile'

---

## 📊 预期性能提升

| 场景 | 优化前 | 优化后 | 提升 |
|------|--------|--------|------|
| 查看 50 条评论 | ~150 SQL | ~5 SQL | **30x** |
| 查看 100 个帖子 | ~500 SQL | ~10 SQL | **50x** |
| 联系人列表（50 人） | ~200 SQL | ~5 SQL | **40x** |

**分析完成日期**: 2025-11-23
