from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

from apps.catalog.models import Category, DigitalAsset, Product
from apps.promotions.models import Coupon


SAMPLE_PRODUCTS = [
    {
        "category": "E-Books",
        "title": "Mastering Python Programming",
        "short_description": "Complete guide from basics to advanced Python development.",
        "description": "A comprehensive 400-page e-book covering Python fundamentals, OOP, async programming, testing, and deployment. Perfect for developers at any level.",
        "price": "29.99",
        "compare_at_price": "49.99",
        "is_featured": True,
    },
    {
        "category": "E-Books",
        "title": "Web Development with Django",
        "short_description": "Build scalable web applications with Django framework.",
        "description": "Learn Django from scratch. Covers models, views, templates, REST APIs, authentication, and deployment strategies.",
        "price": "34.99",
        "compare_at_price": None,
        "is_featured": True,
    },
    {
        "category": "Courses",
        "title": "Full-Stack JavaScript Bootcamp",
        "short_description": "12-week intensive course with projects and certificate.",
        "description": "Master React, Node.js, and MongoDB. Includes 40+ hours of video content, coding exercises, and 5 real-world projects.",
        "price": "99.99",
        "compare_at_price": "149.99",
        "is_featured": True,
    },
    {
        "category": "Courses",
        "title": "Data Science Fundamentals",
        "short_description": "Learn pandas, numpy, and machine learning basics.",
        "description": "Hands-on data science course with Jupyter notebooks, datasets, and ML model building exercises.",
        "price": "79.99",
        "compare_at_price": None,
        "is_featured": False,
    },
    {
        "category": "Templates",
        "title": "SaaS Landing Page Kit",
        "short_description": "20 responsive landing page templates for startups.",
        "description": "Beautiful, conversion-optimized landing page templates built with Tailwind CSS. Includes Figma files and HTML/CSS source.",
        "price": "49.99",
        "compare_at_price": "79.99",
        "is_featured": True,
    },
    {
        "category": "Templates",
        "title": "Admin Dashboard UI Kit",
        "short_description": "Complete admin panel components and layouts.",
        "description": "100+ UI components for building admin dashboards. Charts, tables, forms, and navigation patterns included.",
        "price": "39.99",
        "compare_at_price": None,
        "is_featured": False,
    },
    {
        "category": "Tools",
        "title": "SEO Analyzer Pro",
        "short_description": "Desktop tool for website SEO analysis and reporting.",
        "description": "Analyze any website's SEO performance. Generate PDF reports, track keywords, and get actionable recommendations.",
        "price": "59.99",
        "compare_at_price": "89.99",
        "is_featured": False,
    },
    {
        "category": "Tools",
        "title": "Code Snippet Manager",
        "short_description": "Organize and sync your code snippets across devices.",
        "description": "Cross-platform snippet manager with syntax highlighting, tagging, and cloud sync. Supports 50+ languages.",
        "price": "24.99",
        "compare_at_price": None,
        "is_featured": False,
    },
    {
        "category": "Graphics",
        "title": "Icon Pack — 2000+ Icons",
        "short_description": "Minimal line icons in SVG and PNG formats.",
        "description": "Professional icon set with 2000+ icons in multiple styles. SVG, PNG, and Figma formats included.",
        "price": "19.99",
        "compare_at_price": "29.99",
        "is_featured": True,
    },
    {
        "category": "Graphics",
        "title": "Social Media Template Bundle",
        "short_description": "500+ templates for Instagram, Twitter, and LinkedIn.",
        "description": "Ready-to-use social media templates in Canva and PSD formats. Covers posts, stories, and banners.",
        "price": "29.99",
        "compare_at_price": None,
        "is_featured": False,
    },
]

CATEGORIES = [
    {"name": "E-Books", "icon": "📚", "description": "Digital books and guides for learning"},
    {"name": "Courses", "icon": "🎓", "description": "Video courses and training programs"},
    {"name": "Templates", "icon": "🎨", "description": "Website and design templates"},
    {"name": "Tools", "icon": "🔧", "description": "Software tools and utilities"},
    {"name": "Graphics", "icon": "🖼️", "description": "Icons, illustrations, and design assets"},
]


class Command(BaseCommand):
    help = "Seed the database with sample categories, products, coupons, and admin user"

    def handle(self, *args, **options):
        self.stdout.write("Seeding database...")

        for i, cat_data in enumerate(CATEGORIES):
            Category.objects.get_or_create(
                name=cat_data["name"],
                defaults={
                    "icon": cat_data["icon"],
                    "description": cat_data["description"],
                    "sort_order": i,
                },
            )

        for prod_data in SAMPLE_PRODUCTS:
            category = Category.objects.get(name=prod_data["category"])
            product, created = Product.objects.get_or_create(
                title=prod_data["title"],
                defaults={
                    "category": category,
                    "short_description": prod_data["short_description"],
                    "description": prod_data["description"],
                    "price": prod_data["price"],
                    "compare_at_price": prod_data["compare_at_price"],
                    "is_featured": prod_data["is_featured"],
                },
            )
            if created:
                placeholder = ContentFile(
                    b"Digital product placeholder file for demo purposes.",
                    name=f"{product.slug}.txt",
                )
                DigitalAsset.objects.create(
                    product=product,
                    title=f"{product.title} — Main File",
                    file=placeholder,
                )

        coupons = [
            {"code": "WELCOME10", "discount_type": "percentage", "discount_value": "10", "description": "10% off for new customers"},
            {"code": "SAVE20", "discount_type": "fixed", "discount_value": "20", "description": "$20 off orders over $50", "min_order_amount": "50"},
            {"code": "FLASH50", "discount_type": "percentage", "discount_value": "50", "description": "50% flash sale", "max_uses": 100},
        ]
        for c in coupons:
            Coupon.objects.get_or_create(
                code=c["code"],
                defaults={
                    "discount_type": c["discount_type"],
                    "discount_value": c["discount_value"],
                    "description": c["description"],
                    "min_order_amount": c.get("min_order_amount", 0),
                    "max_uses": c.get("max_uses"),
                },
            )

        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser("admin", "admin@digitalshop.com", "admin123")
            self.stdout.write(self.style.SUCCESS("Created admin user (admin / admin123)"))

        if not User.objects.filter(username="demo").exists():
            User.objects.create_user("demo", "demo@digitalshop.com", "demo123")
            self.stdout.write(self.style.SUCCESS("Created demo user (demo / demo123)"))

        self.stdout.write(self.style.SUCCESS("Database seeded successfully!"))
