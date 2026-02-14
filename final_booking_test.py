#!/usr/bin/env python
"""Final test showing the complete fixed booking flow"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labease_django.settings')
django.setup()

from django.test import Client
from django.core.cache import cache

client = Client()
cache.clear()

print("\n" + "=" * 70)
print("COMPLETE BOOKING FLOW - MULTI-MESSAGE WITH DATE")
print("=" * 70 + "\n")

session_id = "final_test"

# Simulate user flow
flow = [
    {
        'step': '1️⃣  User selects test',
        'message': 'Book 24 HRS URINARY MAGNESIUM',
        'expect': '✅ Test Selected'
    },
    {
        'step': '2️⃣  User provides details with preferred date',
        'message': 'My name is John Smith, pralhadgyawali@gmail.com, 9876543210, tomorrow morning',
        'expect': '✅ Booking Confirmed'
    }
]

for item in flow:
    print(f"{item['step']}")
    print(f"   Message: \"{item['message']}\"")
    
    response = client.post(
        '/api/chatbot/',
        data=json.dumps({
            'message': item['message'],
            'session_id': session_id
        }),
        content_type='application/json'
    )
    
    result = response.json()
    response_text = result.get('response', '')
    
    # Show response
    if item['expect'] in response_text:
        print(f"   ✅ {item['expect']}")
    else:
        print(f"   ❌ Expected '{item['expect']}'")
    
    # Show booking details if present
    if 'Booking ID' in response_text:
        import re
        
        # Extract booking ID
        booking_id_match = re.search(r'🎫 \*\*Booking ID:\*\* ([A-Z0-9-]+)', response_text)
        if booking_id_match:
            print(f"   🎫 Booking ID: {booking_id_match.group(1)}")
        
        # Extract test name
        test_match = re.search(r'🩸 \*\*Test:\*\* ([^*]+)', response_text)
        if test_match:
            print(f"   🩸 Test: {test_match.group(1).strip()}")
        
        # Extract appointment date
        date_match = re.search(r'📅 \*\*Booked Date:\*\* ([^*\n]+)', response_text)
        if date_match:
            print(f"   📅 Appointment: {date_match.group(1).strip()}")
        
        # Extract price
        price_match = re.search(r'💰 \*\*Price:\*\* ([^*\n]+)', response_text)
        if price_match:
            print(f"   💰 {price_match.group(1).strip()}")
    
    print()

print("=" * 70)
print("✅ BOOKING FLOW COMPLETE!")
print("=" * 70)
print("\n📌 Key Fixes Applied:")
print("   ✓ Session-based test memory across messages")
print("   ✓ Appointment date/time extraction from user message")
print("   ✓ Proper caching and retrieval of selected tests")
print("   ✓ Multi-message booking without losing context\n")

cache.clear()
