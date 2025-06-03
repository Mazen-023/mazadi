"""
Management command to clean up expired price estimation cache.

This command follows Django best practices for management commands.
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db import models
from datetime import timedelta

from price_estimation.models import PriceEstimationCache


class Command(BaseCommand):
    """
    Management command to clean up expired price estimation cache entries.
    
    Usage:
        python manage.py cleanup_price_cache
        python manage.py cleanup_price_cache --days 7
        python manage.py cleanup_price_cache --all
    """
    
    help = 'Clean up expired price estimation cache entries'
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--days',
            type=int,
            default=1,
            help='Remove cache entries older than N days (default: 1)'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Remove all cache entries regardless of expiration'
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be deleted without actually deleting'
        )
    
    def handle(self, *args, **options):
        """Main command handler."""
        self.verbosity = options['verbosity']
        
        if options['all']:
            # Remove all cache entries
            queryset = PriceEstimationCache.objects.all()
            action_description = "all cache entries"
        else:
            # Remove expired entries or entries older than specified days
            cutoff_date = timezone.now() - timedelta(days=options['days'])
            queryset = PriceEstimationCache.objects.filter(
                expires_at__lt=timezone.now()
            ) | PriceEstimationCache.objects.filter(
                created_at__lt=cutoff_date
            )
            action_description = f"cache entries older than {options['days']} days or expired"
        
        count = queryset.count()
        
        if count == 0:
            self.stdout.write(
                self.style.SUCCESS('No cache entries to clean up.')
            )
            return
        
        if options['dry_run']:
            self.stdout.write(
                self.style.WARNING(
                    f'DRY RUN: Would delete {count} {action_description}'
                )
            )
            
            if self.verbosity >= 2:
                self.stdout.write('\nEntries that would be deleted:')
                for entry in queryset[:10]:  # Show first 10
                    self.stdout.write(f'  - {entry.cache_key[:50]}... (created: {entry.created_at})')
                if count > 10:
                    self.stdout.write(f'  ... and {count - 10} more entries')
        else:
            # Actually delete the entries
            deleted_count, _ = queryset.delete()
            
            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully deleted {deleted_count} {action_description}.'
                )
            )
            
            if self.verbosity >= 2:
                # Show cache statistics
                remaining_count = PriceEstimationCache.objects.count()
                total_hits = PriceEstimationCache.objects.aggregate(
                    total_hits=models.Sum('hit_count')
                )['total_hits'] or 0
                
                self.stdout.write(
                    f'\nCache statistics:\n'
                    f'  Remaining entries: {remaining_count}\n'
                    f'  Total cache hits: {total_hits}'
                )
