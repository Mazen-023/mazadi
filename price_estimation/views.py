"""
Views for price estimation functionality following Django best practices.
"""

import json
import logging
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from auctions.models import Auction
from .models import PriceEstimation
from .services.price_estimator_service import PriceEstimatorService
from .estimators.base import PriceEstimationError

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
def estimate_price_ajax(request):
    """
    AJAX endpoint for real-time price estimation.

    Expected POST data:
    - name: Product name
    - description: Product description
    - auction_id: (optional) Auction ID if updating existing auction
    """
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        auction_id = data.get('auction_id')

        if not name or not description:
            return JsonResponse({
                'success': False,
                'error': 'Product name and description are required.'
            }, status=400)

        # Initialize price estimator service
        estimator = PriceEstimatorService()

        # Get price estimation
        result = estimator.estimate_price(name, description)

        # If auction_id is provided, save the estimation
        if auction_id:
            try:
                auction = get_object_or_404(Auction, id=auction_id, user=request.user)
                _save_price_estimation(auction, result, request.user)
            except Exception as e:
                logger.error(f"Failed to save price estimation for auction {auction_id}: {str(e)}")

        # Prepare response
        response_data = {
            'success': True,
            'estimated_price': result['estimated_price'],
            'amazon_price': result['amazon_price'],
            'dubizzle_price': result['dubizzle_price'],
            'sources_used': result['sources_used'],
            'estimation_date': result['estimation_date'].isoformat(),
            'cached': result.get('cached', False),
        }

        if result['errors']:
            response_data['warnings'] = result['errors']

        return JsonResponse(response_data)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data.'
        }, status=400)
    except PriceEstimationError as e:
        logger.error(f"Price estimation error: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': f'Price estimation failed: {str(e)}'
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error in price estimation: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred. Please try again.'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def update_auction_price_estimate(request, auction_id):
    """
    Update price estimate for a specific auction.
    """
    try:
        auction = get_object_or_404(Auction, id=auction_id, user=request.user)

        # Initialize price estimator service
        estimator = PriceEstimatorService()

        # Get price estimation
        result = estimator.estimate_price(auction.title, auction.description)

        # Save the estimation
        _save_price_estimation(auction, result, request.user)

        if result['estimated_price']:
            messages.success(
                request,
                f"Price estimate updated: {result['estimated_price']} EGP "
                f"(Sources: {', '.join(result['sources_used'])})"
            )
        else:
            messages.warning(
                request,
                "Could not estimate price from available sources. Please try again later."
            )

        return JsonResponse({
            'success': True,
            'estimated_price': result['estimated_price'],
            'sources_used': result['sources_used'],
        })

    except PriceEstimationError as e:
        logger.error(f"Price estimation error for auction {auction_id}: {str(e)}")
        messages.error(request, f"Price estimation failed: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
    except Exception as e:
        logger.error(f"Unexpected error updating price estimate for auction {auction_id}: {str(e)}")
        messages.error(request, "An unexpected error occurred. Please try again.")
        return JsonResponse({
            'success': False,
            'error': 'An unexpected error occurred.'
        }, status=500)


@login_required
def get_price_estimation_history(request, auction_id):
    """
    Get price estimation history for an auction.
    """
    try:
        auction = get_object_or_404(Auction, id=auction_id, user=request.user)

        estimations = PriceEstimation.objects.filter(auction=auction).order_by('-created_at')[:10]

        history_data = []
        for estimation in estimations:
            history_data.append({
                'id': estimation.id,
                'estimated_price': float(estimation.estimated_price) if estimation.estimated_price else None,
                'amazon_price': float(estimation.amazon_price) if estimation.amazon_price else None,
                'dubizzle_price': float(estimation.dubizzle_price) if estimation.dubizzle_price else None,
                'sources_used': estimation.sources_used,
                'created_at': estimation.created_at.isoformat(),
                'sources_display': estimation.sources_display,
                'success_rate': estimation.success_rate,
                'has_errors': estimation.has_errors,
            })

        return JsonResponse({
            'success': True,
            'history': history_data,
            'auction_title': auction.title,
        })

    except Exception as e:
        logger.error(f"Error getting price estimation history for auction {auction_id}: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to retrieve price estimation history.'
        }, status=500)


@login_required
def suggest_price_range(request):
    """
    Suggest price range based on category and condition.
    """
    try:
        category = request.GET.get('category')
        condition = request.GET.get('condition', 'new')

        if not category:
            return JsonResponse({
                'success': False,
                'error': 'Category is required.'
            }, status=400)

        # Get recent price estimations for the same category
        recent_estimations = PriceEstimation.objects.filter(
            auction__category=category,
            estimated_price__isnull=False,
            auction__is_close=False
        ).order_by('-created_at')[:20]

        if not recent_estimations:
            return JsonResponse({
                'success': True,
                'message': 'No recent price data available for this category.',
                'suggested_range': None
            })

        # Calculate price statistics
        prices = [float(estimation.estimated_price) for estimation in recent_estimations]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = sum(prices) / len(prices)

        # Adjust for condition
        if condition.lower() in ['used', 'مستعمل']:
            min_price *= 0.6
            max_price *= 0.8
            avg_price *= 0.7

        return JsonResponse({
            'success': True,
            'suggested_range': {
                'min_price': round(min_price, 2),
                'max_price': round(max_price, 2),
                'avg_price': round(avg_price, 2),
                'sample_size': len(prices)
            }
        })

    except Exception as e:
        logger.error(f"Error suggesting price range: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'Failed to suggest price range.'
        }, status=500)


def _save_price_estimation(auction, estimation_result, user):
    """
    Save price estimation result to the database.

    Args:
        auction: Auction instance
        estimation_result: Dictionary containing estimation results
        user: User who requested the estimation
    """
    try:
        # Update auction fields
        if estimation_result['estimated_price']:
            auction.estimated_price = Decimal(str(estimation_result['estimated_price']))
            auction.price_estimation_date = timezone.now()
            auction.price_estimation_sources = estimation_result['sources_used']
            auction.save(update_fields=['estimated_price', 'price_estimation_date', 'price_estimation_sources'])

        # Create detailed price estimation record
        price_estimation = PriceEstimation.objects.create(
            auction=auction,
            estimated_price=Decimal(str(estimation_result['estimated_price'])) if estimation_result['estimated_price'] else None,
            amazon_price=Decimal(str(estimation_result['amazon_price'])) if estimation_result['amazon_price'] else None,
            dubizzle_price=Decimal(str(estimation_result['dubizzle_price'])) if estimation_result['dubizzle_price'] else None,
            sources_used=estimation_result['sources_used'],
            estimation_errors=estimation_result.get('errors', []),
            requested_by=user,
            estimation_metadata={
                'cached': estimation_result.get('cached', False),
                'estimation_date': estimation_result['estimation_date'].isoformat(),
            }
        )

        logger.info(f"Saved price estimation for auction {auction.id}: {estimation_result['estimated_price']}")
        return price_estimation

    except Exception as e:
        logger.error(f"Failed to save price estimation for auction {auction.id}: {str(e)}")
        raise
