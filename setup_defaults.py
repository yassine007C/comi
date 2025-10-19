import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'comic_generator.settings')
django.setup()

from tokens.models import TokenPackage

packages = [
    {
        'name': 'Starter Pack',
        'token_amount': 10,
        'price': 9.99,
        'description': 'Perfect for trying out the service',
        'is_active': True
    },
    {
        'name': 'Popular Pack',
        'token_amount': 50,
        'price': 39.99,
        'description': 'Best value for regular users',
        'is_active': True
    },
    {
        'name': 'Pro Pack',
        'token_amount': 150,
        'price': 99.99,
        'description': 'For power users and professionals',
        'is_active': True
    }
]

for package_data in packages:
    package, created = TokenPackage.objects.get_or_create(
        name=package_data['name'],
        defaults=package_data
    )
    if created:
        print(f"Created package: {package.name}")
    else:
        print(f"Package already exists: {package.name}")

print("\nDefault token packages setup complete!")
