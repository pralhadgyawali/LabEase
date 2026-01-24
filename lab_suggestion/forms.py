from django import forms
from .models import Lab, Test, ContactMessage
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
        fields = ['name', 'description', 'price', 'popularity']

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']

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