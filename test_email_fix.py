#!/usr/bin/env python
"""
Test email configuration
Run: python test_email_fix.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'labease_django.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings

print("=" * 60)
print("EMAIL CONFIGURATION TEST")
print("=" * 60)
print(f"Email Backend: {settings.EMAIL_BACKEND}")
print(f"Email Host: {settings.EMAIL_HOST}")
print(f"Email Port: {settings.EMAIL_PORT}")
print(f"Email User: {settings.EMAIL_HOST_USER}")
print(f"Use SSL: {settings.EMAIL_USE_SSL}")
print(f"Use TLS: {settings.EMAIL_USE_TLS}")
print("=" * 60)

try:
    # Send test email
    send_mail(
        subject='LabEase Email Test ✅',
        message='If you received this email, your SMTP configuration is working correctly! 🎉',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=['pralhadlearns@gmail.com'],
        html_message='<h2>LabEase Email Test</h2><p>If you received this email, your SMTP configuration is working correctly! 🎉</p>'
    )
    print("✅ SUCCESS! Email sent successfully!")
    print("Check your inbox for the test email.")
except Exception as e:
    print(f"❌ FAILED! Error: {str(e)}")
    print("\nTroubleshooting:")
    print("1. Did you generate a NEW app password from Google?")
    print("2. Did you paste it without spaces?")
    print("3. Is 2-Step Verification enabled on your Google Account?")
    print("4. Restart Django server after changing the password")
