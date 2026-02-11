"""
Cleanup script to remove junk test records from database
Run with: python manage.py shell < cleanup_tests.py
"""

from lab_suggestion.models import Test

# Tests to delete - obviously invalid or junk data
junk_test_names = [
    'a', 'u', 'z', 'acer',  # Single letters and brand names
    'AMBULANCE CHARG', 'CABIN BED', 'GENERAL BED',  # Not medical tests
    'HIGH CARE BED', 'SSCU', 'ICU', 'OBSERVATION BED',  # Facility charges
    'POST ANESTHESIA', 'TRANSPLANT ROOM', 'TRIPLE BED',  # Bed types
    'VENTILATOR CHARGE',  # Equipment charges
]

# Find and delete junk tests
deleted_count = 0
for test_name in junk_test_names:
    deleted, _ = Test.objects.filter(name__icontains=test_name).delete()
    if deleted > 0:
        print(f"✓ Deleted {deleted} test(s) containing: {test_name}")
        deleted_count += deleted

print(f"\n✓ Total deleted: {deleted_count}")
print(f"✓ Remaining tests: {Test.objects.count()}")
