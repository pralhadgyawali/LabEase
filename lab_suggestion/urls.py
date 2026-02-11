from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about_page, name='about_page'),
    path('contact/', views.contact_page, name='contact_page'),
    path('search/', views.search_labs, name='search_labs'),
    path('api/search-tests/', views.search_tests_autocomplete, name='search_tests_autocomplete'),
    path('register/', views.register, name='register'),
    path('register-lab/', views.lab_registration, name='lab_registration'),
    path('login/', views.lab_login_view, name='login'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('lab-admin/labs/', views.admin_lab_list, name='admin_lab_list'),
    path('lab-admin/labs/<int:lab_id>/edit/', views.admin_edit_lab, name='admin_edit_lab'),
    path('lab-admin/labs/<int:lab_id>/delete/', views.admin_delete_lab, name='admin_delete_lab'),
    path('lab-admin/contacts/', views.view_contacts, name='view_contacts'),
    path('lab/dashboard/', views.manage_lab, name='manage_lab'),
    path('lab/edit_test/<int:test_id>/', views.edit_test, name='edit_test'),
    path('lab/delete_test/<int:test_id>/', views.delete_test, name='delete_test'),
    path('lab/delete_message/<int:message_id>/', views.delete_message, name='delete_message'), # New URL pattern
    path('lab/view-bookings/', views.view_lab_bookings, name='view_lab_bookings'),
    path('admin/delete_message/<int:message_id>/', views.admin_delete_message, name='admin_delete_message'),
    path('admin/upload_excel/', views.upload_excel, name='admin_upload_excel'), # Renamed for clarity
    path('lab/upload_tests_excel/', views.lab_upload_tests_excel, name='lab_upload_tests_excel'), # New URL for lab users
    # AI Features
    path('api/chatbot/', views.chatbot_api, name='chatbot_api'),
    path('ai/recommendations/', views.ai_recommendations_view, name='ai_recommendations'),
    path('chatbot/history/', views.chatbot_history, name='chatbot_history'),
    # Test Booking Features
    path('book-test/<int:test_id>/<int:lab_id>/', views.book_test, name='book_test'),
    path('check-booking-status/', views.check_booking_status, name='check_booking_status'),
    path('update-booking/<str:booking_id>/', views.update_booking, name='update_booking'),
    path('cancel-booking/<str:booking_id>/', views.cancel_booking, name='cancel_booking'),
]