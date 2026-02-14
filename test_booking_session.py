#!/usr/bin/env python
"""Test the session memory for booking flow"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labease_django.settings')
django.setup()

from django.test import Client
from django.core.cache import cache

# Create a test client
client = Client()

# Test data
test_session_id = "test_session_123"
test_message_1 = "Book 24 HRS URINARY MAGNESIUM"
test_message_2 = "My name is John Smith, john.smith@gmail.com, 9876543210"

print("=" * 60)
print("TESTING SESSION MEMORY FOR BOOKING FLOW")
print("=" * 60)

print("\n[1] First message: User clicks 'Book 24 HRS URINARY MAGNESIUM'")
print(f"    Sending: {test_message_1}")

response_1 = client.post(
    '/api/chatbot/',
    data=json.dumps({
        'message': test_message_1,
        'session_id': test_session_id
    }),
    content_type='application/json'
)

result_1 = response_1.json()
print(f"    Response: {result_1['response'][:100]}...")

# Check if test was stored in cache
stored_test = cache.get(f"booking_test_{test_session_id}")
print(f"    Stored test in cache: {stored_test}")

print("\n[2] Second message: User provides details")
print(f"    Sending: {test_message_2}")

response_2 = client.post(
    '/api/chatbot/',
    data=json.dumps({
        'message': test_message_2,
        'session_id': test_session_id
    }),
    content_type='application/json'
)

result_2 = response_2.json()
print(f"    Response: {result_2['response'][:150]}...")

# Check if booking was successful
if "Booking Confirmed" in result_2['response'] or "successfully" in result_2['response'].lower():
    print("\n✅ SUCCESS: Booking completed on second message!")
    print("   Test context was remembered across messages.")
else:
    print("\n❌ FAILED: Booking not created")
    print("   Test context may not have been retrieved from cache.")

# Clean up
cache.delete(f"booking_test_{test_session_id}")

print("\n" + "=" * 60)
print("TEST COMPLETE")
print("=" * 60)
