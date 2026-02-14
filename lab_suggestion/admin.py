from django.contrib import admin
from .models import Test, Lab, LabTestDetail, ContactMessage, ChatMessage, AIRecommendation, ContactMessage, ChatMessage, AIRecommendation

class LabTestDetailInline(admin.TabularInline):
    model = LabTestDetail
    extra = 1  # How many empty forms to display

@admin.register(Lab)
class LabAdmin(admin.ModelAdmin):
    inlines = [LabTestDetailInline]
    list_display = ('name', 'address', 'city', 'state', 'phone_number', 'contact_email')
    search_fields = ('name', 'city', 'state')

@admin.register(Test)
class TestAdmin(admin.ModelAdmin):
    list_display = ('name', 'price') # Removed 'popularity'
    search_fields = ('name', 'description')
    # list_filter = ('popularity',) # Removed this line

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'lab', 'recipient_admin', 'sent_at')
    list_filter = ('recipient_admin', 'sent_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('sent_at',)

@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session_id', 'user', 'user_message', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user_message', 'bot_response', 'session_id')
    readonly_fields = ('created_at',)

@admin.register(AIRecommendation)
class AIRecommendationAdmin(admin.ModelAdmin):
    list_display = ('symptoms', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('symptoms',)
    filter_horizontal = ('recommended_tests',)
    readonly_fields = ('created_at',)

# You might also want to register LabTestDetail if you want to manage it directly, but the inline handles most cases.
# admin.site.register(LabTestDetail)
