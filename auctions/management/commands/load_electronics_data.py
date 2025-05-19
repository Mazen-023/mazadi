import os
import random
import requests
from io import BytesIO
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.contrib.auth import get_user_model
from auctions.models import Auction, Bid, CATEGORY_CHOICES
from django.conf import settings

User = get_user_model()

# Sample electronics data by category
ELECTRONICS_DATA = {
    'laptops': [
        {
            'title': 'Dell XPS 15 (2023)',
            'description': 'Premium laptop with 15.6" OLED display, Intel Core i7-12700H, 16GB RAM, 1TB SSD, NVIDIA RTX 3050 Ti, Windows 11 Pro. Perfect for professionals and content creators.',
            'price': Decimal('1499.99'),
            'image_url': 'https://i.dell.com/is/image/DellContent/content/dam/ss2/product-images/dell-client-products/notebooks/xps-notebooks/xps-15-9530/media-gallery/black/notebook-xps-15-9530-t-black-gallery-1.psd?fmt=png-alpha&pscan=auto&scl=1&hei=402&wid=402&qlt=100,1&resMode=sharp2&size=402,402&chrss=full'
        },
        {
            'title': 'MacBook Pro 14" M2 Pro',
            'description': 'Apple MacBook Pro with M2 Pro chip, 14-inch Liquid Retina XDR display, 16GB unified memory, 512GB SSD storage. Powerful performance for developers and designers.',
            'price': Decimal('1999.99'),
            'image_url': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/mbp14-spacegray-select-202301?wid=904&hei=840&fmt=jpeg&qlt=90&.v=1671304673229'
        },
        {
            'title': 'Lenovo ThinkPad X1 Carbon Gen 11',
            'description': 'Business laptop with 14" WUXGA display, Intel Core i5-1335U, 16GB LPDDR5, 512GB SSD, Windows 11 Pro. Military-grade durability with premium performance.',
            'price': Decimal('1399.99'),
            'image_url': 'https://p1-ofp.static.pub/medias/bWFzdGVyfHJvb3R8MjM5NTIxfGltYWdlL3BuZ3xoMjEvaGRkLzE0MzY5NjQxMDg5MDU0LnBuZ3w0ZjBiNGU5MGZkYzA3MDIwNGZlODYxZTJkMzhjZTAwYjllNDY3NTMxODUzYWE2YWE5ZTZjMjI0M2VjYjUyYTJj/lenovo-laptop-thinkpad-x1-carbon-gen-11-14-intel-hero.png'
        },
        {
            'title': 'ASUS ROG Zephyrus G14',
            'description': 'Gaming laptop with 14" QHD 120Hz display, AMD Ryzen 9 7940HS, 16GB DDR5, 1TB SSD, NVIDIA GeForce RTX 4060, Windows 11 Home. Compact powerhouse for gamers.',
            'price': Decimal('1599.99'),
            'image_url': 'https://dlcdnwebimgs.asus.com/gain/C97AE94C-346D-4301-A10D-B3F395A1D453/w1000/h732'
        },
        {
            'title': 'HP Spectre x360 14',
            'description': 'Convertible laptop with 13.5" 3K2K OLED touch display, Intel Core i7-1355U, 16GB RAM, 1TB SSD, Intel Iris Xe Graphics, Windows 11 Home. Elegant design with versatile functionality.',
            'price': Decimal('1449.99'),
            'image_url': 'https://ssl-product-images.www8-hp.com/digmedialib/prodimg/lowres/c08499684.png'
        }
    ],
    'smartphones': [
        {
            'title': 'Samsung Galaxy S23 Ultra',
            'description': 'Flagship smartphone with 6.8" Dynamic AMOLED 2X display, Snapdragon 8 Gen 2, 12GB RAM, 256GB storage, 200MP main camera, 5000mAh battery, Android 13. Ultimate performance and photography.',
            'price': Decimal('1199.99'),
            'image_url': 'https://images.samsung.com/is/image/samsung/p6pim/levant/2302/gallery/levant-galaxy-s23-ultra-s918-sm-s918bzkcmea-534859389'
        },
        {
            'title': 'iPhone 15 Pro Max',
            'description': 'Apple\'s premium smartphone with 6.7" Super Retina XDR display, A17 Pro chip, 8GB RAM, 256GB storage, 48MP triple camera system, iOS 17. Titanium design with pro-grade capabilities.',
            'price': Decimal('1199.99'),
            'image_url': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/iphone-15-pro-finish-select-202309-6-7inch-naturaltitanium?wid=5120&hei=2880&fmt=p-jpg&qlt=80&.v=1692845702708'
        },
        {
            'title': 'Google Pixel 8 Pro',
            'description': 'Google\'s flagship with 6.7" Super Actua display, Google Tensor G3, 12GB RAM, 128GB storage, 50MP triple camera system, 5050mAh battery, Android 14. AI-powered features and clean software.',
            'price': Decimal('999.99'),
            'image_url': 'https://lh3.googleusercontent.com/aDhYBZGpZ_twcDH5Je5SsLq5IPwGIL-YFa5yrJPhO5ZQpw8yvn7GiCTgkZJmgYiRHzM3-Dn_NDxGQBuuEcLKaXTpIw=w1000-rw'
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
            'description': 'Premium wireless noise-cancelling headphones with 30-hour battery life, LDAC support, adaptive sound control, and multipoint connection. Industry-leading noise cancellation and sound quality.',
            'price': Decimal('399.99'),
            'image_url': 'https://www.sony.com/image/5d02da5df552836db894cead8a68f5f3?fmt=png-alpha&wid=660&hei=660'
        },
        {
            'title': 'Apple AirPods Pro 2',
            'description': 'Wireless earbuds with active noise cancellation, transparency mode, adaptive EQ, spatial audio, and MagSafe charging case. Seamless integration with Apple devices.',
            'price': Decimal('249.99'),
            'image_url': 'https://store.storeimages.cdn-apple.com/4982/as-images.apple.com/is/MQD83?wid=1144&hei=1144&fmt=jpeg&qlt=90&.v=1660803972361'
        },
        {
            'title': 'Bose QuietComfort Ultra Headphones',
            'description': 'Premium noise-cancelling headphones with immersive audio, CustomTune technology, up to 24-hour battery life, and smart features. Exceptional comfort and sound quality.',
            'price': Decimal('429.99'),
            'image_url': 'https://assets.bose.com/content/dam/cloudassets/Bose_DAM/Web/consumer_electronics/global/products/headphones/qc_ultra_headphones/product_silo_images/QCU_HP_BLK_hero_010_RGB.png'
        },
        {
            'title': 'Sennheiser Momentum 4 Wireless',
            'description': 'Audiophile-grade wireless headphones with 60-hour battery life, adaptive noise cancellation, and customizable sound. Superior sound quality with exceptional comfort.',
            'price': Decimal('349.99'),
            'image_url': 'https://assets.sennheiser.com/img/25504/x1_desktop_Sennheiser_MOMENTUM_4_Wireless_Black_Product_shot_Perspective.jpg'
        },
        {
            'title': 'Samsung Galaxy Buds 3 Pro',
            'description': 'Wireless earbuds with intelligent ANC, 360 audio, 24-bit Hi-Fi sound, and seamless connectivity. Perfect companion for Samsung devices with long battery life.',
            'price': Decimal('229.99'),
            'image_url': 'https://images.samsung.com/is/image/samsung/p6pim/uk/2307/gallery/uk-galaxy-buds3-pro-r630-sm-r630nzaaeua-537518048'
        }
    ],
    'monitors': [
        {
            'title': 'LG UltraGear 27GP950-B',
            'description': '27" 4K UHD Nano IPS gaming monitor with 144Hz refresh rate, 1ms response time, NVIDIA G-SYNC, AMD FreeSync Premium Pro, HDR600, and RGB lighting. Ultimate gaming experience.',
            'price': Decimal('799.99'),
            'image_url': 'https://www.lg.com/us/images/monitors/md08003830/gallery/desktop-01.jpg'
        },
        {
            'title': 'Dell UltraSharp U3223QE',
            'description': '32" 4K UHD IPS monitor with USB-C hub, HDR400, 98% DCI-P3 color coverage, and KVM switch. Perfect for professionals and content creators.',
            'price': Decimal('899.99'),
            'image_url': 'https://i.dell.com/is/image/DellContent/content/dam/ss2/product-images/dell-client-products/peripherals/monitors/u-series/u3223qe/media-gallery/monitor-u3223qe-gallery-1.psd?fmt=png-alpha&pscan=auto&scl=1&hei=402&wid=402&qlt=100,1&resMode=sharp2&size=402,402'
        },
        {
            'title': 'Samsung Odyssey G9 G95NC',
            'description': '49" DQHD curved gaming monitor with mini-LED, 240Hz refresh rate, 1ms response time, HDR2000, and AMD FreeSync Premium Pro. Immersive ultrawide gaming experience.',
            'price': Decimal('1999.99'),
            'image_url': 'https://images.samsung.com/is/image/samsung/p6pim/uk/ls49cg954suxen/gallery/uk-odyssey-g9-g95nc-ls49cg954suxen-536860738'
        },
        {
            'title': 'ASUS ProArt PA32UCG-K',
            'description': '32" 4K HDR mini-LED monitor with 120Hz refresh rate, Thunderbolt 4, 98% DCI-P3, 99.5% Adobe RGB, and hardware calibration. Professional-grade display for creators.',
            'price': Decimal('2999.99'),
            'image_url': 'https://dlcdnwebimgs.asus.com/gain/f93bdd99-47d7-4f97-b770-7ff5c0aa46a0/'
        },
        {
            'title': 'Gigabyte M32UC',
            'description': '32" 4K curved gaming monitor with 144Hz refresh rate, 1ms response time, AMD FreeSync Premium Pro, and HDR400. Excellent value for high-performance gaming.',
            'price': Decimal('649.99'),
            'image_url': 'https://static.gigabyte.com/StaticFile/Image/Global/53c182f5b4d0d1d7b34f352ce3b8b9c4/Product/32215/png/1000'
        }
    ],
    'gaming': [
        {
            'title': 'PlayStation 5 Pro',
            'description': 'Next-gen gaming console with enhanced GPU, 2TB SSD storage, 4K gaming at 120fps, ray tracing, and backward compatibility. The ultimate PlayStation experience.',
            'price': Decimal('699.99'),
            'image_url': 'https://gmedia.playstation.com/is/image/SIEPDC/ps5-product-thumbnail-01-en-14sep21'
        },
        {
            'title': 'Xbox Series X',
            'description': 'Microsoft\'s flagship gaming console with 12 teraflops of power, 1TB SSD, 4K gaming at 120fps, Quick Resume, and Xbox Game Pass compatibility. Powerful next-gen gaming.',
            'price': Decimal('499.99'),
            'image_url': 'https://img-prod-cms-rt-microsoft-com.akamaized.net/cms/api/am/imageFileData/RE4mRni'
        },
        {
            'title': 'Nintendo Switch OLED Model',
            'description': 'Hybrid gaming console with 7" OLED screen, enhanced audio, 64GB storage, and improved kickstand. Play at home or on the go with Nintendo\'s innovative system.',
            'price': Decimal('349.99'),
            'image_url': 'https://assets.nintendo.com/image/upload/f_auto/q_auto/dpr_2.0/c_scale,w_400/ncom/en_US/switch/site-design-update/hardware/switch/nintendo-switch-oled-model-white-set/gallery/image01'
        },
        {
            'title': 'Steam Deck OLED 1TB',
            'description': 'Handheld gaming PC with 7.4" OLED display, AMD APU, 16GB RAM, 1TB SSD, and Steam OS. Play your PC games anywhere with console-like convenience.',
            'price': Decimal('649.99'),
            'image_url': 'https://cdn.cloudflare.steamstatic.com/steamdeck/images/press/oled/steam-deck-oled-front.png'
        },
        {
            'title': 'ASUS ROG Ally X',
            'description': 'Handheld gaming PC with 7" 120Hz display, AMD Ryzen Z2 Extreme, 24GB RAM, 1TB SSD, and Windows 11. High-performance gaming on the go.',
            'price': Decimal('799.99'),
            'image_url': 'https://dlcdnwebimgs.asus.com/gain/F8E6A1E1-8E1B-4D5E-9E0A-C4B1D7F7C9D5/w1000/h732'
        }
    ]
}

