"""
Knowledge base for the auction chatbot
Contains predefined responses for common questions in Arabic and English
"""

# Arabic Knowledge Base
KNOWLEDGE_BASE_AR = {
    "التحية": {
        "examples": ["مرحبا", "السلام عليكم", "أهلا", "مساء الخير", "صباح الخير", "هاي", "هلو"],
        "responses": [
            "مرحباً بك! كيف يمكنني مساعدتك اليوم؟",
            "أهلاً وسهلاً! أنا هنا لمساعدتك في موقع المزادات.",
            "مرحبا! هل تحتاج مساعدة في شيء معين؟"
        ]
    },
    "التسجيل": {
        "examples": ["أريد التسجيل", "كيف أسجل في الموقع؟", "كيف أسجل في الموقع", "تسجيل جديد", "إنشاء حساب", "التسجيل في الموقع"],
        "responses": [
            "مرحباً! يمكنك التسجيل بالضغط على زر 'تسجيل جديد' ثم تعبئة البيانات المطلوبة.",
            "لإنشاء حساب جديد، اذهب إلى صفحة التسجيل وأدخل اسمك، بريدك الإلكتروني وكلمة المرور.",
            "التسجيل سهل جداً! فقط املأ النموذج وستكون جاهزاً للمزايدة."
        ]
    },
    "تسجيل الدخول": {
        "examples": ["كيف أسجل دخولي؟", "تسجيل الدخول", "أريد الدخول لحسابي", "تسجيل دخول", "دخول المستخدم"],
        "responses": [
            "لتسجيل الدخول، اضغط على زر 'تسجيل الدخول' وأدخل بريدك الإلكتروني وكلمة المرور.",
            "يمكنك الدخول إلى حسابك من خلال صفحة تسجيل الدخول في أعلى الصفحة.",
            "مرحباً بعودتك! أدخل بياناتك لتسجيل الدخول."
        ]
    },
    "عرض المزادات": {
        "examples": ["أين أجد المزادات؟", "عرض المزادات المتاحة", "ما هي المزادات الحالية؟", "أريد رؤية المزادات", "قائمة المزادات"],
        "responses": [
            "يمكنك تصفح المزادات الحالية من الصفحة الرئيسية أو قسم المزادات.",
            "لدينا مزادات مميزة الآن! تصفح الفئات المختلفة لتجد ما يناسبك.",
            "جميع المزادات المتاحة تجدها مرتبة حسب الفئات والأسعار."
        ]
    },
    "المزايدة": {
        "examples": ["كيف أزايد؟", "كيف أزايد على منتج؟", "كيف أزايد على منتج", "طريقة المزايدة", "أريد المزايدة على منتج", "كيفية المزايدة", "أين أزايد؟"],
        "responses": [
            "للمزايدة، اختر المزاد الذي تريده واضغط على 'زايد الآن' ثم أدخل المبلغ.",
            "كل ما عليك هو تسجيل الدخول ثم اختيار المنتج والمزايدة عليه.",
            "المزايدة سهلة! فقط توجه للمزاد المطلوب وادخل قيمة أعلى من الحالية."
        ]
    },
    "الدفع": {
        "examples": ["كيف أدفع؟", "ما هي طرق الدفع المتاحة؟", "ما هي طرق الدفع", "طريقة الدفع", "وسائل الدفع", "هل يمكنني الدفع أونلاين؟", "الدفع بعد الفوز", "الدفع"],
        "responses": [
            "نوفر عدة طرق للدفع، منها البطاقة الائتمانية والتحويل البنكي وPayPal.",
            "بعد الفوز بالمزاد، سيتم توجيهك إلى صفحة الدفع لاستكمال العملية.",
            "يمكنك الدفع أونلاين بسهولة بعد انتهاء المزاد من خلال حسابك. نقبل Visa وMastercard وPayPal."
        ]
    },
    "الشحن": {
        "examples": ["متى يصل المنتج؟", "الشحن متى؟", "تفاصيل الشحن", "كيف يتم الشحن؟", "هل يوجد توصيل؟"],
        "responses": [
            "نعم، نوفر خدمة الشحن لجميع المناطق. يتم الشحن خلال 3 إلى 7 أيام عمل.",
            "يتم تجهيز المنتج بعد الدفع مباشرة ويُشحن إلى عنوانك المحدد.",
            "لديك خيار تتبع الشحنة من خلال لوحة التحكم الخاصة بك."
        ]
    },
    "الفئات": {
        "examples": ["ما هي الفئات المتاحة؟", "أنواع المنتجات", "فئات المزادات", "ما تبيعون؟"],
        "responses": [
            "نتخصص في الإلكترونيات: اللابتوبات، الهواتف الذكية، السماعات، والإكسسوارات.",
            "لدينا مزادات متنوعة للأجهزة الإلكترونية بأفضل الأسعار.",
            "تصفح فئاتنا: أجهزة الكمبيوتر، الهواتف، الصوتيات، والملحقات."
        ]
    },
    "الدعم الفني": {
        "examples": ["أحتاج للمساعدة", "مشكلة في الموقع", "الدعم الفني", "كيف أتواصل مع الدعم؟", "المساعدة"],
        "responses": [
            "نحن هنا لمساعدتك! تواصل معنا عبر نظام الرسائل أو البريد الإلكتروني.",
            "إذا واجهت أي مشكلة، لا تتردد بالتواصل معنا عبر الشات أو البريد الإلكتروني.",
            "يمكنك التواصل مع الدعم الفني على مدار الساعة من خلال نموذج التواصل."
        ]
    },
    "الوداع": {
        "examples": ["وداعا", "مع السلامة", "شكرا", "باي", "إلى اللقاء"],
        "responses": [
            "شكراً لك! نتمنى لك تجربة ممتعة في المزايدة.",
            "مع السلامة! لا تتردد في العودة إذا احتجت أي مساعدة.",
            "وداعاً! نراك قريباً في مزاداتنا المميزة."
        ]
    }
}

