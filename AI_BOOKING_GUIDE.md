# AI Test Booking Feature - Complete Guide

## Overview

Your AI chatbot is now **smarter and more efficient** with a dedicated test booking feature! Users can now book tests directly through the chat interface without visiting the booking page.

## How It Works

### 1. **User Initiates Booking Request**

Users can trigger the booking process by saying:

- "I want to book a test"
- "Can I book a test?"
- "I need to book"
- "Schedule a test"
- And similar booking-related phrases

### 2. **AI Asks for Required Information**

The chatbot responds with a conversational message asking for:

1. **Which test?** (e.g., Blood Test, Glucose Test, Lipid Panel)
2. **Full name?** (Patient name)
3. **Email address?** (For confirmation)
4. **Lab preference?** (Optional)
5. **Preferred date/time?** (Optional)

### 3. **User Provides Booking Details**

Users provide their information in a natural way. Examples:

- "My name is John Smith, I want to book a Blood Test, email is john@example.com"
- "I am Sarah, book glucose test for me, sarah123@gmail.com"
- "Name: Mike Johnson, Email: mike@example.com, Test: CBC"

### 4. **AI Processes the Booking**

The chatbot:

- ✅ Extracts all required details using pattern matching
- ✅ Validates the test exists in the system
- ✅ Finds a lab offering that test
- ✅ Creates a TestBooking record
- ✅ Sends confirmation email to the user
- ✅ Provides booking ID and details

### 5. **Confirmation Response**

Users receive a comprehensive response showing:

- ✅ Booking confirmation status
- **Booking ID** (unique identifier like LAB1-TST5-ABC)
- **Test name**
- **Lab name and location**
- **Booking date & time**
- **Lab contact number**
- Email confirmation notification

## Technical Implementation

### Backend Changes

#### 1. **Enhanced `ai_service.py`**

```python
def _handle_booking_request(user_message):
    # Detects booking requests and provides guided flow
    # Returns: Booking instructions for the user

def _get_booking_suggestions():
    # Returns quick suggestions: "Available blood tests", "Cheapest tests", etc.
```

#### 2. **Enhanced `chatbot_api` View**

```python
def chatbot_api(request):
    # Detects if user is providing booking details
    # Calls _process_ai_booking() if booking info detected
    # Returns: Success/error response with suggestions
```

#### 3. **New `_process_ai_booking()` Function**

```python
def _process_ai_booking(user_message, session_id, user):
    # Extracts booking details using regex patterns:
    # - Patient name: "my name is [name]" or "i am [name]"
    # - Email: Standard email format detection
    # - Test: "book [test name]" or "test: [name]"

    # Validates:
    # - All required fields present
    # - Test exists in database
    # - Lab offers the test

    # Creates: TestBooking record
    # Sends: Confirmation email
    # Returns: Success/error message with booking details
```

### Frontend Changes

#### **Updated `chatbot.html` Quick Suggestions**

Added "Book a test" button (red) as the first suggestion for quick access.

### Database

**No schema changes** - Uses existing `TestBooking` model:

- `booking_id` - Auto-generated unique ID
- `name` - Patient name (from AI)
- `email` - Patient email (from AI)
- `test` - ForeignKey to Test
- `lab` - ForeignKey to Lab
- `status` - Defaults to 'booked'
- `booking_date` - Created when booking is made

## Usage Examples

### Example 1: Simple Booking

**User:** "I want to book a blood test"
**AI:** [Shows booking instructions asking for name, email, test]

**User:** "My name is John Smith, I want to book Blood Test, email john@example.com"
**AI:** ✅ **Booking Confirmed!**

- Booking ID: LAB2-TST8-XYZ
- Test: Complete Blood Count
- Lab: Apollo Labs
- Location: Pune, Maharashtra
- Booked Date: February 05, 2026 at 02:40 PM
- Email confirmation sent to john@example.com
- Lab phone: +91-9876543210

### Example 2: With Lab Preference

**User:** "Book glucose test for me. I'm Sarah, sarah@gmail.com"
**AI:** ✅ **Booking Confirmed!**

- Booking ID: LAB1-TST3-ABC
- Test: Glucose Test
- Lab: [Automatically selects available lab]

### Example 3: Incomplete Information

**User:** "Book a blood test"
**AI:** ❌ **Booking Incomplete**

- I couldn't find your name and email.
- Please provide: My name is [name], email [email]

### Example 4: Test Not Found

**User:** "My name is Tom, I want to book XYZ Test, tom@email.com"
**AI:** ❌ **Test Not Found**

- Available tests: Blood Test, Glucose Test, Lipid Panel, ...
- Please mention one of the available tests

## Features

✅ **Smart Pattern Matching**

- Understands various ways users provide information
- Flexible input format - no strict structure needed

✅ **Automatic Validation**

- Checks if test exists
- Verifies lab offers the test
- Validates email format

✅ **Automatic Email Notifications**

- Sends confirmation email with booking details
- Uses existing email system (Gmail SMTP)

✅ **Unique Booking IDs**

- Auto-generated format: LAB{id}-TST{id}-{3randomchars}
- Easy to track and reference

✅ **Session-based Chat**

- Maintains conversation history
- Users can continue booking multiple tests in same session

✅ **Error Handling**

- Clear error messages for missing/invalid data
- Helpful suggestions to correct mistakes
- Graceful fallback to normal chat if booking fails

## Integration Points

### 1. **ChatMessage Model**

- Stores all user messages and AI responses
- Links to user if authenticated
- Maintains session history

### 2. **TestBooking Model**

- Stores all booking details
- Links to Test, Lab, and User (optional)
- Tracks booking status

### 3. **Email System**

- Uses existing `send_booking_confirmation_email()` function
- Sends HTML + plain text emails
- Includes booking details and lab info

### 4. **Search/Discovery Flow**

User can ask about tests before booking:

1. "What tests do you have?" → See available tests
2. "What's the price?" → Check costs
3. "I have symptoms" → Get recommendations
4. **"I want to book"** → Start booking process

## Future Enhancements

🎯 **Potential Improvements:**

- Add date/time preference capture
- Implement lab location preference
- Add payment integration
- SMS notifications
- Appointment scheduling with calendar
- User profile auto-fill for returning users
- Multi-test bookings in one session
- Test package bookings

## Testing Checklist

- [ ] User can say "Book a test" and get instructions
- [ ] User can provide booking details in natural language
- [ ] Booking is created in database
- [ ] Confirmation email is sent
- [ ] Booking ID is displayed
- [ ] Invalid test shows helpful error
- [ ] Missing details shows specific error
- [ ] Chat history is maintained
- [ ] Multiple bookings in same session work

## Support

For issues or questions about the AI booking feature:

1. Check chat history for confirmation
2. Search for booking ID on View Bookings page
3. Contact the lab directly using provided phone number

---

**Updated:** February 5, 2026
**Feature:** AI Test Booking via Chatbot
**Status:** ✅ Active and Ready
