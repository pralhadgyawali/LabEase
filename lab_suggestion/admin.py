from django.contrib import admin
from .models import Test, Lab, LabTestDetail

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
    list_display = ('name', 'price', 'popularity')
    search_fields = ('name', 'description')
    list_filter = ('popularity',)

# You might also want to register LabTestDetail if you want to manage it directly, but the inline handles most cases.
# admin.site.register(LabTestDetail)
