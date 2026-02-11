"""
Django management command to cleanup junk test data
Usage: python manage.py cleanup_junk_tests
"""

from django.core.management.base import BaseCommand
from lab_suggestion.models import Test

class Command(BaseCommand):
    help = 'Remove junk test records from database'

    def handle(self, *args, **options):
        # Define patterns for junk tests
        junk_keywords = [
            'AMBULANCE', 'VENTILATOR', 'CABIN', 'BED', 'ICU', 'SSCU',
            'POST ANESTHESIA', 'TRANSPLANT', 'OBSERVATION', 'CHARGE'
        ]
        
        # Single letter tests
        single_letter_tests = Test.objects.filter(name__in=['a', 'u', 'z', 'x', 'acer', 'xray'])
        
        # Find tests with junk keywords
        junk_tests = Test.objects.none()
        for keyword in junk_keywords:
            junk_tests = junk_tests | Test.objects.filter(name__icontains=keyword)
        
        junk_tests = junk_tests | single_letter_tests
        
        count = junk_tests.count()
        
        if count > 0:
            self.stdout.write(f"Found {count} junk test(s)")
            self.stdout.write("\nTests to be deleted:")
            for test in junk_tests[:20]:
                self.stdout.write(f"  - {test.name}")
            
            if junk_tests.count() > 20:
                self.stdout.write(f"  ... and {junk_tests.count() - 20} more")
            
            # Confirm before deleting
            confirm = input("\nDelete these junk tests? (yes/no): ")
            if confirm.lower() == 'yes':
                deleted = junk_tests.delete()
                self.stdout.write(self.style.SUCCESS(f"✓ Deleted {deleted[0]} test(s)"))
                self.stdout.write(f"✓ Remaining valid tests: {Test.objects.count()}")
            else:
                self.stdout.write("Operation cancelled")
        else:
            self.stdout.write("No junk tests found")
