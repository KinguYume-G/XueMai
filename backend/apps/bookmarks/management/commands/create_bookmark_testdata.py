from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.bookmarks.models import Bookmark
from apps.posts.models import Post
from apps.opportunities.models import ExchangeProgram, Internship
from apps.communities.models import Community

User = get_user_model()


class Command(BaseCommand):
    help = 'Create bookmark test data'

    def handle(self, *args, **options):
        # Get first user or create test user
        user = User.objects.first()
        if not user:
            self.stdout.write(self.style.ERROR('No user found. Please create a user first.'))
            return

        self.stdout.write(f'Creating bookmarks for user: {user.username}')

        # Clear existing bookmarks for this user
        Bookmark.objects.filter(user=user).delete()

        created_count = 0

        # Bookmark 2 posts
        posts = Post.objects.all()[:2]
        for post in posts:
            Bookmark.objects.get_or_create(
                user=user,
                content_type='post',
                object_id=post.id
            )
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'  - Bookmarked post: {post.title}'))

        # Bookmark 2 exchange programs
        exchanges = ExchangeProgram.objects.all()[:2]
        for exchange in exchanges:
            Bookmark.objects.get_or_create(
                user=user,
                content_type='exchange',
                object_id=exchange.id
            )
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'  - Bookmarked exchange: {exchange.title}'))

        # Bookmark 2 internships
        internships = Internship.objects.all()[:2]
        for internship in internships:
            Bookmark.objects.get_or_create(
                user=user,
                content_type='internship',
                object_id=internship.id
            )
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'  - Bookmarked internship: {internship.title}'))

        # Bookmark 2 communities
        communities = Community.objects.all()[:2]
        for community in communities:
            Bookmark.objects.get_or_create(
                user=user,
                content_type='community',
                object_id=community.id
            )
            created_count += 1
            self.stdout.write(self.style.SUCCESS(f'  - Bookmarked community: {community.name}'))

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully created {created_count} bookmarks!'))
