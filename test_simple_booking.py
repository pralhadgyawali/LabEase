#!/usr/bin/env python
"""Simple test to check server is running and working"""
import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labease_django.settings')
django.setup()

from django.test import Client

# Create a test client
client = Client()

# Simple test without date
session_id = "simple_test"

print("Testing basic booking flow...")

# First message
response_1 = client.post(
    '/api/chatbot/',
    data=json.dumps({
        'message': 'Book Blood Sugar',
        'session_id': session_id
    }),
    content_type='application/json'
)

print(f"Response 1 status: {response_1.status_code}")
if response_1.status_code == 200:
    result_1 = response_1.json()
    print(f"✅ Got response: {result_1['response'][:100]}...")
    
    # Second message with details
    response_2 = client.post(
        '/api/chatbot/',
        data=json.dumps({
            'message': 'My name is Test User, test@gmail.com, 1234567890',
            'session_id': session_id
        }),
        content_type='application/json'
    )
    
    print(f"Response 2 status: {response_2.status_code}")
    if response_2.status_code == 200:
        result_2 = response_2.json()
        print(f"Response: {result_2['response'][:200]}...")
        if 'Booking Confirmed' in result_2['response']:
            print("✅ Basic booking works!")
        else:
            print("Response keys:", result_2.keys())
    else:
        print(f"❌ Error: {response_2.status_code}")
        print(response_2.content[:500])
else:
    print(f"❌ Error: {response_1.status_code}")
    print(response_1.content[:500])
