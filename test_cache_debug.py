#!/usr/bin/env python
"""Debug test to see what's happening with cache and booking"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labease_django.settings')
django.setup()

from django.test import Client
from django.core.cache import cache
from lab_suggestion.models import Test

# Show available tests
print("Available tests (first 20):")
for i, test in enumerate(Test.objects.all()[:20], 1):
    print(f"{i}. {test.name}")

print("\n" + "="*70)
print("TESTING BOOKING WITH CACHE")
print("="*70)

# Clear cache first
cache.clear()

# Create a test client
client = Client()
session_id = "debug_test"

# Message 1: Select test
print("\n[MESSAGE 1] Detecting and caching test...")
print('Sending: "Book Blood Sugar"')

response_1 = client.post(
    '/api/chatbot/',
    data=json.dumps({
        'message': 'Book Blood Sugar',
        'session_id': session_id
    }),
    content_type='application/json'
)

result_1 = response_1.json()
print(f"Response 1: {result_1['response'][:150]}...")

# Check cache
cached = cache.get(f"booking_test_{session_id}")
print(f"Cached test after message 1: {cached}")

# Message 2: Provide booking details
print("\n[MESSAGE 2] Providing booking details...")
print('Sending: "My name is Test User, test@gmail.com, 1234567890"')

response_2 = client.post(
    '/api/chatbot/',
    data=json.dumps({
        'message': 'My name is Test User, test@gmail.com, 1234567890',
        'session_id': session_id
    }),
    content_type='application/json'
)

result_2 = response_2.json()
print(f"Response 2 keys: {result_2.keys()}")

# Check if it's an error
if 'error' in result_2:
    print(f"❌ ERROR: {result_2['error']}")
else:
    print(f"Response 2: {result_2['response'][:200]}...")
    
    # Check what type of response this is
    if 'Booking Confirmed' in result_2['response']:
        print("✅ BOOKING SUCCESSFUL!")
    elif 'Test Email:' in result_2['response']:
        print("ℹ️ Showing email details (normal flow)")
    elif 'I found' in result_2['response']:
        print("⚠️ Showing search results (NOT BOOKING!)")
    elif 'Missing' in result_2['response']:
        print("⚠️ Missing information message (NOT BOOKING!)")
    else:
        print("❓ Unknown response type")

# Check cache after
cached_after = cache.get(f"booking_test_{session_id}")
print(f"\nCached test after message 2: {cached_after}")

print("\n" + "="*70)
