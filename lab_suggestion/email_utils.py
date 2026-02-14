"""
Email sending utilities for LabEase
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


def send_booking_confirmation_email(booking):
    """
    Send booking confirmation email to the user
    """
    try:
        # Prepare email context
        context = {
            'booking': booking,
            'test': booking.test,
            'lab': booking.lab,
            'user_name': booking.name,
            'booking_id': booking.booking_id,
        }
        
        # Render HTML and plain text versions
        html_message = render_to_string('emails/booking_confirmation_email.html', context)
        plain_message = render_to_string('emails/booking_confirmation_email.txt', context)
        
        # Send email
        send_mail(
            subject=f'Booking Confirmation - {booking.test.name} at {booking.lab.name}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def send_booking_update_email(booking):
    """
    Send booking update notification email to the user
    """
    try:
        context = {
            'booking': booking,
            'test': booking.test,
            'lab': booking.lab,
            'user_name': booking.name,
            'booking_id': booking.booking_id,
            'action': 'updated',
        }
        
        html_message = render_to_string('emails/booking_notification_email.html', context)
        plain_message = render_to_string('emails/booking_notification_email.txt', context)
        
        send_mail(
            subject=f'Booking Updated - {booking.test.name} at {booking.lab.name}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False


def send_booking_cancellation_email(booking):
    """
    Send booking cancellation notification email to the user
    """
    try:
        context = {
            'booking': booking,
            'test': booking.test,
            'lab': booking.lab,
            'user_name': booking.name,
            'booking_id': booking.booking_id,
            'action': 'cancelled',
        }
        
        html_message = render_to_string('emails/booking_cancellation_email.html', context)
        plain_message = render_to_string('emails/booking_cancellation_email.txt', context)
        
        send_mail(
            subject=f'Booking Cancelled - {booking.test.name} at {booking.lab.name}',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False
