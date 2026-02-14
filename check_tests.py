#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labease_django.settings')
django.setup()

from lab_suggestion.models import Test

tests = Test.objects.all().order_by('id')
print(f"Total tests in database: {Test.objects.count()}\n")
print("ID | Test Name | Price")
print("-" * 60)
for test in tests:
    price = f"Rs. {test.price}" if test.price else "No price"
    print(f"{test.id} | {test.name} | {price}")