class Command(BaseCommand):
    help = 'Loads realistic electronics data into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--user',
            type=str,
            help='Username of the user who will own the auctions (will be created if does not exist)',
            default='admin'
        )
        parser.add_argument(
            '--password',
            type=str,
            help='Password for the user if it needs to be created',
            default='adminpassword'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing auctions before loading new data',
        )

    def handle(self, *args, **options):
        username = options['user']
        password = options['password']
        clear = options['clear']
        
        # Get or create user
        try:
            user = User.objects.get(username=username)
            self.stdout.write(self.style.SUCCESS(f'Using existing user: {username}'))
        except User.DoesNotExist:
            user = User.objects.create_user(username=username, password=password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created new user: {username}'))
        
        # Clear existing auctions if requested
        if clear:
            auction_count = Auction.objects.count()
            Auction.objects.all().delete()
            self.stdout.write(self.style.SUCCESS(f'Cleared {auction_count} existing auctions'))
        
        # Create directory for downloaded images if it doesn't exist
        media_root = settings.MEDIA_ROOT
        images_dir = os.path.join(media_root, 'auction_images')
        os.makedirs(images_dir, exist_ok=True)
        
        # Load data for each category
        total_created = 0
        for category, items in ELECTRONICS_DATA.items():
            self.stdout.write(f'Loading data for category: {category}')
            
            for item in items:
                # Create auction
                auction = Auction(
                    title=item['title'],
                    description=item['description'],
                    price=item['price'],
                    category=category,
                    user=user,
                    is_close=False
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
                    else:
                        auction.image_url = item['image_url']
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error downloading image: {e}"))
                    auction.image_url = item['image_url']
                
                auction.save()
                
                # Create initial bid
                Bid.objects.create(
                    amount=item['price'],
                    auction=auction,
                    user=user
                )
                
                total_created += 1
                self.stdout.write(f'  - Created auction: {item["title"]}')
        
        self.stdout.write(self.style.SUCCESS(f'Successfully loaded {total_created} electronics items'))
