from django.shortcuts import render, redirect
from .models import Test, Lab, ContactMessage, ChatMessage, AIRecommendation
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import get_object_or_404
from .forms import LabUserRegistrationForm, TestForm, ContactForm, LabForm, ExcelUploadForm, AdminLabEditForm
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.views import LoginView
import openpyxl
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.forms import modelformset_factory # Import modelformset_factory
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import uuid
from .ai_service import AIChatbotService, AIRecommendationService

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# Create your views here.
def index(request):
    # Get popular tests - prioritize tests with prices, limit to 8 for better display
    popular_tests = Test.objects.filter(price__isnull=False).order_by('price')[:8]
    if popular_tests.count() < 4:
        # Fallback to any tests if not enough with prices
        popular_tests = Test.objects.all()[:8]
    return render(request, 'index.html', {'popular_tests': popular_tests})

def lab_login_view(request):
    """Custom login view for lab users"""
    if request.user.is_authenticated:
        # If user is already logged in, redirect based on user type
        if request.user.is_superuser:
            return redirect('admin_lab_list')
        elif hasattr(request.user, 'lab'):
            return redirect('manage_lab')
        else:
            return redirect('index')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                # Redirect based on user type
                if user.is_superuser:
                    return redirect('admin_lab_list')
                elif hasattr(user, 'lab'):
                    return redirect('manage_lab')
                else:
                    return redirect('index')
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'registration/login.html', {'form': form})

def admin_login_view(request):
    """Admin login view - only allows superuser access"""
    if request.user.is_authenticated and request.user.is_superuser:
        # If already logged in as superuser, redirect to admin panel
        return redirect('admin_lab_list')
    
    error_message = None
    
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        
        if not username or not password:
            error_message = 'Please enter both username and password.'
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                if user.is_superuser:
                    login(request, user)
                    messages.success(request, f'Welcome back, {user.username}!')
                    return redirect('admin_lab_list')
                else:
                    error_message = 'Access denied. This account does not have administrator privileges.'
            else:
                error_message = 'Invalid username or password. Please try again.'
    
    return render(request, 'adminlogin.html', {'error': error_message})


def about_page(request):
    return render(request, 'about.html')

def contact_page(request):
    # Check if this is a booking request
    is_booking = request.GET.get('booking') == 'true'
    test_name = request.GET.get('test_name', '')
    lab_name = request.GET.get('lab_name', '')
    
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            recipient_choice = form.cleaned_data['recipient_choice']
            contact_message = form.save(commit=False)
            if recipient_choice == 'admin':
                contact_message.recipient_admin = True
                contact_message.lab = None
            else:
                contact_message.recipient_admin = False
                contact_message.lab = Lab.objects.get(id=int(recipient_choice))
            contact_message.save()
            if is_booking:
                messages.success(request, f'Your booking request for {test_name} has been sent to {lab_name}. They will contact you shortly!')
            else:
                messages.success(request, 'Your message has been sent successfully!')
            return redirect('index')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill form if it's a booking request
        initial_data = {}
        if is_booking and test_name and lab_name:
            # Find the lab by name
            try:
                lab = Lab.objects.get(name=lab_name)
                # Set the recipient to the lab
                initial_data['recipient_choice'] = str(lab.id)
                # Don't pre-fill message - let user add their own notes
                initial_data['message'] = ''
            except Lab.DoesNotExist:
                pass
        
        form = ContactForm(initial=initial_data)
    
    return render(request, 'contact.html', {
        'form': form, 
        'is_booking': is_booking,
        'test_name': test_name,
        'lab_name': lab_name
    })

def search_labs(request):
    query = request.GET.get('query')
    print(f"Search query received: {query}")
    display_results = [] # This will store a list of dictionaries, each representing a test-lab pair

    if query:
        # Find tests that match the query (case-insensitive)
        matching_tests = Test.objects.filter(name__icontains=query)
        print(f"Matching tests found: {matching_tests}")

        for test in matching_tests:
            # For each test, find all labs that offer it
            labs_offering_test = test.lab_set.all()
            print(f"Labs offering test '{test.name}': {labs_offering_test}")

            for lab in labs_offering_test:
                display_results.append({
                    'test_name': test.name,
                    'test_description': test.description,
                    'test_price': test.price,
                    'lab_name': lab.name,
                    'lab_address': lab.address,
                    'lab_contact_email': lab.contact_email,
                    'lab_contact_phone': lab.contact_phone,
                })

    return render(request, 'labdetails.html', {'display_results': display_results, 'query': query})

