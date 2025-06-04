# Price Estimation App

A Django app for estimating product prices by scraping Amazon Egypt and Dubizzle Egypt. This app follows Django best practices and integrates seamlessly with the auction platform.

## Features

- **Multi-source price estimation**: Scrapes Amazon Egypt and Dubizzle Egypt
- **Real prices only**: No hardcoded or fallback pricing - only actual scraped prices
- **Intelligent caching**: Avoids repeated API calls with database-backed caching
- **Similarity matching**: Uses text similarity to find relevant products on Dubizzle
- **Condition-aware pricing**: Applies discounts for used items
- **Comprehensive admin interface**: Full admin support with custom actions
- **Management commands**: CLI tools for bulk operations
- **RESTful API**: AJAX endpoints for real-time price estimation
- **Clear error messaging**: Transparent feedback when no prices are found

## Installation

1. **Install dependencies**:
   ```bash
   pip install requests beautifulsoup4 selenium webdriver-manager
   ```

2. **Add to INSTALLED_APPS** in `settings.py`:
   ```python
   INSTALLED_APPS = [
       # ... other apps
       'price_estimation',
   ]
   ```

3. **Include URLs** in main `urls.py`:
   ```python
   urlpatterns = [
       # ... other patterns
       path("price-estimation/", include("price_estimation.urls")),
   ]
   ```

4. **Run migrations**:
   ```bash
   python manage.py makemigrations price_estimation
   python manage.py migrate
   ```

## Usage

### Basic Price Estimation

```python
from price_estimation.services import PriceEstimatorService

# Initialize the service
estimator = PriceEstimatorService()

# Estimate price
result = estimator.estimate_price("iPhone 15", "128GB excellent condition")

print(f"Estimated price: {result['estimated_price']} EGP")
print(f"Amazon price: {result['amazon_price']} EGP")
print(f"Dubizzle price: {result['dubizzle_price']} EGP")
print(f"Sources used: {result['sources_used']}")
```

### AJAX Integration

Include the price estimation widget in your auction creation form:

```html
<!-- In your auction creation template -->
{% include 'price_estimation/price_estimate_widget.html' %}
```

### Management Commands

**Estimate prices for auctions**:
```bash
# Estimate prices for all auctions without recent estimates
python manage.py estimate_auction_prices

# Estimate price for a specific auction
python manage.py estimate_auction_prices --auction-id 123

# Estimate prices for a specific category
python manage.py estimate_auction_prices --category laptops

# Force update even if recent estimates exist
python manage.py estimate_auction_prices --force-update
```

**Clean up expired cache**:
```bash
# Remove expired cache entries
python manage.py cleanup_price_cache

# Remove cache entries older than 7 days
python manage.py cleanup_price_cache --days 7

# Remove all cache entries
python manage.py cleanup_price_cache --all
```

## API Endpoints

### Estimate Price (AJAX)
- **URL**: `/price-estimation/estimate/`
- **Method**: `POST`
- **Auth**: Required (login_required)
- **Data**:
  ```json
  {
    "name": "iPhone 15",
    "description": "128GB excellent condition",
    "auction_id": 123  // optional
  }
  ```
- **Response**:
  ```json
  {
    "success": true,
    "estimated_price": 25000.0,
    "amazon_price": 26000.0,
    "dubizzle_price": 24000.0,
    "sources_used": ["amazon", "dubizzle"],
    "estimation_date": "2024-01-01T00:00:00Z",
    "cached": false
  }
  ```

### Update Auction Estimate
- **URL**: `/price-estimation/auction/<int:auction_id>/update/`
- **Method**: `POST`
- **Auth**: Required (auction owner only)

### Get Estimation History
- **URL**: `/price-estimation/auction/<int:auction_id>/history/`
- **Method**: `GET`
- **Auth**: Required (auction owner only)

### Suggest Price Range
- **URL**: `/price-estimation/suggest-range/?category=laptops&condition=new`
- **Method**: `GET`
- **Auth**: Required

## Models

### PriceEstimation
Stores detailed price estimation history for auctions.

**Fields**:
- `auction`: ForeignKey to Auction
- `estimated_price`: Final estimated price
- `amazon_price`: Price from Amazon Egypt
- `dubizzle_price`: Price from Dubizzle Egypt
- `sources_used`: JSON list of successful sources
- `estimation_errors`: JSON list of errors encountered
- `requested_by`: User who requested the estimation
- `created_at`, `updated_at`: Timestamps

### PriceEstimationCache
Caches price estimation results to avoid repeated API calls.

**Fields**:
- `cache_key`: Unique key based on product name/description
- `estimated_price`, `amazon_price`, `dubizzle_price`: Cached prices
- `expires_at`: Cache expiration timestamp
- `hit_count`: Number of times cache was used

## Configuration

### Chrome WebDriver
The app uses Chrome WebDriver for Amazon scraping. The `webdriver-manager` package automatically downloads and manages the driver.

### Caching
- **Default cache timeout**: 1 hour (3600 seconds)
- **Cache cleanup**: Use management command or admin actions
- **Database-backed**: Uses Django models for persistent caching

### Error Handling
- **Graceful degradation**: Works with partial data if some sources fail
- **Retry logic**: Built into individual estimators
- **Comprehensive logging**: All errors are logged for debugging

## Best Practices

1. **Use caching**: Enable caching to avoid hitting external APIs repeatedly
2. **Run in background**: Use Celery for bulk price estimations
3. **Monitor rate limits**: Be respectful of external site rate limits
4. **Regular cleanup**: Schedule cache cleanup to manage database size
5. **Error monitoring**: Monitor logs for estimation failures

## Architecture

The app follows Django best practices:

- **Service layer**: Business logic separated from views
- **DRY principle**: Shared functionality in base classes
- **Dependency injection**: Estimators are pluggable
- **Proper error handling**: Custom exceptions and graceful degradation
- **Comprehensive testing**: Unit tests for all components
- **Admin integration**: Full admin interface with custom actions

## Extending

To add new price sources:

1. Create a new estimator class inheriting from `BasePriceEstimator`
2. Implement the `estimate_price` method
3. Add to `PriceEstimatorService.estimators` dictionary
4. Update models to include new source fields if needed

Example:
```python
class NewSourceEstimator(BasePriceEstimator):
    def estimate_price(self, name: str, description: str) -> Union[float, str]:
        # Implementation here
        pass
```

## Troubleshooting

**Chrome WebDriver issues**:
- Ensure Chrome browser is installed
- Check firewall/antivirus settings
- Try updating Chrome and webdriver-manager

**Scraping failures**:
- Check internet connection
- Verify target sites are accessible
- Review rate limiting policies

**Performance issues**:
- Enable caching
- Use background tasks for bulk operations
- Monitor database query performance
