from django.core.management.base import BaseCommand
from auctions.models import User
from accounts.models import UserProfile

class Command(BaseCommand):
    help = 'Creates UserProfile objects for existing users who do not have one'

    def handle(self, *args, **options):
        users_without_profiles = []
        
        # Find users without profiles
        for user in User.objects.all():
            try:
                # Try to access the profile
                profile = user.profile
            except UserProfile.DoesNotExist:
                # If profile doesn't exist, add user to the list
                users_without_profiles.append(user)
        
        # Create profiles for users who don't have one
        for user in users_without_profiles:
            UserProfile.objects.create(user=user)
            self.stdout.write(self.style.SUCCESS(f'Created profile for user: {user.username}'))
        
        if not users_without_profiles:
            self.stdout.write(self.style.SUCCESS('All users already have profiles'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Created {len(users_without_profiles)} user profiles'))