def lab_registration(request):
    if request.method == 'POST':
        form = LabUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create lab with default values for required fields
            Lab.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                address=form.cleaned_data['address'],
                city='Kathmandu',  # Default city
                state='Bagmati',   # Default state
                zip_code='44600',  # Default zip code
                phone_number=form.cleaned_data['contact_phone'],
                contact_email=form.cleaned_data['contact_email'],
                contact_phone=form.cleaned_data['contact_phone']
            )
            messages.success(request, 'Registration successful! Please login to access your lab dashboard.')
            return redirect('login')  # Redirect to login page after successful registration
    else:
        form = LabUserRegistrationForm()
    return render(request, 'labregister.html', {'form': form})


@login_required
def manage_lab(request):
    try:
        # Get the lab associated with the logged-in user
        lab = request.user.lab
    except Lab.DoesNotExist:
        # If the user is a superuser without a lab, maybe show a different page or redirect
        if request.user.is_superuser:
            return redirect('admin_lab_list')
        # For regular users not associated with a lab, redirect to the landing page
        return redirect('index')

    if request.method == 'POST':
        form = TestForm(request.POST)
        if form.is_valid():
            # Create a new test and associate it with the current lab
            test = form.save()
            lab.tests.add(test)
            return redirect('manage_lab')
    else:
        form = TestForm()

    tests = lab.tests.all()
    # Fetch messages sent to this lab (recipient_admin is False)
    lab_messages = ContactMessage.objects.filter(lab=lab, recipient_admin=False).order_by('-sent_at')
    
    # Statistics for dashboard
    total_tests = tests.count()
    total_messages = lab_messages.count()
    recent_messages = lab_messages[:5]
    
    # Add ExcelUploadForm to context for lab-only upload interface
    excel_upload_form = ExcelUploadForm()
    
    context = {
        'lab': lab,
        'tests': tests,
        'form': form,
        'excel_upload_form': excel_upload_form,
        'lab_messages': lab_messages,
        'total_tests': total_tests,
        'total_messages': total_messages,
        'recent_messages': recent_messages,
    }
    return render(request, 'labmanage.html', context)


@login_required
def edit_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    # Check if the user is an admin or owns the lab that offers this test
    if not (request.user.is_superuser or (hasattr(request.user, 'lab') and test in request.user.lab.tests.all())):
        return redirect('manage_lab')

    if request.method == 'POST':
        form = TestForm(request.POST, instance=test)
        if form.is_valid():
            form.save()
            return redirect('manage_lab')
    else:
        form = TestForm(instance=test)

    return render(request, 'edit_test.html', {'form': form, 'test': test})


@login_required
def delete_test(request, test_id):
    test = get_object_or_404(Test, id=test_id)
    lab = request.user.lab
    # Check if the user is an admin or owns the lab that offers this test
    if not (request.user.is_superuser or (hasattr(request.user, 'lab') and test in lab.tests.all())):
        return redirect('manage_lab')

    if request.method == 'POST':
        # Remove the test from the lab. It doesn't delete the test itself
        # in case other labs offer it.
        lab.tests.remove(test)
        return redirect('manage_lab')

    return render(request, 'delete_test_confirm.html', {'test': test})


@user_passes_test(lambda u: u.is_superuser)
def admin_lab_list(request):
    labs = Lab.objects.all()
    
    # Statistics for dashboard
    total_labs = labs.count()
    total_tests = Test.objects.count()
    total_messages = ContactMessage.objects.count()
    recent_messages = ContactMessage.objects.order_by('-sent_at')[:5]
    total_users = User.objects.filter(is_superuser=False).count()
    
    # Recent labs (last 5 registered)
    recent_labs = labs.order_by('-id')[:5]
    
    context = {
        'labs': labs,
        'total_labs': total_labs,
        'total_tests': total_tests,
        'total_messages': total_messages,
        'total_users': total_users,
        'recent_messages': recent_messages,
        'recent_labs': recent_labs,
    }
    return render(request, 'admin_lab_manage.html', context)

