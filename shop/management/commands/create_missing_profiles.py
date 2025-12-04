from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from shop.models import Profile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create profiles for users who dont have one'

    def handle(self, *args, **options):
        users_without_profile = User.objects.filter(profile__isnull=True)
        count = 0
        
        for user in users_without_profile:
            Profile.objects.create(user=user)
            count += 1
        
        self.stdout.write(self.style.SUCCESS(f'Created {count} profiles'))
