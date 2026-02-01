"""
Management command to load sample data for LabEase
Run with: python manage.py load_sample_data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from lab_suggestion.models import Lab, Test, LabTestDetail, ContactMessage, ChatMessage
from django.utils import timezone
from datetime import timedelta
import random


class Command(BaseCommand):
    help = 'Loads sample data for tests, labs, and associations'

    def handle(self, *args, **options):
        self.stdout.write('Loading sample data...')
        
        # Create admin user if it doesn't exist
        admin_user, admin_created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@labease.com',
                'is_superuser': True,
                'is_staff': True,
                'is_active': True
            }
        )
        if admin_created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created admin user: admin (password: admin123)'))
        else:
            # Ensure admin has correct permissions
            if not admin_user.is_superuser:
                admin_user.is_superuser = True
                admin_user.is_staff = True
                admin_user.save()
                self.stdout.write(self.style.SUCCESS('Updated admin user permissions'))
        
        # Sample tests data
        sample_tests = [
            {'name': 'Complete Blood Count (CBC)', 'description': 'Measures red blood cells, white blood cells, and platelets', 'price': 45.00},
            {'name': 'Basic Metabolic Panel (BMP)', 'description': 'Tests glucose, electrolytes, and kidney function', 'price': 55.00},
            {'name': 'Lipid Panel', 'description': 'Measures cholesterol and triglycerides', 'price': 50.00},
            {'name': 'Thyroid Stimulating Hormone (TSH)', 'description': 'Tests thyroid function', 'price': 60.00},
            {'name': 'Hemoglobin A1C', 'description': 'Measures average blood sugar over 3 months', 'price': 65.00},
            {'name': 'Glucose Test', 'description': 'Measures blood sugar levels', 'price': 40.00},
            {'name': 'Liver Function Test (LFT)', 'description': 'Tests liver enzymes and function', 'price': 70.00},
            {'name': 'Kidney Function Test', 'description': 'Tests creatinine and BUN levels', 'price': 55.00},
            {'name': 'Cardiac Troponin', 'description': 'Tests for heart muscle damage', 'price': 85.00},
            {'name': 'Vitamin D Test', 'description': 'Measures vitamin D levels', 'price': 75.00},
            {'name': 'Vitamin B12 Test', 'description': 'Measures B12 levels', 'price': 70.00},
            {'name': 'COVID-19 PCR Test', 'description': 'Detects COVID-19 virus', 'price': 100.00},
            {'name': 'Urinalysis', 'description': 'Complete urine analysis', 'price': 35.00},
            {'name': 'Chest X-Ray', 'description': 'X-ray imaging of the chest', 'price': 120.00},
            {'name': 'ECG/EKG', 'description': 'Electrocardiogram test', 'price': 80.00},
            {'name': 'T3 and T4 Test', 'description': 'Comprehensive thyroid function test', 'price': 90.00},
            {'name': 'ALT and AST Test', 'description': 'Liver enzyme tests', 'price': 65.00},
            {'name': 'Creatinine Test', 'description': 'Kidney function marker', 'price': 45.00},
            {'name': 'BUN Test', 'description': 'Blood urea nitrogen test', 'price': 40.00},
            {'name': 'Bilirubin Test', 'description': 'Liver function marker', 'price': 50.00},
        ]
        
        # Create or get tests
        created_tests = []
        for test_data in sample_tests:
            test, created = Test.objects.get_or_create(
                name=test_data['name'],
                defaults={
                    'description': test_data['description'],
                    'price': test_data['price']
                }
            )
            created_tests.append(test)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created test: {test.name}'))
            else:
                self.stdout.write(f'Test already exists: {test.name}')
        
        # Sample labs data - Nepali locations
        sample_labs = [
            {
                'username': 'citylab_kathmandu',
                'email': 'info@citylabkathmandu.com',
                'name': 'City Lab Kathmandu',
                'address': 'New Road, Kathmandu',
                'city': 'Kathmandu',
                'state': 'Bagmati',
                'zip_code': '44600',
                'phone_number': '01-4221234',
                'contact_email': 'info@citylabkathmandu.com',
                'contact_phone': '01-4221234'
            },
            {
                'username': 'medtest_lalitpur',
                'email': 'contact@medtestlalitpur.com',
                'name': 'MedTest Lalitpur',
                'address': 'Patan Durbar Square, Lalitpur',
                'city': 'Lalitpur',
                'state': 'Bagmati',
                'zip_code': '44700',
                'phone_number': '01-5525678',
                'contact_email': 'contact@medtestlalitpur.com',
                'contact_phone': '01-5525678'
            },
            {
                'username': 'healthlab_bhaktapur',
                'email': 'info@healthlabbhaktapur.com',
                'name': 'Health Lab Bhaktapur',
                'address': 'Bhaktapur Durbar Square, Bhaktapur',
                'city': 'Bhaktapur',
                'state': 'Bagmati',
                'zip_code': '44800',
                'phone_number': '01-6612345',
                'contact_email': 'info@healthlabbhaktapur.com',
                'contact_phone': '01-6612345'
            },
            {
                'username': 'quicktest_kathmandu',
                'email': 'support@quicktestkathmandu.com',
                'name': 'QuickTest Kathmandu',
                'address': 'Thamel, Kathmandu',
                'city': 'Kathmandu',
                'state': 'Bagmati',
                'zip_code': '44600',
                'phone_number': '01-4701234',
                'contact_email': 'support@quicktestkathmandu.com',
                'contact_phone': '01-4701234'
            },
            {
                'username': 'premium_labs_lalitpur',
                'email': 'info@premiumlabslalitpur.com',
                'name': 'Premium Labs Lalitpur',
                'address': 'Jawalakhel, Lalitpur',
                'city': 'Lalitpur',
                'state': 'Bagmati',
                'zip_code': '44700',
                'phone_number': '01-5527890',
                'contact_email': 'info@premiumlabslalitpur.com',
                'contact_phone': '01-5527890'
            },
        ]
        
        # Create labs with users
        created_labs = []
        for lab_data in sample_labs:
            user, user_created = User.objects.get_or_create(
                username=lab_data['username'],
                defaults={
                    'email': lab_data['email'],
                    'is_active': True
                }
            )
            
            if user_created:
                user.set_password('sample123')  # Default password for sample labs
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created user: {user.username}'))
            
            lab, lab_created = Lab.objects.get_or_create(
                user=user,
                defaults={
                    'name': lab_data['name'],
                    'address': lab_data['address'],
                    'city': lab_data['city'],
                    'state': lab_data['state'],
                    'zip_code': lab_data['zip_code'],
                    'phone_number': lab_data['phone_number'],
                    'contact_email': lab_data['contact_email'],
                    'contact_phone': lab_data['contact_phone']
                }
            )
            created_labs.append(lab)
            if lab_created:
                self.stdout.write(self.style.SUCCESS(f'Created lab: {lab.name}'))
            else:
                self.stdout.write(f'Lab already exists: {lab.name}')
        
        # Associate tests with labs (each lab gets a random selection of tests)
        for lab in created_labs:
            # Each lab gets 8-15 random tests
            num_tests = random.randint(8, min(15, len(created_tests)))
            lab_tests = random.sample(created_tests, num_tests)
            
            for test in lab_tests:
                lab.tests.add(test)
                # Create LabTestDetail with potentially different pricing
                lab_test_detail, created = LabTestDetail.objects.get_or_create(
                    lab=lab,
                    test=test,
                    defaults={
                        'lab_specific_price': float(test.price) * random.uniform(0.9, 1.1),  # ±10% variation
                        'lab_specific_description': f'{test.description} - Available at {lab.name}'
                    }
                )
            
            self.stdout.write(f'Associated {len(lab_tests)} tests with {lab.name}')
        
        # Create sample contact messages - more comprehensive
        sample_messages = [
            # Messages to labs
            {
                'name': 'John Doe',
                'email': 'john.doe@example.com',
                'message': 'I would like to book a Complete Blood Count (CBC) test. What are your available time slots?',
                'to_lab': True
            },
            {
                'name': 'Sarah Smith',
                'email': 'sarah.smith@example.com',
                'message': 'I need to get a Lipid Panel test done. Can you please provide information about pricing and availability?',
                'to_lab': True
            },
            {
                'name': 'Michael Johnson',
                'email': 'michael.j@example.com',
                'message': 'I have diabetes symptoms and need to book a Hemoglobin A1C test. Please let me know when I can schedule an appointment.',
                'to_lab': True
            },
            {
                'name': 'Emily Brown',
                'email': 'emily.brown@example.com',
                'message': 'I need a Thyroid Stimulating Hormone (TSH) test. What is the procedure and how long does it take?',
                'to_lab': True
            },
            {
                'name': 'David Wilson',
                'email': 'david.wilson@example.com',
                'message': 'I would like to book a Liver Function Test (LFT). Are you open on weekends?',
                'to_lab': True
            },
            {
                'name': 'Lisa Anderson',
                'email': 'lisa.anderson@example.com',
                'message': 'I need a COVID-19 PCR Test urgently. Do you have same-day results available?',
                'to_lab': True
            },
            {
                'name': 'Raj Kumar',
                'email': 'raj.kumar@example.com',
                'message': 'I would like to book a Glucose Test for my annual health checkup. What is the best time to visit?',
                'to_lab': True
            },
            {
                'name': 'Priya Sharma',
                'email': 'priya.sharma@example.com',
                'message': 'I need to get a Vitamin D Test done. Can you provide information about the test and pricing?',
                'to_lab': True
            },
            {
                'name': 'Amit Patel',
                'email': 'amit.patel@example.com',
                'message': 'I would like to book a Kidney Function Test. What are your operating hours?',
                'to_lab': True
            },
            {
                'name': 'Sita Thapa',
                'email': 'sita.thapa@example.com',
                'message': 'I need an ECG/EKG test. Do you have walk-in appointments available?',
                'to_lab': True
            },
            # Messages to admin
            {
                'name': 'Robert Taylor',
                'email': 'robert.taylor@example.com',
                'message': 'I have a question about your services and pricing. Can someone contact me?',
                'to_admin': True
            },
            {
                'name': 'Jennifer Martinez',
                'email': 'jennifer.m@example.com',
                'message': 'I would like to register my lab on your platform. How can I do that?',
                'to_admin': True
            },
            {
                'name': 'Dr. Sanjay Maharjan',
                'email': 'sanjay.maharjan@example.com',
                'message': 'I am interested in partnering with LabEase. Can you provide more information about the registration process?',
                'to_admin': True
            },
            {
                'name': 'Health Care Center',
                'email': 'info@healthcarecenter.com',
                'message': 'We are a new medical facility and would like to list our services on your platform.',
                'to_admin': True
            },
        ]
        
        created_messages = []
        for i, msg_data in enumerate(sample_messages):
            # Distribute messages to different labs
            if msg_data.get('to_lab') and created_labs:
                lab = random.choice(created_labs)
                # Create message with timestamp spread over last 7 days
                sent_at = timezone.now() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
                message = ContactMessage.objects.create(
                    name=msg_data['name'],
                    email=msg_data['email'],
                    message=msg_data['message'],
                    lab=lab,
                    recipient_admin=False,
                    sent_at=sent_at
                )
                created_messages.append(message)
                self.stdout.write(f'Created message to {lab.name} from {msg_data["name"]}')
            elif msg_data.get('to_admin'):
                sent_at = timezone.now() - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23))
                message = ContactMessage.objects.create(
                    name=msg_data['name'],
                    email=msg_data['email'],
                    message=msg_data['message'],
                    lab=None,
                    recipient_admin=True,
                    sent_at=sent_at
                )
                created_messages.append(message)
                self.stdout.write(f'Created message to admin from {msg_data["name"]}')
        
        # Create sample chat messages
        sample_chats = [
            {
                'user_message': 'What tests do you have?',
                'bot_response': 'We offer a wide range of medical tests including Complete Blood Count (CBC), Lipid Panel, Thyroid tests, Liver Function Tests, and many more. You can search for specific tests on our homepage!'
            },
            {
                'user_message': 'Find labs near me',
                'bot_response': 'I can help you find labs! Please use our search feature on the homepage to search for tests, and you\'ll see all labs offering that test in your area.'
            },
            {
                'user_message': 'What is the price of blood test?',
                'bot_response': 'Blood test prices vary depending on the type of test. A Complete Blood Count (CBC) typically costs around Rs. 45-55. Use our search feature to find specific test prices from different labs!'
            },
        ]
        
        # Create chat messages for admin user if exists
        admin_user = User.objects.filter(username='admin').first()
        if admin_user:
            for chat_data in sample_chats:
                session_id = f'sample_session_{random.randint(1000, 9999)}'
                sent_at = timezone.now() - timedelta(days=random.randint(0, 5), hours=random.randint(0, 23))
                chat = ChatMessage.objects.create(
                    session_id=session_id,
                    user_message=chat_data['user_message'],
                    bot_response=chat_data['bot_response'],
                    user=admin_user,
                    created_at=sent_at
                )
                self.stdout.write(f'Created chat message: {chat_data["user_message"][:30]}...')
        
        self.stdout.write(self.style.SUCCESS('\n✅ Sample data loaded successfully!'))
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'   • {len(created_tests)} tests')
        self.stdout.write(f'   • {len(created_labs)} labs')
        self.stdout.write(f'   • {len(created_messages)} contact messages')
        self.stdout.write(f'   • Admin user: admin (password: admin123)')
        self.stdout.write(f'\n🔑 Lab credentials (password: sample123):')
        for lab in created_labs:
            self.stdout.write(f'   • {lab.user.username} - {lab.name}')
        self.stdout.write(f'\n💡 You can now login to the admin dashboard to see all the sample data!')