@user_passes_test(lambda u: u.is_superuser)
def admin_edit_lab(request, lab_id):
    lab = get_object_or_404(Lab, pk=lab_id)
    user = lab.user
    
    # Removed 'popularity' from fields list in modelformset_factory
    TestFormSet = modelformset_factory(Test, fields=('name', 'description', 'price'), extra=0, can_delete=True)

    if request.method == 'POST':
        print("Raw POST data:", request.POST) # Add this line
        # Bind form to existing lab instance and pass initial data for user-related fields only
        form = AdminLabEditForm(request.POST, instance=lab, initial={
            'username': user.username,
            'email': user.email,
        })
        test_form = TestForm(request.POST, prefix='test') # Initialize with prefix in POST request
        formset = TestFormSet(request.POST, queryset=lab.tests.all(), prefix='tests')

        if form.is_valid() and formset.is_valid():
            # Update User model fields
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.save()
            
            # Update Lab model fields
            lab.name = form.cleaned_data['name']
            lab.address = form.cleaned_data['address']
            lab.contact_email = form.cleaned_data['contact_email']
            lab.contact_phone = form.cleaned_data['contact_phone']
            lab.save()

            # Save changes to existing tests and handle deletions
            formset.save()
            for test_instance in formset.deleted_objects:
                lab.tests.remove(test_instance) # Disassociate deleted tests from the lab

            # Handle adding a new test ONLY if the name field is provided
            if request.POST.get('test-name') and test_form.is_valid(): # Check for 'test-name' with the correct prefix
                new_test = test_form.save()
                lab.tests.add(new_test)
                messages.success(request, 'New test added and associated with the lab.')

            messages.success(request, 'Lab and associated tests updated successfully.')
            return redirect('admin_lab_list')
        else:
            print("Form errors:", form.errors) # Add this line to inspect form errors
            print("Test Form errors:", test_form.errors) # Add this line to inspect new test form errors
            print("Formset errors:", formset.errors) # Add this line to inspect formset errors
            messages.error(request, 'Please correct the errors below.')
    else:
        form = AdminLabEditForm(instance=lab, initial={
            'username': user.username,
            'email': user.email,
        })
        test_form = TestForm(prefix='test')  # Add prefix to avoid field name conflict
        formset = TestFormSet(queryset=lab.tests.all(), prefix='tests')

    # Get all available tests for selection (optional, depending on desired UI for adding existing tests)
    all_tests = Test.objects.all()

    return render(request, 'admin_edit_lab.html', {
        'form': form,
        'lab': lab,
        'test_form': test_form, # Form for adding new tests
        'formset': formset,     # Formset for managing existing tests
        'all_tests': all_tests  # All tests for potential selection
    })

@user_passes_test(lambda u: u.is_superuser)
def admin_delete_lab(request, lab_id):
    lab = Lab.objects.get(id=lab_id)
    lab.user.delete() # This will also delete the lab due to the CASCADE on the OneToOneField
    return redirect('admin_lab_list')

@user_passes_test(lambda u: u.is_superuser)
def view_contacts(request):
    messages = ContactMessage.objects.all().order_by('-sent_at')
    return render(request, 'view_contacts.html', {'messages': messages})


