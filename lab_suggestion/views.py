from django.shortcuts import render, redirect
from .models import Test, Lab, ContactMessage
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import get_object_or_404
from .forms import LabUserRegistrationForm, TestForm, ContactForm, LabForm, ExcelUploadForm, AdminLabEditForm
from django.contrib import messages
import openpyxl
from django.contrib.auth import authenticate, login
from django.forms import modelformset_factory # Import modelformset_factory

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
    popular_tests = Test.objects.order_by('-name')[:5]  # Order by name for now
    return render(request, 'index.html', {'popular_tests': popular_tests})

def admin_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to the new admin lab list URL
            return redirect('admin_lab_list')
        else:
            # Return an 'invalid login' error message.
            return render(request, 'adminlogin.html', {'error': 'Invalid credentials'})
    return render(request, 'adminlogin.html')


def about_page(request):
    return render(request, 'about.html')

def contact_page(request):
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
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('index')  # Or a 'thank you' page
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

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
            Lab.objects.create(
                user=user,
                name=form.cleaned_data['name'],
                address=form.cleaned_data['address'],
                contact_email=form.cleaned_data['contact_email'],
                contact_phone=form.cleaned_data['contact_phone']
            )
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
    # New: Fetch messages sent to this lab (recipient_admin is False)
    lab_messages = ContactMessage.objects.filter(lab=lab, recipient_admin=False)
    print(f"Debug: Messages retrieved for lab {lab.name}: {lab_messages.count()} messages")
    for msg in lab_messages:
        print(f"Debug: Message: {msg.message}") # Changed from msg.subject to msg.message
    # Add ExcelUploadForm to context for lab-only upload interface
    excel_upload_form = ExcelUploadForm()
    # New: Pass lab_messages to the template
    return render(request, 'labmanage.html', {'lab': lab, 'tests': tests, 'form': form, 'excel_upload_form': excel_upload_form, 'lab_messages': lab_messages})


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
    return render(request, 'admin_lab_manage.html', {'labs': labs})

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


def admin_lab_list(request):
    labs = Lab.objects.all()
    return render(request, 'admin_lab_manage.html', {'labs': labs})

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
                        test, created = Test.objects.get_or_create(
                            name__iexact=test_name, # Case-insensitive search for existing test
                            defaults={
                                'description': row_data.get('test description', ''),
                                'price': row_data.get('test price', 0.00)
                            }
                        )
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
