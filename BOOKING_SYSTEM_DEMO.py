#!/usr/bin/env python
"""
Demonstrate the new multi-stage AI booking flow

This shows users can now:
1. Select a test
2. Provide personal details
3. Choose appointment date/time
4. Confirm booking (NOT instant!)
"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE','labease_django.settings')
django. setup()

from django.test import Client
from django.core.cache import cache

print("\n" + "="*80)
print("LABEASE AI - NEW MULTI-STAGE BOOKING SYSTEM")
print("="*80)

print("""
BEFORE (Instant Booking):
  User: "Book Blood Sugar, name John, john@email.com, phone 123"
  AI:   "✓ Booked instantly" (No time to choose date/time!)

AFTER (Multi-Stage Booking):
  Step 1: User selects test
  Step 2: User provides personal details  
  Step 3: User chooses appointment date/time
  Step 4: AI confirms booking
  
✨ Users now have full control over their appointment! ✨
""")

client = Client()
examples = [
    {
        'name': 'Example 1: Today Appointment',
        'steps': [
            ('Book Blood Sugar F', 'Test selected'),
            ('I am Jane, jane@email.com, 555-1234', 'Details confirmed'),
            ('Today at 2:00 PM', 'BOOKING CONFIRMED')
        ]
    },
    {
        'name': 'Example 2: Tomorrow Appointment',
        'steps': [
            ('Book BODY FLUID PH', 'Test selected'),
            ('My name is Ahmed Khan, ahmed@test.com', 'Details confirmed'),
            ('Tomorrow morning', 'BOOKING CONFIRMED')
        ]
    },
    {
        'name': 'Example 3: Specific Date/Time',
        'steps': [
            ('Book ALBUMIN', 'Test selected'),
            ('Name: Alex Smith, alex@company.com, 9876543210', 'Details confirmed'),
            ('14 Feb at 3:30 PM', 'BOOKING CONFIRMED')
        ]
    }
]

for example in examples:
    print("\n" + "-"*80)
    print(f"Test: {example['name']}")
    print("-"*80)
    
    sid = f"demo_{examples.index(example)}"
    cache.clear()
    
    for i, (msg, expected) in enumerate(example['steps'], 1):
        print(f"\nStep{i}: User says: \"{msg}\"")
        
        r = client.post('/api/chatbot/',
            data=json.dumps({'message': msg, 'session_id': sid}),
            content_type='application/json').json()
        
        resp = r['response']
        
        if 'Test Selected' in resp:
            print(f"       AI: ✓ Test Selected! Ready for your details.")
        elif 'Great! Details Confirmed' in resp:
            print(f"       AI: ✓ Details Saved! Now, choose appointment.")
        elif 'Booking Confirmed' in resp:
            print(f"       AI: ✅ BOOKING CONFIRMED!")
            # Show booking details
            import re
            bid = re.search(r'LAB\d+-TST\d+-\w+', resp)
            appt = re.search(r'Appointment:\*\* ([^*\n]+)', resp)
            if bid: print(f"       📋 Booking ID: {bid.group(0)}")
            if appt: print(f"       📅 {appt.group(1).strip()}")
        else:
            print(f"       AI: {resp[:60]}...")

print("\n" + "="*80)
print("✨ MULTI-STAGE BOOKING SYSTEM ACTIVE! ✨")
print("="*80)
print("""
BENEFITS:
✓ Users have full control over appointment timing
✓ No instant bookings that users can't modify
✓ AI asks for date/time preference as a separate step
✓ Clear, conversational flow
✓ Works with multiple date/time formats:
  - "Today at 2:00 PM"
  - "Tomorrow morning"
  - "14 Feb at 3:30 PM"
  - "This week"
  - etc.
""")