@user_passes_test(lambda u: u.is_superuser)
def upload_excel(request):
    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            try:
                workbook = openpyxl.load_workbook(excel_file)
                sheet = workbook.active

                # Assuming the first row is headers
                headers = [cell.value.lower() if cell.value else None for cell in sheet[1]]

                # Basic validation for required columns
                required_lab_cols = ['lab name', 'address', 'city', 'state', 'zip code', 'phone number', 'contact email', 'contact phone']
                required_test_cols = ['test name', 'test description', 'test price']

                if not all(col in headers for col in required_lab_cols + required_test_cols):
                    messages.error(request, "Missing one or more required columns in the Excel file (case-insensitive). Required: Lab Name, Address, City, State, Zip Code, Phone Number, Contact Email, Contact Phone, Test Name, Test Description, Test Price.")
                    return render(request, 'admin_upload_excel.html', {'form': form})

                for row_index in range(2, sheet.max_row + 1):
                    row_data = {headers[i]: cell.value for i, cell in enumerate(sheet[row_index])}

                    # Create or get Lab
                    lab_name = row_data.get('lab name')
                    if not lab_name:
                        messages.warning(request, f"Skipping row {row_index}: Lab Name is missing.")
                        continue

                    try:
                        lab = Lab.objects.get(name__iexact=lab_name) # Case-insensitive search for existing lab
                    except Lab.DoesNotExist:
                        user, created = User.objects.get_or_create(username=f"lab_{lab_name.replace(' ', '_').lower()}", defaults={'is_active': True})
                        if created:
                            user.set_password('defaultpassword') # IMPORTANT: Change this for production!
                            user.save()
                        lab = Lab.objects.create(
                            user=user,
                            name=lab_name,
                            address=row_data.get('address', ''),
                            city=row_data.get('city', ''),
                            state=row_data.get('state', ''),
                            zip_code=row_data.get('zip code', ''),
                            phone_number=row_data.get('phone number', ''),
                            contact_email=row_data.get('contact email', 'noreply@example.com'),
                            contact_phone=row_data.get('contact phone', '000-000-0000')
                        )
                        messages.info(request, f"Created new lab: {lab_name}")

                    # Create or get Test and associate with Lab
                    test_name = row_data.get('test name')
                    if test_name:
                        # Case-insensitive search for existing test
                        try:
                            test = Test.objects.get(name__iexact=test_name)
                            created = False
                        except Test.DoesNotExist:
                            test = Test.objects.create(
                                name=test_name,
                                description=row_data.get('test description', ''),
                                price=row_data.get('test price', 0.00)
                            )
                            created = True
                        
                        if created:
                            messages.info(request, f"Created new test: {test_name}")
                        lab.tests.add(test)
                        messages.info(request, f"Associated test '{test_name}' with lab '{lab_name}'")

                messages.success(request, "Excel file uploaded and processed successfully!")
                return redirect('admin_lab_list') # Redirect to admin lab list after successful upload

            except Exception as e:
                messages.error(request, f"Error processing Excel file: {e}")
    else:
        form = ExcelUploadForm()
    return render(request, 'admin_upload_excel.html', {'form': form})


@login_required
def lab_upload_tests_excel(request):
    if not hasattr(request.user, 'lab'):
        messages.error(request, "You must be a registered lab to upload tests.")
        return redirect('lab_registration')

    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            try:
                workbook = openpyxl.load_workbook(excel_file)
                sheet = workbook.active

                # Assuming the first row is headers
                headers = [cell.value.lower() if cell.value else None for cell in sheet[1]]
                expected_headers = ['name', 'description', 'price']

                # Fix 1: Map "test name" header to "name" if present
                if 'test name' in headers and 'name' not in headers:
                    headers[headers.index('test name')] = 'name'

                if not all(header in headers for header in expected_headers):
                    messages.error(request, "Missing required columns (case-insensitive). Accepts: Name/Test Name, Description, Price.")
                    return render(request, 'labmanage.html', {'form': form, 'lab': request.user.lab, 'tests': request.user.lab.tests.all()})

                for row_index in range(2, sheet.max_row + 1):
                    row_data = {headers[i]: cell.value for i, cell in enumerate(sheet[row_index])}

                    test_name = row_data.get('name')
                    test_description = row_data.get('description', '')
                    test_price = row_data.get('price', 0.00)

                    if not test_name:
                        messages.warning(request, f"Skipping row {row_index}: Test Name is missing.")
                        continue

                    test, created = Test.objects.get_or_create(
                        name__iexact=test_name, # Case-insensitive search
                        defaults={
                            'description': test_description,
                            'price': test_price
                        }
                    )
                    
                    # Explicitly update fields even if the test already existed
                    test.name = test_name # Ensure name is set/updated
                    test.description = test_description
                    test.price = test_price
                    test.save()

                    if created:
                        messages.info(request, f"Created new test: {test_name}")
                    else:
                        messages.info(request, f"Updated existing test: {test_name}")

                    request.user.lab.tests.add(test)
                    messages.info(request, f"Associated test '{test_name}' with your lab.")

                messages.success(request, "Excel file uploaded and processed successfully!")
                # Fix 2: Redirect to manage_lab to preserve original UI context
                return redirect('manage_lab')

            except Exception as e:
                messages.error(request, f"Error processing Excel file: {e}")
    else:
        form = ExcelUploadForm()
    return render(request, 'labmanage.html', {'form': form, 'lab': request.user.lab, 'tests': request.user.lab.tests.all(), 'excel_upload_form': form})


