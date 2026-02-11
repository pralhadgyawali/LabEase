import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labease_django.settings')
django.setup()
from django.test import Client
from django.core.cache import cache

client = Client()
sid = 'test_fixed'
cache.clear()

print('='*70)
print('Test: Complete Booking Flow')
print('='*70)
print()

print('[STAGE 1] User selects test')
print('  User: Book 24 HRS URINARY MAGNESIUM')
r1 = client.post('/api/chatbot/', json.dumps({'message': 'Book 24 HRS URINARY MAGNESIUM', 'session_id': sid}), content_type='application/json').json()
print('  ✓ Test Selected')
print()

print('[STAGE 2] User provides all details including date/time')
print('  User: My name is John Smith, pralhadgyawali@gmail.com, 9876543210, tomorrow morning')
r2 = client.post('/api/chatbot/', json.dumps({'message': 'My name is John Smith, pralhadgyawali@gmail.com, 9876543210, tomorrow morning', 'session_id': sid}), content_type='application/json').json()
if 'error' in r2:
    print(f'  ✗ ERROR: {r2["error"]}')
else:
    if 'Details Confirmed' in r2['response']:
        print('  ✓ Details Confirmed - Waiting for appointment selection')
    else:
        print(f'  ? Unexpected response')
print()

print('[STAGE 3] User confirms appointment')        
print('  User: Yes, tomorrow morning is good')
r3 = client.post('/api/chatbot/', json.dumps({'message': 'yes, tomorrow morning is good', 'session_id': sid}), content_type='application/json').json()
if 'Booking Confirmed' in r3.get('response', ''):
    print('  ✓ BOOKING CREATED!')
    import re
    bid = re.search(r'LAB\d+-TST\d+-\w+', r3['response'])
    if bid: print(f'    ID: {bid.group(0)}')
else:
    print(f'  Response: {r3.get("response", "N/A")[:100]}...')

print()
print('='*70)
cache.clear()
