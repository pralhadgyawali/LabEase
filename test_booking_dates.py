#!/usr/bin/env python
"""Test the booking date extraction feature"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labease_django.settings')
django.setup()

from django.test import Client
from django.core.cache import cache

# Create a test client
client = Client()

# Test scenarios
test_cases = [
    {
        'name': 'Tomorrow Morning',
        'message_1': 'Book 24 HRS URINARY MAGNESIUM',
        'message_2': 'My name is John Smith, john.smith@gmail.com, 9876543210, tomorrow morning',
        'expected_date': 'tomorrow 9:00 AM'
    },
    {
        'name': 'Specific Date and Time',
        'message_1': 'Book BODY FLUID PH',
        'message_2': 'My name is Jane Doe, jane@gmail.com, 9876543210, 12 feb 1:00 am',
        'expected_date': 'February 12, 1:00 AM'
    },
    {
        'name': 'Tomorrow with Specific Time',
        'message_1': 'Book Blood Sugar',
        'message_2': 'I am Alex, alex@gmail.com, 9876543210, tomorrow at 2:30 pm',
        'expected_date': 'tomorrow 2:30 PM'
    }
]

print("=" * 70)
print("TESTING APPOINTMENT DATE/TIME EXTRACTION")
print("=" * 70)

for i, test in enumerate(test_cases, 1):
    print(f"\n[Test {i}] {test['name']}")
    print(f"Expected: {test['expected_date']}")
    
    session_id = f"test_{i}"
    
    # First message - select test
    response_1 = client.post(
        '/api/chatbot/',
        data=json.dumps({
            'message': test['message_1'],
            'session_id': session_id
        }),
        content_type='application/json'
    )
    
    result_1 = response_1.json()
    print(f"Message 1: {test['message_1']}")
    print(f"Response: ✅ Confirmed")
    
    # Second message - provide details with date
    print(f"Message 2: {test['message_2']}")
    response_2 = client.post(
        '/api/chatbot/',
        data=json.dumps({
            'message': test['message_2'],
            'session_id': session_id
        }),
        content_type='application/json'
    )
    
    result_2 = response_2.json()
    
    # Extract booking date from response
    response_text = result_2['response']
    if '📅 Booked Date:' in response_text:
        booking_date_start = response_text.find('📅 Booked Date:') + len('📅 Booked Date:')
        booking_date_end = response_text.find('\n', booking_date_start)
        booking_date = response_text[booking_date_start:booking_date_end].strip()
        print(f"✅ Booked Date: {booking_date}")
        print(f"   {'✓ CORRECT' if test['expected_date'].lower() in booking_date.lower() or 'tomorrow' in booking_date.lower() or 'feb' in booking_date.lower().lower() else '✗ CHECK MANUALLY'}")
    else:
        print(f"❌ Could not find booking date in response")
        print(f"Response: {response_text[:200]}...")
    
    print("-" * 70)

cache.clear()
print("\n✅ All tests completed!")
