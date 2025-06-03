"""
Management command to estimate prices for auctions.

This command follows Django best practices for management commands.
"""

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from datetime import timedelta

from auctions.models import Auction
from price_estimation.models import PriceEstimation
from price_estimation.services import PriceEstimatorService, PriceEstimationError


class Command(BaseCommand):
    """
    Management command to estimate prices for auctions.
    
    Usage:
        python manage.py estimate_auction_prices
        python manage.py estimate_auction_prices --auction-id 123
        python manage.py estimate_auction_prices --category laptops
        python manage.py estimate_auction_prices --force-update
    """
    
    help = 'Estimate prices for auctions using external sources'
    
    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            '--auction-id',
            type=int,
            help='Estimate price for a specific auction ID'
        )
        parser.add_argument(
            '--category',
            type=str,
            help='Estimate prices for auctions in a specific category'
        )
        parser.add_argument(
            '--force-update',
            action='store_true',
            help='Force update even if auction already has recent price estimation'
        )
        parser.add_argument(
            '--max-auctions',
            type=int,
            default=50,
            help='Maximum number of auctions to process (default: 50)'
        )
        parser.add_argument(
            '--days-threshold',
            type=int,
            default=7,
            help='Only update auctions without price estimation in the last N days (default: 7)'
        )
    
    def handle(self, *args, **options):
        """Main command handler."""
        self.verbosity = options['verbosity']
        
        try:
            # Get auctions to process
            auctions = self._get_auctions_to_process(options)
            
            if not auctions.exists():
                self.stdout.write(
                    self.style.WARNING('No auctions found matching the criteria.')
                )
                return
            
            # Initialize price estimator
            estimator = PriceEstimatorService()
            
            # Process auctions
            processed_count = 0
            success_count = 0
            error_count = 0
            
            for auction in auctions[:options['max_auctions']]:
                try:
                    with transaction.atomic():
                        result = self._estimate_auction_price(auction, estimator)
                        if result:
                            success_count += 1
                            if self.verbosity >= 2:
                                self.stdout.write(
                                    self.style.SUCCESS(
                                        f'✓ Estimated price for "{auction.title}": '
                                        f'{result.estimated_price} EGP'
                                    )
                                )
                        else:
                            error_count += 1
                            if self.verbosity >= 2:
                                self.stdout.write(
                                    self.style.ERROR(
                                        f'✗ Failed to estimate price for "{auction.title}"'
                                    )
                                )
                    
                    processed_count += 1
                    
                except Exception as e:
                    error_count += 1
                    if self.verbosity >= 1:
                        self.stdout.write(
                            self.style.ERROR(
                                f'Error processing auction "{auction.title}": {str(e)}'
                            )
                        )
            
            # Print summary
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nPrice estimation completed:\n'
                    f'  Processed: {processed_count} auctions\n'
                    f'  Successful: {success_count}\n'
                    f'  Failed: {error_count}'
                )
            )
            
        except CommandError:
            raise
        except Exception as e:
            raise CommandError(f'Command failed: {str(e)}')
    
    def _get_auctions_to_process(self, options):
        """Get queryset of auctions to process based on options."""
        queryset = Auction.objects.filter(is_close=False)
        
        # Filter by auction ID
        if options['auction_id']:
            queryset = queryset.filter(id=options['auction_id'])
            if not queryset.exists():
                raise CommandError(f'Auction with ID {options["auction_id"]} not found.')
        
        # Filter by category
        if options['category']:
            queryset = queryset.filter(category=options['category'])
            if not queryset.exists():
                raise CommandError(f'No auctions found in category "{options["category"]}".')
        
        # Filter by recent price estimations unless force update
        if not options['force_update']:
            threshold_date = timezone.now() - timedelta(days=options['days_threshold'])
            
            # Exclude auctions that have recent price estimations
            recent_estimation_auction_ids = PriceEstimation.objects.filter(
                created_at__gte=threshold_date
            ).values_list('auction_id', flat=True)
            
            queryset = queryset.exclude(id__in=recent_estimation_auction_ids)
        
        return queryset.order_by('-created_at')
    
    def _estimate_auction_price(self, auction, estimator):
        """Estimate price for a single auction."""
        try:
            # Get price estimation
            result = estimator.estimate_price(auction.title, auction.description)
            
            if not result['estimated_price']:
                if self.verbosity >= 2:
                    self.stdout.write(
                        self.style.WARNING(
                            f'No price estimate available for "{auction.title}". '
                            f'Errors: {", ".join(result["errors"])}'
                        )
                    )
                return None
            
            # Create price estimation record
            price_estimation = PriceEstimation.objects.create(
                auction=auction,
                estimated_price=result['estimated_price'],
                amazon_price=result['amazon_price'],
                dubizzle_price=result['dubizzle_price'],
                sources_used=result['sources_used'],
                estimation_errors=result.get('errors', []),
                estimation_metadata={
                    'command_run': True,
                    'estimation_date': result['estimation_date'].isoformat(),
                    'cached': result.get('cached', False),
                }
            )
            
            return price_estimation
            
        except PriceEstimationError as e:
            if self.verbosity >= 1:
                self.stdout.write(
                    self.style.ERROR(
                        f'Price estimation error for "{auction.title}": {str(e)}'
                    )
                )
            return None
        except Exception as e:
            if self.verbosity >= 1:
                self.stdout.write(
                    self.style.ERROR(
                        f'Unexpected error for "{auction.title}": {str(e)}'
                    )
                )
            return None