# English Knowledge Base
KNOWLEDGE_BASE_EN = {
    "greetings": {
        "examples": ["hi", "hello", "hey", "greetings", "good morning", "good evening", "howdy"],
        "responses": [
            "Hello! How can I assist you today?",
            "Hi there! I'm here to help you with our auction platform.",
            "Welcome! What can I do for you?"
        ]
    },
    "registration": {
        "examples": ["how to register", "How to register?", "How to register", "sign up", "create account", "registration process", "new account"],
        "responses": [
            "To register, click the 'Sign Up' button and fill in the required information.",
            "Creating an account is easy! Just go to the registration page and enter your details.",
            "Registration is simple - just provide your name, email, and password to get started."
        ]
    },
    "login": {
        "examples": ["how to login", "sign in", "log in", "access account", "login process"],
        "responses": [
            "To log in, click the 'Login' button and enter your email and password.",
            "You can access your account through the login page at the top of the site.",
            "Welcome back! Just enter your credentials to sign in."
        ]
    },
    "auctions": {
        "examples": ["view auctions", "current auctions", "available auctions", "auction list", "browse auctions"],
        "responses": [
            "You can browse current auctions from the homepage or auctions section.",
            "We have exciting auctions available now! Browse different categories to find what you need.",
            "All available auctions are organized by categories and prices for easy browsing."
        ]
    },
    "bidding": {
        "examples": ["how to bid", "How to bid on items?", "How to bid on items", "bidding process", "place bid", "make bid", "bidding instructions"],
        "responses": [
            "To bid, select the auction you want and click 'Place Bid', then enter your amount.",
            "Simply log in, choose the product, and place your bid with an amount higher than current bid.",
            "Bidding is easy! Just go to the auction and enter a value higher than the current bid."
        ]
    },
    "payment": {
        "examples": ["payment methods", "Payment methods?", "Payment methods", "how to pay", "payment process", "online payment", "pay after winning"],
        "responses": [
            "We offer several payment methods including credit cards, bank transfers, and PayPal.",
            "After winning an auction, you'll be directed to the payment page to complete the transaction.",
            "You can pay online easily after the auction ends through your account. We accept Visa, Mastercard, and PayPal."
        ]
    },
    "shipping": {
        "examples": ["shipping info", "delivery time", "when will it arrive", "shipping details", "delivery"],
        "responses": [
            "Yes, we provide shipping to all areas. Delivery takes 3 to 7 business days.",
            "Products are prepared after payment and shipped to your specified address.",
            "You can track your shipment through your account dashboard."
        ]
    },
    "categories": {
        "examples": ["what categories", "product types", "what do you sell", "available categories"],
        "responses": [
            "We specialize in electronics: laptops, smartphones, headphones, and accessories.",
            "We have diverse auctions for electronic devices at the best prices.",
            "Browse our categories: computers, phones, audio equipment, and accessories."
        ]
    },
    "support": {
        "examples": ["need help", "technical support", "contact support", "customer service", "assistance"],
        "responses": [
            "We're here to help! Contact us through our messaging system or email.",
            "If you encounter any issues, don't hesitate to reach out via chat or email.",
            "You can contact technical support 24/7 through our contact form."
        ]
    },
    "goodbye": {
        "examples": ["bye", "goodbye", "see you", "thanks", "farewell"],
        "responses": [
            "Thank you! We hope you enjoy your bidding experience.",
            "Goodbye! Don't hesitate to come back if you need any help.",
            "See you later! We look forward to seeing you in our exciting auctions."
        ]
    }
}
