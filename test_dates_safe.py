#!/usr/bin/env python
"""Test the booking date extraction feature with better error handling"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labease_django.settings')
django.setup()

from django.test import Client
from django.core.cache import cache

# Create a test client
client = Client()

test_session_id = "date_test_1"
test_message_1 = "Book 24 HRS URINARY MAGNESIUM"
test_message_2 = "My name is John Smith, john.smith@gmail.com, 9876543210, tomorrow morning"

print("=" * 70)
print("TESTING APPOINTMENT DATE EXTRACTION")
print("=" * 70)

print("\n[1] First message: Select test")
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
print(f"    Status: {response_1.status_code}")
print(f"    Response: {result_1.get('response', 'No response')[:100]}...")

# Check cache
cached = cache.get(f"booking_test_{test_session_id}")
print(f"    Cached test: {cached}")

print("\n[2] Second message: Provide details with date")
print(f"    Sending: {test_message_2}")

response_2 = client.post(
    '/api/chatbot/',
    data=json.dumps({
        'message': test_message_2,
        'session_id': test_session_id
    }),
    content_type='application/json'
)

print(f"    Status: {response_2.status_code}")
print(f"    Content-Type: {response_2.get('Content-Type', 'unknown')}")

if response_2.status_code == 200:
    try:
        result_2 = response_2.json()
        if 'error' in result_2:
            print(f"    Error: {result_2['error']}")
        else:
            response_text = result_2.get('response', '')
            
            # Extract booking date
            if '📅 Booked Date:' in response_text:
                booking_date_start = response_text.find('📅 Booked Date:') + len('📅 Booked Date:')
                booking_date_end = response_text.find('\n', booking_date_start)
                booking_date = response_text[booking_date_start:booking_date_end].strip()
                
                print(f"    ✅ Booking Confirmed!")
                print(f"    📅 Booked Date: {booking_date}")
                
                # Check if date contains "tomorrow" or tomorrow's date
                import datetime
                tomorrow = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime('%B %d')
                if 'tomorrow' in booking_date.lower() or tomorrow in booking_date or '9:' in booking_date:
                    print(f"    ✓ Date extraction WORKING!")
                else:
                    print(f"    ⚠ Date might not be extracted correctly")
            else:
                print(f"    ❌ No booking found")
                print(f"    Response: {response_text[:300]}...")
    except json.JSONDecodeError as e:
        print(f"    JSON Error: {e}")
        print(f"    Response: {response_2.content.decode()[:500]}")
else:
    print(f"    ❌ HTTP Error {response_2.status_code}")
    print(f"    Response: {response_2.content.decode()[:500]}")

cache.clear()
print("\n" + "=" * 70)
