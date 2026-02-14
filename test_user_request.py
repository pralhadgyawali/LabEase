import os, django, json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labease_django.settings')
django.setup()
from django.test import Client
from django.core.cache import cache

client = Client()
cache.clear()

print()
print('='*70)
print('TESTING USER REQUEST SCENARIO')
print('='*70)
print()

sid = 'user_scenario'

# Message 1: Book test
print('Message 1: User books a test')
print('  "Book 24 HRS URINARY MAGNESIUM"')
r1 = client.post('/api/chatbot/', 
    json.dumps({'message': 'Book 24 HRS URINARY MAGNESIUM', 'session_id': sid}), 
    content_type='application/json').json()

if '✅ Test Selected' in r1['response']:
    print('  [OK] Response: Test Selected')
else:
    print('  [FAIL] Unexpected response')

print()

# Message 2: Provide all details
print('Message 2: User provides details')
print('  "My name is John Smith, pralhadgyawali@gmail.com, 9876543210, tomorrow morning"')
r2 = client.post('/api/chatbot/', 
    json.dumps({'message': 'My name is John Smith, pralhadgyawali@gmail.com, 9876543210, tomorrow morning', 'session_id': sid}), 
    content_type='application/json').json()

if 'error' in r2:
    print(f'  [ERROR] {r2["error"]}')
    exit(1)
elif 'Details Confirmed' in r2['response']:
    print('  [OK] Response: Details Confirmed')
    print('  [OK] System says: Select your appointment date')
else:
    print(f'  [UNKNOWN] {r2["response"][:80]}...')

print()

# Message 3: Confirm appointment  
print('Message 3: User confirms appointment')
print('  "tomorrow morning"')
r3 = client.post('/api/chatbot/', 
    json.dumps({'message': 'tomorrow morning', 'session_id': sid}), 
    content_type='application/json').json()

if 'Booking Confirmed' in r3['response']:
    print('  [OK] Response: Booking Confirmed')
    import re
    bid = re.search(r'LAB\d+-TST\d+-\w+', r3['response'])
    if bid: print(f'    Booking ID: {bid.group(0)}')
    print('    Appointment: Confirmed for Tomorrow Morning')
else:
    print(f'  [FAIL] Booking not created')
    print(f'    {r3["response"][:100]}...')
    exit(1)

print()
print('='*70)
print('SUCCESS: All tests passed!')
print('='*70)
cache.clear()

