# LabEase Email Configuration Guide

## Email Setup Instructions

The LabEase booking system now sends automated confirmation emails to users when they:

1. Complete a booking
2. Update a booking
3. Cancel a booking

### Setting Up Gmail (Recommended for Development)

1. **Enable 2-Factor Authentication on your Gmail account:**
   - Go to https://myaccount.google.com/security
   - Click on "2-Step Verification"
   - Follow the steps to enable it

2. **Create an App Password:**
   - After enabling 2FA, go back to Security settings
   - Find "App passwords" (it appears only if you have 2FA enabled)
   - Select "Mail" and "Windows Computer"
   - Google will generate a 16-character password
   - Copy this password

3. **Update Django Settings:**
   - Open `labease_django/settings.py`
   - Find the EMAIL configuration section
   - Update these settings:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@gmail.com'  # Your Gmail address
EMAIL_HOST_PASSWORD = 'your-app-password'  # 16-character App Password from step 2
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'  # Your Gmail address
```

### For Development/Testing

If you want to see emails in the console instead of actually sending them, use:

```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

This will print emails to the Django development server console.

### Alternative Email Services

You can also use other services like:

#### SendGrid:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = 'your-sendgrid-api-key'
DEFAULT_FROM_EMAIL = 'your-email@example.com'
```

#### Mailgun:

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'postmaster@yourdomain.mailgun.org'
EMAIL_HOST_PASSWORD = 'your-mailgun-password'
DEFAULT_FROM_EMAIL = 'your-email@example.com'
```

### Email Features

The system automatically sends:

1. **Booking Confirmation Email** - Sent when a user completes a booking
   - Includes booking ID, test details, lab information
   - Contains preferred appointment date
   - Provides link to check booking status

2. **Booking Update Notification** - Sent when a booking is updated
   - Notifies of date/detail changes
   - Shows updated booking information

3. **Booking Cancellation Email** - Sent when a booking is cancelled
   - Confirms cancellation
   - Provides lab contact information for rescheduling

### Email Templates

Email templates are located in:

- `lab_suggestion/templates/emails/booking_confirmation_email.html` - HTML version
- `lab_suggestion/templates/emails/booking_confirmation_email.txt` - Plain text version
- `lab_suggestion/templates/emails/booking_notification_email.html`
- `lab_suggestion/templates/emails/booking_notification_email.txt`
- `lab_suggestion/templates/emails/booking_cancellation_email.html`
- `lab_suggestion/templates/emails/booking_cancellation_email.txt`

You can customize these templates to match your branding.

### Testing Emails

To test the email functionality:

1. Start the development server
2. Create a test booking
3. Check your email inbox for the confirmation

Or use the console backend to see emails printed in the terminal.

### Troubleshooting

**Issue:** "SMTPAuthenticationError: Application-specific password required"

- **Solution:** Make sure you're using an App Password (16 characters), not your regular Gmail password

**Issue:** Emails not being sent but no error appears

- **Solution:** Make sure 2-Factor Authentication is enabled on your Gmail account

**Issue:** "SMTP port connection refused"

- **Solution:** Check firewall settings or use port 465 with SSL instead of port 587

**Issue:** Development server shows "SMTPException"

- **Solution:** Switch to console backend temporarily: `EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'`

### Security Notes

- Never commit your EMAIL_HOST_PASSWORD to version control
- Use environment variables for production:

```python
import os

EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL')
```

- Keep your App Passwords secure
- For production, use a dedicated email service provider
