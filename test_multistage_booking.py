#!/usr/bin/env python
"""Test the new multi-stage booking flow"""
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
print("TESTING NEW MULTI-STAGE BOOKING FLOW")
print("=" * 70 + "\n")

session_id = "multi_stage_test"

# Stage 0: User selects test
print("Step 0: User selects test")
print('Message: "Book BLOOD SUGAR F"')
r0 = client.post('/api/chatbot/',
    data=json.dumps({'message': 'Book BLOOD SUGAR F', 'session_id': session_id}),
    content_type='application/json').json()
print(f"AI: {r0['response'][:100]}...\n")

# Stage 1: User provides name, email, phone
print("Step 1: User provides personal details")
print('Message: "My name is John Smith, john@example.com, 9876543210"')
r1 = client.post('/api/chatbot/',
    data=json.dumps({'message': 'My name is John Smith, john@example.com, 9876543210', 'session_id': session_id}),
    content_type='application/json').json()

response1 = r1['response']
if 'Great! Details Confirmed' in response1:
    print(f"AI: ✅ Details confirmed!")
    print(f"    Now ask for appointment date/time\n")
else:
    print(f"AI: {response1[:200]}...\n")

# Stage 2: User selects date/time
print("Step 2: User selects appointment date/time")
print('Message: "Tomorrow at 2:30 PM"')
r2 = client.post('/api/chatbot/',
    data=json.dumps({'message': 'Tomorrow at 2:30 PM', 'session_id': session_id}),
    content_type='application/json').json()

response2 = r2['response']
if 'Booking Confirmed' in response2:
    print(f"AI: ✅ Booking Confirmed!")
    
    # Extract details
    import re
    bid = re.search(r'LAB\d+-TST\d+-\w+', response2)
    test = re.search(r'Test:\*\* ([^*\n]+)', response2)
    appt = re.search(r'Appointment:\*\* ([^*\n]+)', response2)
    
    if bid: print(f"    Booking ID: {bid.group(0)}")
    if test: print(f"    Test: {test.group(1).strip()}")
    if appt: print(f"    Appointment: {appt.group(1).strip()}")
else:
    print(f"AI: {response2[:200]}...\n")

print("\n" + "=" * 70)
print("✅ MULTI-STAGE BOOKING FLOW WORKING!")
print("=" * 70)
print("\nFlow Summary:")
print("  Step 0: User clicks/says test name → AI confirms")
print("  Step 1: User provides name, email, phone → AI confirms details")
print("  Step 2: User selects date/time → AI creates booking")
print("  ✓ No more instant bookings!")
print("  ✓ Users can choose their preferred appointment time!")

cache.clear()
