from django import forms
from .models import Lab, Test, ContactMessage
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
import re

class LabUserRegistrationForm(UserCreationForm):
    name = forms.CharField(max_length=100, help_text='The name of the lab.')
    address = forms.CharField(widget=forms.Textarea, help_text='The address of the lab.')
    contact_email = forms.EmailField(help_text='A contact email for the lab.')
    contact_phone = forms.CharField(max_length=20, help_text='A contact phone number for the lab.')

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email',)
    
    def clean_contact_phone(self):
        """Validate that phone number contains at least 10 digits"""
        phone = self.cleaned_data.get('contact_phone')
        if phone:
            # Remove common phone formatting characters
            digits_only = re.sub(r'\D', '', phone)
            if len(digits_only) < 10:
                raise forms.ValidationError('Phone number must contain at least 10 digits.')
        return phone
    
    def clean_name(self):
        """Validate that lab name is not empty or just whitespace"""
        name = self.cleaned_data.get('name')
        if name and not name.strip():
            raise forms.ValidationError('Lab name cannot be empty.')
        return name

class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ['name', 'description', 'price'] # Removed 'popularity'
    
    def clean_price(self):
        """Validate that price is positive"""
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError('Price cannot be negative.')
        return price
    
    def clean_name(self):
        """Validate that test name is not empty"""
        name = self.cleaned_data.get('name')
        if name and not name.strip():
            raise forms.ValidationError('Test name cannot be empty.')
        return name

class ContactForm(forms.ModelForm):
    recipient_choice = forms.ChoiceField(choices=[], required=True, label="Send message to")

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message', 'lab', 'recipient_admin']
        widgets = {
            'lab': forms.HiddenInput(),
            'recipient_admin': forms.HiddenInput(),
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