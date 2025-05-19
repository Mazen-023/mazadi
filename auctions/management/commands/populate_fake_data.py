import os
import random
import requests
from io import BytesIO
from decimal import Decimal
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from django.utils import timezone
from auctions.models import Auction, Bid, Comment, Watchlist, CATEGORY_CHOICES
from accounts.models import Rating, UserProfile
from django.conf import settings

User = get_user_model()

# Sample user data
USERS = [
    {
        'username': 'john_doe',
        'email': 'john@example.com',
        'password': 'password123',
        'first_name': 'John',
        'last_name': 'Doe',
        'bio': 'Tech enthusiast and collector of vintage electronics.',
        'profile_pic': 'https://randomuser.me/api/portraits/men/1.jpg'
    },
    {
        'username': 'jane_smith',
        'email': 'jane@example.com',
        'password': 'password123',
        'first_name': 'Jane',
        'last_name': 'Smith',
        'bio': 'Professional photographer and gadget lover.',
        'profile_pic': 'https://randomuser.me/api/portraits/women/2.jpg'
    },
    {
        'username': 'mike_johnson',
        'email': 'mike@example.com',
        'password': 'password123',
        'first_name': 'Mike',
        'last_name': 'Johnson',
        'bio': 'Software developer with a passion for the latest tech.',
        'profile_pic': 'https://randomuser.me/api/portraits/men/3.jpg'
    },
    {
        'username': 'sarah_williams',
        'email': 'sarah@example.com',
        'password': 'password123',
        'first_name': 'Sarah',
        'last_name': 'Williams',
        'bio': 'IT consultant specializing in consumer electronics.',
        'profile_pic': 'https://randomuser.me/api/portraits/women/4.jpg'
    },
    {
        'username': 'david_brown',
        'email': 'david@example.com',
        'password': 'password123',
        'first_name': 'David',
        'last_name': 'Brown',
        'bio': 'Electronics retailer with 10+ years of experience.',
        'profile_pic': 'https://randomuser.me/api/portraits/men/5.jpg'
    }
]

