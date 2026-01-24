from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about_page, name='about_page'),
    path('contact/', views.contact_page, name='contact_page'),
    path('search/', views.search_labs, name='search_labs'),
    path('register/', views.register, name='register'),
    path('register-lab/', views.lab_registration, name='lab_registration'),
    path('admin-login/', views.admin_login_view, name='admin_login'),
    path('lab-admin/labs/', views.admin_lab_list, name='admin_lab_list'),
    path('lab-admin/labs/<int:lab_id>/edit/', views.admin_edit_lab, name='admin_edit_lab'),
    path('lab-admin/labs/<int:lab_id>/delete/', views.admin_delete_lab, name='admin_delete_lab'),
    path('lab-admin/contacts/', views.view_contacts, name='view_contacts'),
    path('lab/dashboard/', views.manage_lab, name='manage_lab'),
    path('lab/test/<int:test_id>/edit/', views.edit_test, name='edit_test'),
    path('lab/test/<int:test_id>/delete/', views.delete_test, name='delete_test'),
    path('admin/upload_excel/', views.upload_excel, name='admin_upload_excel'), # Renamed for clarity
    path('lab/upload_tests_excel/', views.lab_upload_tests_excel, name='lab_upload_tests_excel'), # New URL for lab users
]