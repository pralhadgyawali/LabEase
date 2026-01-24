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
            form.save()
            return redirect('index')  # Or a 'thank you' page
    else:
        form = ContactForm()
    return render(request, 'contact.html', {'form': form})

def search_labs(request):
    query = request.GET.get('query')
    print(f"Search query received: {query}")
    display_results = [] # This will store a list of dictionaries, each representing a test-lab pair

    if query:
        # Find tests that match the query
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
    print(f"Debug: Tests retrieved for lab {lab.name} in manage_lab view: {tests.count()} tests")
    for test in tests:
        print(f"Debug: Test in manage_lab: {test.name}")
    # Add ExcelUploadForm to context for lab-only upload interface
    excel_upload_form = ExcelUploadForm()
    return render(request, 'labmanage.html', {'lab': lab, 'tests': tests, 'form': form, 'excel_upload_form': excel_upload_form})


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
    
    # Create a formset for managing existing tests associated with the lab
    TestFormSet = modelformset_factory(Test, fields=('name', 'description', 'price', 'popularity'), extra=0, can_delete=True)

    if request.method == 'POST':
        print("Raw POST data:", request.POST) # Add this line
        # Bind form to existing lab instance and pass initial data for user-related fields only
        form = AdminLabEditForm(request.POST, instance=lab, initial={
            'username': user.username,
            'email': user.email,
        })
        test_form = TestForm(request.POST)
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
            if request.POST.get('tests-0-name') and test_form.is_valid(): # Check if 'name' for new test is present
                new_test = test_form.save()
                lab.tests.add(new_test)
                messages.success(request, 'New test added and associated with the lab.')

            messages.success(request, 'Lab and associated tests updated successfully.')
            return redirect('admin_lab_list')
        else:
            print("Form errors:", form.errors) # Add this line to inspect form errors
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
                headers = [cell.value for cell in sheet[1]]

                # Basic validation for required columns
                required_lab_cols = ['Lab Name', 'Address', 'City', 'State', 'Zip Code', 'Phone Number', 'Contact Email', 'Contact Phone']
                required_test_cols = ['Test Name', 'Test Description', 'Test Price']

                if not all(col in headers for col in required_lab_cols + required_test_cols):
                    messages.error(request, "Missing one or more required columns in the Excel file. Required: Lab Name, Address, City, State, Zip Code, Phone Number, Contact Email, Contact Phone, Test Name, Test Description, Test Price.")
                    return render(request, 'admin_upload_excel.html', {'form': form})

                for row_index in range(2, sheet.max_row + 1):
                    row_data = {headers[i]: cell.value for i, cell in enumerate(sheet[row_index])}

                    # Create or get Lab
                    lab_name = row_data.get('Lab Name')
                    if not lab_name:
                        messages.warning(request, f"Skipping row {row_index}: Lab Name is missing.")
                        continue

                    # For simplicity, let's assume a user for the lab already exists or we create a dummy one.
                    # In a real application, you'd link to an existing user or create a new one with a proper username/password.
                    # For now, we'll try to find an existing lab by name.
                    try:
                        lab = Lab.objects.get(name=lab_name)
                    except Lab.DoesNotExist:
                        # If lab doesn't exist, create a dummy user and then the lab
                        # This part needs careful consideration for production. For now, a simple approach.
                        user, created = User.objects.get_or_create(username=f"lab_{lab_name.replace(' ', '_').lower()}", defaults={'is_active': True})
                        if created:
                            user.set_password('defaultpassword') # IMPORTANT: Change this for production!
                            user.save()
                        lab = Lab.objects.create(
                            user=user,
                            name=lab_name,
                            address=row_data.get('Address', ''),
                            city=row_data.get('City', ''),
                            state=row_data.get('State', ''),
                            zip_code=row_data.get('Zip Code', ''),
                            phone_number=row_data.get('Phone Number', ''),
                            contact_email=row_data.get('Contact Email', 'noreply@example.com'),
                            contact_phone=row_data.get('Contact Phone', '000-000-0000')
                        )
                        messages.info(request, f"Created new lab: {lab_name}")

                    # Create or get Test and associate with Lab
                    test_name = row_data.get('Test Name')
                    if test_name:
                        test, created = Test.objects.get_or_create(
                            name=test_name,
                            defaults={
                                'description': row_data.get('Test Description', ''),
                                'price': row_data.get('Test Price', 0.00)
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
        return redirect('lab_registration') # Or an appropriate redirect

    if request.method == 'POST':
        form = ExcelUploadForm(request.POST, request.FILES)
        if form.is_valid():
            excel_file = request.FILES['excel_file']
            try:
                workbook = openpyxl.load_workbook(excel_file)
                sheet = workbook.active

                # Assuming the first row is headers
                headers = [cell.value.lower() if cell.value else None for cell in sheet[1]]
                expected_headers = ['name', 'description', 'price', 'popularity']

                if not all(header in headers for header in expected_headers):
                    # Update error message to clarify case insensitivity
                    messages.error(request, "Missing required columns in Excel file (case-insensitive). Expected: Name, Description, Price, Popularity.")
                    return redirect('manage_lab')

                for row_index in range(2, sheet.max_row + 1):
                    row_data = {headers[i]: sheet.cell(row=row_index, column=i+1).value for i in range(len(headers))}

                    test_name = row_data.get('name')
                    test_description = row_data.get('description')
                    test_price = row_data.get('price')
                    test_popularity = row_data.get('popularity', 0)

                    if not test_name or test_price is None:
                        messages.warning(request, f"Skipping row {row_index}: Test name and price are required.")
                        continue

                    # Create or update the test
                    # The following lines are incorrect and should be removed or commented out:
                    # test_name = row_data['test_name'] 
                    # test_price = row_data['test_price']
                    # test_description = row_data['test_description']

                    print(f"Debug: Processing test from Excel - Name: {test_name}, Price: {test_price}, Description: {test_description}")

                    test, created = Test.objects.update_or_create(
                        name=test_name,
                        defaults={'price': test_price, 'description': test_description}
                    )
                    if created:
                        print(f"Debug: Created new test: {test.name}")
                    else:
                        print(f"Debug: Updated existing test: {test.name}")

                    request.user.lab.tests.add(test)
                    print(f"Debug: Added test {test.name} to lab {request.user.lab.name}")

                messages.success(request, "Tests uploaded and associated with your lab successfully!")
                return redirect('manage_lab') # Redirect to the lab management page

            except Exception as e:
                messages.error(request, f"Error processing Excel file: {e}")
        else:
            messages.error(request, "Invalid form submission.")
    else:
        form = ExcelUploadForm()
    
    # This view is primarily for POST requests, but if accessed via GET, it should redirect or show a form.
    # For now, redirect to manage_lab if it's a GET request without a valid form submission.
    return redirect('manage_lab')