# Sample electronics data
ELECTRONICS_DATA = {
    'laptops': [
        {
            'title': 'MacBook Pro 16" (2023)',
            'description': 'Apple M2 Pro chip, 16GB RAM, 1TB SSD, 16-inch Liquid Retina XDR display. Perfect for creative professionals and developers. Includes charger and original box.',
            'price': Decimal('1899.99'),
            'image_url': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp16-spacegray-select-202301?wid=904&hei=840&fmt=jpeg&qlt=90&.v=1671304673202'
        },
        {
            'title': 'Dell XPS 15 (2023)',
            'description': 'Premium laptop with 15.6" OLED display, Intel Core i7-12700H, 16GB RAM, 1TB SSD, NVIDIA RTX 3050 Ti, Windows 11 Pro. Perfect for professionals and content creators.',
            'price': Decimal('1499.99'),
            'image_url': 'https://i.dell.com/is/image/DellContent/content/dam/ss2/product-images/dell-client-products/notebooks/xps-notebooks/xps-15-9530/media-gallery/black/notebook-xps-15-9530-t-black-gallery-1.psd?fmt=png-alpha&pscan=auto&scl=1&hei=402&wid=402&qlt=100,1&resMode=sharp2&size=402,402&chrss=full'
        },
        {
            'title': 'Lenovo ThinkPad X1 Carbon',
            'description': 'Business laptop with 14" WQUXGA display, Intel Core i7-1270P, 32GB RAM, 1TB SSD, Windows 11 Pro. Military-grade durability and excellent keyboard.',
            'price': Decimal('1299.99'),
            'image_url': 'https://p1-ofp.static.pub/medias/bWFzdGVyfHJvb3R8MjM5NTI0fGltYWdlL3BuZ3xoMDgvaGQ5LzE0MzU1NDE5NTc4Mzk4LnBuZ3w0ZjFkNWJiYmQ5OTcwZjZhZTllYTQ2ZWE2YjU0ZDY3YjlmMGJlZWEzMGEyZjkxMjZkOGJhZGMwZDZhNTc5NzA0/lenovo-laptop-thinkpad-x1-carbon-gen-10-14-hero.png'
        },
        {
            'title': 'ASUS ROG Zephyrus G14',
            'description': 'Gaming laptop with 14" QHD display, AMD Ryzen 9 7940HS, 16GB RAM, 1TB SSD, NVIDIA RTX 4060, Windows 11 Home. Compact powerhouse for gaming on the go.',
            'price': Decimal('1599.99'),
            'image_url': 'https://dlcdnwebimgs.asus.com/gain/C97AE94C-346D-4301-A10D-B3F395A1D453/w1000/h732'
        },
        {
            'title': 'HP Spectre x360 14',
            'description': 'Convertible laptop with 13.5" OLED display, Intel Core i7-1255U, 16GB RAM, 1TB SSD, Intel Iris Xe Graphics, Windows 11 Home. Elegant design with 360-degree hinge.',
            'price': Decimal('1399.99'),
            'image_url': 'https://ssl-product-images.www8-hp.com/digmedialib/prodimg/lowres/c08164339.png'
        }
    ],
    'smartphones': [
        {
            'title': 'iPhone 15 Pro Max',
            'description': 'Apple\'s flagship smartphone with 6.7" Super Retina XDR display, A17 Pro chip, 8GB RAM, 256GB storage, 48MP triple camera system, iOS 17. Premium build with titanium frame.',
            'price': Decimal('1199.99'),
            'image_url': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-15-pro-finish-select-202309-6-7inch-naturaltitanium?wid=5120&hei=2880&fmt=p-jpg&qlt=80&.v=1692845702708'
        },
        {
            'title': 'Samsung Galaxy S23 Ultra',
            'description': 'Flagship smartphone with 6.8" Dynamic AMOLED 2X display, Snapdragon 8 Gen 2, 12GB RAM, 256GB storage, 200MP main camera, 5000mAh battery, Android 13. Ultimate performance and photography.',
            'price': Decimal('1099.99'),
            'image_url': 'https://images.samsung.com/is/image/samsung/p6pim/levant/2302/gallery/levant-galaxy-s23-ultra-s918-sm-s918bzkcmea-534859389'
        },
        {
            'title': 'Google Pixel 8 Pro',
            'description': 'Google\'s premium smartphone with 6.7" LTPO OLED display, Google Tensor G3, 12GB RAM, 128GB storage, 50MP triple camera, 5000mAh battery, Android 14. Computational photography excellence.',
            'price': Decimal('999.99'),
            'image_url': 'https://lh3.googleusercontent.com/zyAJlZnfSVRhQyDNYpRZVvEkCKCZAGNqYMD9JcH2Xk-0JUfPjPh7jnXHsM1CQ_TQjGZ4v2BGP9zuYdB_ZmMBtVDHQnXKk3uqyQKj=w1000-rw'
        },
        {
            'title': 'OnePlus 12',
            'description': 'Flagship killer with 6.82" LTPO AMOLED display, Snapdragon 8 Gen 3, 12GB RAM, 256GB storage, 50MP triple Hasselblad camera, 5400mAh battery, OxygenOS 14. Fast charging and smooth performance.',
            'price': Decimal('899.99'),
            'image_url': 'https://oasis.opstatics.com/content/dam/oasis/page/2023/12-series/spec-image/Flowy%20Emerald-gallery.png'
        },
        {
            'title': 'Xiaomi 14 Ultra',
            'description': 'Photography powerhouse with 6.73" LTPO AMOLED display, Snapdragon 8 Gen 3, 16GB RAM, 512GB storage, 50MP quad Leica camera, 5000mAh battery, MIUI 15. Professional camera experience.',
            'price': Decimal('1099.99'),
            'image_url': 'https://i02.appmifile.com/324_operator_sg/10/03/2024/d7bce7b9c9a5d6f2a3a6b3d0a1e7c3e2.png'
        }
    ],
    'audio': [
        {
            'title': 'Sony WH-1000XM5',
            'description': 'Premium noise-cancelling headphones with 30-hour battery life, LDAC support, adaptive sound control, and multipoint connection. Industry-leading noise cancellation and sound quality.',
            'price': Decimal('399.99'),
            'image_url': 'https://www.sony.com/image/5d02da5df552836db894cead8a68f5f3?fmt=png-alpha&wid=660&hei=660'
        },
        {
            'title': 'Apple AirPods Pro 2',
            'description': 'Wireless earbuds with active noise cancellation, transparency mode, spatial audio, H2 chip, and MagSafe charging case. Perfect for Apple ecosystem users.',
            'price': Decimal('249.99'),
            'image_url': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/MQD83?wid=1144&hei=1144&fmt=jpeg&qlt=90&.v=1660803972361'
        },
        {
            'title': 'Bose QuietComfort Ultra',
            'description': 'Premium headphones with immersive audio, CustomTune technology, 24-hour battery life, and advanced noise cancellation. Exceptional comfort for long listening sessions.',
            'price': Decimal('429.99'),
            'image_url': 'https://assets.bose.com/content/dam/cloudassets/Bose_DAM/Web/consumer_electronics/global/products/headphones/qc_ultra_headphones/product_silo_images/QCU_HP_BLK_hero_010_RGB.png/jcr:content/renditions/cq5dam.web.1280.1280.png'
        },
        {
            'title': 'Sennheiser Momentum 4 Wireless',
            'description': 'Premium headphones with 60-hour battery life, adaptive noise cancellation, and high-resolution audio. Exceptional sound quality and comfort for audiophiles.',
            'price': Decimal('349.99'),
            'image_url': 'https://assets.sennheiser.com/img/25504/x1_desktop_Sennheiser_MOMENTUM_4_Wireless_Black_Product_shot_Perspective.jpg'
        },
        {
            'title': 'Samsung Galaxy Buds 3 Pro',
            'description': 'Wireless earbuds with intelligent ANC, 360 audio, 24-bit audio, and IPX7 water resistance. Perfect companion for Samsung devices with seamless integration.',
            'price': Decimal('229.99'),
            'image_url': 'https://images.samsung.com/is/image/samsung/p6pim/uk/galaxy-s24/gallery/uk-galaxy-buds2-pro-r510-sm-r510nlvaeua-533186488'
        }
    ],
    'tablets': [
        {
            'title': 'iPad Pro 12.9" (2023)',
            'description': 'Apple\'s premium tablet with 12.9" Liquid Retina XDR display, M2 chip, 8GB RAM, 256GB storage, ProMotion technology, and Apple Pencil 2 support. Perfect for creative professionals.',
            'price': Decimal('1099.99'),
            'image_url': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/ipad-pro-finish-select-202210-11inch-space-gray-wifi?wid=5120&hei=2880&fmt=p-jpg&qlt=95&.v=1664411207154'
        },
        {
            'title': 'Samsung Galaxy Tab S9 Ultra',
            'description': 'Premium Android tablet with 14.6" Dynamic AMOLED 2X display, Snapdragon 8 Gen 2, 12GB RAM, 256GB storage, S Pen included, and IP68 water resistance. Excellent for productivity and entertainment.',
            'price': Decimal('999.99'),
            'image_url': 'https://images.samsung.com/is/image/samsung/p6pim/levant/sm-x910nzaemea/gallery/levant-galaxy-tab-s9-ultra-wifi-x910-sm-x910nzaemea-536818728'
        }
    ],
    'monitors': [
        {
            'title': 'LG UltraGear 27GP950-B',
            'description': '27" 4K UHD Nano IPS gaming monitor with 144Hz refresh rate, 1ms response time, HDMI 2.1, G-Sync and FreeSync Premium Pro compatibility. Perfect for high-end gaming setups.',
            'price': Decimal('799.99'),
            'image_url': 'https://www.lg.com/us/images/monitors/md08003830/gallery/desktop-01.jpg'
        },
        {
            'title': 'Dell UltraSharp U3223QE',
            'description': '32" 4K UHD IPS monitor with USB-C hub, HDR400, 98% DCI-P3 color coverage, and KVM switch. Ideal for professional work and content creation.',
            'price': Decimal('899.99'),
            'image_url': 'https://i.dell.com/is/image/DellContent/content/dam/ss2/product-images/dell-client-products/peripherals/monitors/u-series/u3223qe/media-gallery/monitor-u3223qe-gallery-1.psd?fmt=pjpg&pscan=auto&scl=1&wid=3491&hei=2077&qlt=100,1&resMode=sharp2&size=3491,2077'
        }
    ],
    'accessories': [
        {
            'title': 'Logitech MX Master 3S',
            'description': 'Premium wireless mouse with 8K DPI tracking, quiet clicks, MagSpeed electromagnetic scrolling, and multi-device support. Ergonomic design for all-day comfort.',
            'price': Decimal('99.99'),
            'image_url': 'https://resource.logitech.com/content/dam/logitech/en/products/mice/mx-master-3s/gallery/mx-master-3s-mouse-top-view-graphite.png'
        },
        {
            'title': 'Keychron Q1 Pro',
            'description': 'Wireless mechanical keyboard with QMK/VIA support, hot-swappable switches, aluminum case, and RGB backlighting. Perfect for enthusiasts and professionals.',
            'price': Decimal('199.99'),
            'image_url': 'https://cdn.shopify.com/s/files/1/0059/0630/1017/t/5/assets/keychronq1prowirelesscustomizablemechanicalkeyboard--edited-1669362431347.jpg'
        }
    ]
}

