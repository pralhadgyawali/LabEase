#!/usr/bin/env python
"""Test booking with specific date and time"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labease_django.settings')
django.setup()

from django.test import Client
from django.core.cache import cache

client = Client()

test_cases = [
    {
        'name': 'Tomorrow Morning',
        'msg1': 'Book BODY FLUID PH',
        'msg2': 'My name is John Doe, john@example.com, 9876543210, tomorrow morning'
    },
    {
        'name': 'Specific Date 1:00 AM',
        'msg1': 'Book Blood Sugar F',
        'msg2': 'I am Jane Smith, jane@test.com, 9876543210, 12 feb 1:00 am'
    },
    {
        'name': 'Specific Date 2:30 PM',
        'msg1': 'Book ALBUMIN',
        'msg2': 'My name is Alex Jones, alex@mail.com, 1234567890, 15 feb 2:30 pm'
    }
]

print("=" * 70)
print("BOOKING WITH APPOINTMENT DATES")
print("=" * 70)

for tc in test_cases:
    print(f"\n✓ Test: {tc['name']}")
    session_id = f"date_test_{tc['name']}"
    cache.clear()
    
    # Message 1
    r1 = client.post('/api/chatbot/', 
        data=json.dumps({'message': tc['msg1'], 'session_id': session_id}),
        content_type='application/json').json()
    
    # Message 2
    r2 = client.post('/api/chatbot/',
        data=json.dumps({'message': tc['msg2'], 'session_id': session_id}),
        content_type='application/json').json()
    
    # Extract booking date
    resp_text = r2.get('response', '')
    if '📅 Booked Date:' in resp_text:
        date_start = resp_text.find('📅 Booked Date:') + len('📅 Booked Date:')
        date_end = resp_text.find('\n', date_start)
        booking_date = resp_text[date_start:date_end].strip()
        print(f"  📅 Appointment: {booking_date}")
        if 'Booking Confirmed' in resp_text:
            print(f"  ✅ SUCCESS")
        else:
            print(f"  ⚠ Check manual")
    else:
        print(f"  ❌ FAILED")
        print(f"  Response: {resp_text[:150]}...")

print("\n" + "=" * 70)
print("All tests completed!")
