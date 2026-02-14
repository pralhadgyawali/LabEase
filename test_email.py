#!/usr/bin/env python
"""
Test script to verify email configuration
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labease_django.settings')
sys.path.insert(0, r'c:\Users\Acer\Desktop\labease-ai')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 60)
print("LabEase Email Configuration Test")
print("=" * 60)

print(f"\n✓ EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
print(f"✓ EMAIL_HOST: {settings.EMAIL_HOST}")
print(f"✓ EMAIL_PORT: {settings.EMAIL_PORT}")
print(f"✓ EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
print(f"✓ EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
print(f"✓ DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")

print("\n" + "=" * 60)
print("Sending Test Email...")
print("=" * 60)

try:
    send_mail(
        subject='LabEase Test Email',
        message='This is a test email from LabEase to verify email configuration.',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['pralhadlearns@gmail.com'],
        fail_silently=False,
    )
    print("\n✓ Test email sent successfully!")
except Exception as e:
    print(f"\n✗ Error sending email: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test Complete")
print("=" * 60)
