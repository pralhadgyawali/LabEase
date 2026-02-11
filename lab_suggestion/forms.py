from django import forms
from .models import Lab, Test, ContactMessage, TestBooking
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class LabUserRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=100, help_text='The name of the lab.')
    address = forms.CharField(widget=forms.Textarea, help_text='The address of the lab.')
    contact_email = forms.EmailField(help_text='A contact email for the lab.')
    contact_phone = forms.CharField(max_length=20, help_text='A contact phone number for the lab.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['name', 'description', 'price'] # Removed 'popularity'

class ContactForm(forms.ModelForm):
    recipient_choice = forms.ChoiceField(choices=[], required=True, label="Send message to")
    phone_number = forms.CharField(max_length=20, required=False, label="Phone Number", help_text="Optional - for lab to contact you")

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone_number', 'message', 'lab', 'recipient_admin']
        widgets = {
            'lab': forms.HiddenInput(),
            'recipient_admin': forms.HiddenInput(),
            'phone_number': forms.TextInput(attrs={'placeholder': 'e.g., 01-XXXXXXX or +977-XXXXXXXXX'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        labs = Lab.objects.all()
        choices = [('admin', 'System Admin')]
        choices.extend([(str(lab.id), lab.name) for lab in labs])
        self.fields['recipient_choice'].choices = choices

class LabForm(forms.ModelForm):
    class Meta:
        model = Lab
        fields = ['name', 'address', 'city', 'state', 'zip_code', 'phone_number', 'contact_email', 'contact_phone', 'latitude', 'longitude', 'tests']

# New admin-specific lab edit form
class AdminLabEditForm(forms.ModelForm):
    username = forms.CharField(max_length=150, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.')
    email = forms.EmailField(required=False)

    class Meta:
        model = Lab
        fields = ['name', 'address', 'contact_email', 'contact_phone']

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField()


class TestBookingForm(forms.ModelForm):
    """Form for booking tests"""
    name = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full Name',
            'required': 'required'
        }),
        label='Full Name',
        max_length=100,
        help_text='Enter your full name'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com',
            'required': 'required'
        }),
        label='Email Address'
    )
    booking_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'placeholder': 'Select booking date and time'
        }),
        label='Preferred Test Date & Time'
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Any special requirements or notes'
        }),
        required=False,
        label='Additional Notes'
    )

    class Meta:
        model = TestBooking
        fields = ['name', 'email', 'booking_date', 'notes']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'booking_date': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Any special requirements or notes'
            }),
        }