@login_required
def delete_message(request, message_id):
    message = get_object_or_404(ContactMessage, id=message_id)
    # Ensure only the recipient lab can delete the message
    if message.lab and message.lab.user == request.user:
        message.delete()
        messages.success(request, 'Message deleted successfully.')
    else:
        messages.error(request, 'You are not authorized to delete this message.')
    return redirect('manage_lab')

@login_required
@user_passes_test(lambda user: user.is_staff)
def admin_delete_message(request, message_id):
    message = get_object_or_404(ContactMessage, id=message_id)
    message.delete()
    messages.success(request, 'Message deleted successfully.')
    return redirect('view_contacts')
    # Ensure that only the lab to whom the message was sent can delete it
    if not (hasattr(request.user, 'lab') and message.lab == request.user.lab):
        messages.error(request, "You are not authorized to delete this message.")
        return redirect('manage_lab')

    if request.method == 'POST':
        message.delete()
        messages.success(request, "Message deleted successfully.")
        return redirect('manage_lab')
    
    # Optionally, you could render a confirmation page here
    return redirect('manage_lab') # For now, just redirect back to manage_lab


# AI Chatbot Views
# Note: Full-page chatbot removed - using floating widget only (more popular pattern)
# The floating widget is available on all pages via base.html

@csrf_exempt
@require_http_methods(["POST"])
def chatbot_api(request):
    """API endpoint for chatbot interactions"""
    try:
        data = json.loads(request.body)
        user_message = data.get('message', '').strip()
        session_id = data.get('session_id', str(uuid.uuid4()))
        
        if not user_message:
            return JsonResponse({'error': 'Message is required'}, status=400)
        
        # Initialize chatbot service
        chatbot = AIChatbotService()
        
        # Generate response and suggestions
        bot_response, suggestions = chatbot.generate_response(user_message, session_id)
        
        # Save to database
        chat_message = ChatMessage.objects.create(
            session_id=session_id,
            user_message=user_message,
            bot_response=bot_response,
            user=request.user if request.user.is_authenticated else None
        )
        
        return JsonResponse({
            'response': bot_response,
            'suggestions': suggestions,
            'session_id': session_id,
            'timestamp': chat_message.created_at.isoformat()
        })
    
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def ai_recommendations_view(request):
    """View for AI-powered test recommendations based on symptoms"""
    recommended_tests = None
    symptoms = ''
    recommendation = None
    
    if request.method == 'POST':
        symptoms = request.POST.get('symptoms', '').strip()
        
        if symptoms:
            recommendation_service = AIRecommendationService()
            recommendation = recommendation_service.recommend_tests(
                symptoms,
                user=request.user if request.user.is_authenticated else None
            )
            
            if recommendation:
                recommended_tests = recommendation.recommended_tests.all()
                if not recommended_tests.exists():
                    messages.warning(request, 'Recommendations were created but no tests were found. Please ensure sample data is loaded.')
            else:
                messages.info(request, 'No specific recommendations found. Please try describing your symptoms in more detail.')
        else:
            messages.error(request, 'Please enter your symptoms.')
    
    return render(request, 'ai_recommendations.html', {
        'recommendation': recommendation,
        'recommended_tests': recommended_tests,
        'symptoms': symptoms
    })


def chatbot_history(request):
    """View chat history for authenticated users"""
    if not request.user.is_authenticated:
        messages.info(request, 'Please login to view your chat history.')
        return redirect('login')
    
    chat_history = ChatMessage.objects.filter(user=request.user).order_by('-created_at')[:50]
    return render(request, 'chatbot_history.html', {'chat_history': chat_history})
