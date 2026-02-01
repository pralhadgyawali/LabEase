from django.db import models
from django.contrib.auth.models import User

class Test(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    # popularity = models.IntegerField(default=0) # Removed this line

    def __str__(self):
        return self.name

class Lab(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    phone_number = models.CharField(max_length=15)
    contact_email = models.EmailField(max_length=100, default='noreply@example.com')
    contact_phone = models.CharField(max_length=20, default='000-000-0000')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    tests = models.ManyToManyField(Test, through='LabTestDetail', blank=True)

class LabTestDetail(models.Model):
    lab = models.ForeignKey(Lab, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE)
    lab_specific_description = models.TextField(blank=True, null=True)
    lab_specific_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return f'{self.lab.name} - {self.test.name}'

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True, null=True, help_text='Contact phone number for follow-up')
    message = models.TextField()
    lab = models.ForeignKey(Lab, on_delete=models.SET_NULL, null=True, blank=True)
    recipient_admin = models.BooleanField(default=False)
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.lab:
            return f'Message to {self.lab.name} from {self.name} at {self.sent_at.strftime("%Y-%m-%d %H:%M")}'
        elif self.recipient_admin:
            return f'Message to Admin from {self.name} at {self.sent_at.strftime("%Y-%m-%d %H:%M")}'
        return f'Message from {self.name} at {self.sent_at.strftime("%Y-%m-%d %H:%M")}'

class ChatMessage(models.Model):
    """Model to store chatbot conversation history"""
    session_id = models.CharField(max_length=100, db_index=True)
    user_message = models.TextField()
    bot_response = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Chat {self.session_id} - {self.created_at.strftime("%Y-%m-%d %H:%M")}'

class AIRecommendation(models.Model):
    """Model to store AI-powered test recommendations"""
    symptoms = models.TextField()
    recommended_tests = models.ManyToManyField(Test)
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Recommendation for: {self.symptoms[:50]}...'