# Sample comments
COMMENTS = [
    "This looks amazing! Is it still under warranty?",
    "How long have you owned this device?",
    "Does it come with all original accessories?",
    "Would you accept a lower offer?",
    "Is there any damage or scratches?",
    "How's the battery health?",
    "Can you ship internationally?",
    "Is the price negotiable?",
    "Do you have the original receipt?",
    "What's the reason for selling?",
    "How does it perform with demanding applications?",
    "Are there any known issues with this model?",
    "Can I see more photos of the device?",
    "Is this the latest model?",
    "Does it support fast charging?"
]

class Command(BaseCommand):
    help = 'Populates the database with realistic fake data for electronics auctions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before populating',
        )

    def handle(self, *args, **options):
        clear = options['clear']

        if clear:
            self.clear_existing_data()

        # Create users with profiles
        users = self.create_users()

        # Create auctions
        auctions = self.create_auctions(users)

        # Create bids, comments, watchlists
        self.create_interactions(users, auctions)

        # Close some auctions and create ratings
        self.close_auctions_and_create_ratings(users, auctions)

        self.stdout.write(self.style.SUCCESS('Successfully populated database with fake data'))

    def clear_existing_data(self):
        """Clear existing data from the database"""
        self.stdout.write("Clearing existing data...")

        # Delete in proper order to avoid foreign key constraints
        Rating.objects.all().delete()
        Comment.objects.all().delete()
        Bid.objects.all().delete()
        Watchlist.objects.all().delete()
        Auction.objects.all().delete()

        # Keep users if they exist, but delete non-superuser users
        User.objects.filter(is_superuser=False).delete()

        self.stdout.write(self.style.SUCCESS("Existing data cleared"))

    def create_users(self):
        """Create sample users with profiles"""
        self.stdout.write("Creating users...")

        created_users = []

        for user_data in USERS:
            # Check if user already exists
            if not User.objects.filter(username=user_data['username']).exists():
                # Create user
                user = User.objects.create_user(
                    username=user_data['username'],
                    email=user_data['email'],
                    password=user_data['password'],
                    first_name=user_data['first_name'],
                    last_name=user_data['last_name']
                )

                # Update profile
                profile = user.profile
                profile.bio = user_data['bio']

                # Download and save profile picture
                try:
                    response = requests.get(user_data['profile_pic'], stream=True, timeout=10)
                    if response.status_code == 200:
                        filename = f"{user_data['username']}_profile.jpg"
                        profile.profile_picture.save(
                            filename,
                            ContentFile(response.content),
                            save=False
                        )
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error downloading profile picture: {e}"))

                profile.save()
                created_users.append(user)
                self.stdout.write(f"Created user: {user.username}")
            else:
                user = User.objects.get(username=user_data['username'])
                created_users.append(user)
                self.stdout.write(f"User already exists: {user.username}")

        return created_users

    def create_auctions(self, users):
        """Create sample auctions"""
        self.stdout.write("Creating auctions...")

        created_auctions = []

        # Create directory for downloaded images if it doesn't exist
        media_root = settings.MEDIA_ROOT
        images_dir = os.path.join(media_root, 'auction_images')
        os.makedirs(images_dir, exist_ok=True)

        # Create auctions for each category
        for category, items in ELECTRONICS_DATA.items():
            for item in items:
                # Randomly select a user
                user = random.choice(users)

                # Create auction with random creation date in the past 30 days
                days_ago = random.randint(1, 30)
                created_at = timezone.now() - timedelta(days=days_ago)

                auction = Auction(
                    title=item['title'],
                    description=item['description'],
                    price=item['price'],
                    category=category,
                    user=user,
                    is_close=False,
                    created_at=created_at
                )

                # Download and save image
                try:
                    if item['image_url']:
                        response = requests.get(item['image_url'], stream=True, timeout=10)
                        if response.status_code == 200:
                            # Generate a filename from the title
                            filename = f"{category}_{item['title'].lower().replace(' ', '_')[:30]}.jpg"
                            auction.image.save(
                                filename,
                                ContentFile(response.content),
                                save=False
                            )
                        else:
                            auction.image_url = item['image_url']
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error downloading image: {e}"))
                    auction.image_url = item['image_url']

                auction.save()
                created_auctions.append(auction)
                self.stdout.write(f"Created auction: {auction.title}")

                # Create initial bid by the auction creator
                initial_bid = Bid(
                    amount=item['price'],
                    auction=auction,
                    user=user
                )
                initial_bid.save()

        return created_auctions

    def create_interactions(self, users, auctions):
        """Create bids, comments, and watchlists"""
        self.stdout.write("Creating interactions (bids, comments, watchlists)...")

        # Create bids
        for auction in auctions:
            # Skip if auction is by the last user (to avoid self-bidding)
            if auction.user == users[-1]:
                continue

            # Random number of bids (0-5)
            num_bids = random.randint(0, 5)

            current_price = auction.price

            for _ in range(num_bids):
                # Random bidder (not the auction creator)
                potential_bidders = [u for u in users if u != auction.user]
                bidder = random.choice(potential_bidders)

                # Increase price by 5-15%
                increase = random.uniform(0.05, 0.15)
                new_price = current_price * (1 + Decimal(increase))
                new_price = Decimal(round(float(new_price), 2))  # Round to 2 decimal places

                # Create bid
                bid = Bid(
                    amount=new_price,
                    auction=auction,
                    user=bidder
                )
                bid.save()

                current_price = new_price
                self.stdout.write(f"Created bid: {bidder.username} bid {new_price} on {auction.title}")

        # Create comments
        for auction in auctions:
            # Random number of comments (0-3)
            num_comments = random.randint(0, 3)

            for _ in range(num_comments):
                # Random commenter (not the auction creator)
                potential_commenters = [u for u in users if u != auction.user]
                commenter = random.choice(potential_commenters)

                # Random comment
                message = random.choice(COMMENTS)

                # Create comment
                comment = Comment(
                    message=message,
                    user=commenter,
                    auction=auction
                )
                comment.save()
                self.stdout.write(f"Created comment on {auction.title}")

        # Create watchlists
        for user in users:
            # Create watchlist for user if it doesn't exist
            watchlist, created = Watchlist.objects.get_or_create(user=user)

            # Add random auctions to watchlist (not created by the user)
            potential_auctions = [a for a in auctions if a.user != user]
            num_to_watch = min(random.randint(1, 5), len(potential_auctions))

            auctions_to_watch = random.sample(potential_auctions, num_to_watch)

            for auction in auctions_to_watch:
                watchlist.auctions.add(auction)

            self.stdout.write(f"Added {num_to_watch} auctions to {user.username}'s watchlist")

    def close_auctions_and_create_ratings(self, users, auctions):
        """Close some auctions and create ratings"""
        self.stdout.write("Closing auctions and creating ratings...")

        # Close approximately 30% of auctions
        num_to_close = max(1, int(len(auctions) * 0.3))
        auctions_to_close = random.sample(auctions, num_to_close)

        for auction in auctions_to_close:
            # Close the auction
            auction.is_close = True
            auction.save()

            # Get highest bidder
            highest_bid = Bid.objects.filter(auction=auction).order_by('-amount').first()

            if highest_bid and highest_bid.user != auction.user:
                # Create rating from seller to buyer
                seller_rating = Rating(
                    rated_user=highest_bid.user,  # Buyer
                    rater=auction.user,  # Seller
                    auction=auction,
                    score=random.randint(3, 5),  # Random score 3-5
                    comment=f"Great buyer for {auction.title}. Smooth transaction!",
                    as_buyer=True
                )
                seller_rating.save()

                # Create rating from buyer to seller
                buyer_rating = Rating(
                    rated_user=auction.user,  # Seller
                    rater=highest_bid.user,  # Buyer
                    auction=auction,
                    score=random.randint(3, 5),  # Random score 3-5
                    comment=f"Excellent seller! Item as described and fast shipping.",
                    as_seller=True
                )
                buyer_rating.save()

                self.stdout.write(f"Closed auction: {auction.title} and created ratings")
