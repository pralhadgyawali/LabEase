# LabEase - AI-Powered Lab Management System

LabEase is a comprehensive Django-based web application for managing medical laboratories, tests, and providing AI-powered assistance to users. The system includes an intelligent chatbot, AI-driven test recommendations, and a complete lab management interface.

## Features

### Core Features
- **Lab Management**: Register and manage laboratories with detailed information
- **Test Management**: Add, edit, and manage medical tests
- **Search Functionality**: Search for labs and tests easily
- **Contact System**: Send messages to labs or administrators
- **Excel Import**: Bulk import labs and tests via Excel files
- **User Authentication**: Secure login system for labs and administrators

### AI Features
- **AI Chatbot**: Interactive chatbot that helps users find labs, search for tests, get price information, and receive recommendations
- **AI Test Recommendations**: Get personalized test recommendations based on symptoms
- **Chat History**: View your conversation history with the AI assistant (for authenticated users)

## Technology Stack

- **Backend**: Django 5.2.8
- **Database**: SQLite (default, can be configured for PostgreSQL/MySQL)
- **Frontend**: HTML, CSS (Tailwind CSS via CDN), JavaScript
- **AI**: Custom AI service with intelligent pattern matching and recommendation engine
- **File Processing**: openpyxl for Excel file handling

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Virtual environment (recommended)

## Installation

### Option 1: Using setup.sh (Recommended)

```bash
chmod +x setup.sh
./setup.sh
```

### Option 2: Manual Installation

1. **Clone or download the project**
   ```bash
   cd LabEase-master
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Load sample data (recommended)**
   ```bash
   python manage.py load_sample_data
   ```
   This will create sample tests, labs, and associations so the chatbot and AI features work properly.

7. **Start the development server**
   ```bash
   python manage.py runserver
   ```

The application will be available at `http://localhost:8000`

## Quick Start

### Using start.sh

```bash
chmod +x start.sh
./start.sh
```

This script will:
- Activate the virtual environment
- Run migrations (if needed)
- Start the Django development server

## Docker Deployment

### Build and Run with Docker

```bash
# Build the Docker image
docker build -t labease .

# Run the container
docker run -d -p 8000:8000 --name labease-app labease
```

The application will be available at `http://localhost:8000`

### Docker Compose (Alternative)

```bash
docker-compose up -d
```

## Project Structure

```
LabEase-master/
├── labease_django/          # Main Django project settings
│   ├── settings.py          # Django settings
│   ├── urls.py              # Main URL configuration
│   └── wsgi.py              # WSGI configuration
├── lab_suggestion/          # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View functions
│   ├── urls.py             # App URL patterns
│   ├── forms.py            # Django forms
│   ├── ai_service.py       # AI chatbot and recommendation service
│   ├── templates/          # HTML templates
│   └── migrations/         # Database migrations
├── templates/              # Base templates
├── manage.py               # Django management script
├── requirements.txt        # Python dependencies
├── setup.sh                # Setup script
├── start.sh                # Start script
├── Dockerfile              # Docker configuration
└── README.md              # This file
```

## Database

The application uses SQLite by default. The database file (`db.sqlite3`) is created automatically when you run migrations.

### Database Models

- **User**: Django's built-in user model
- **Lab**: Laboratory information
- **Test**: Medical test information
- **LabTestDetail**: Relationship between labs and tests
- **ContactMessage**: Messages sent to labs or admins
- **ChatMessage**: AI chatbot conversation history
- **AIRecommendation**: AI-generated test recommendations

## Usage Guide

### For End Users

1. **Search for Tests**: Use the search bar on the homepage to find tests
2. **AI Chatbot**: Click on "AI Chatbot" in the navigation to interact with the AI assistant
3. **Get Recommendations**: Visit "AI Recommendations" to get test suggestions based on symptoms
4. **Contact Labs**: Use the contact page to send messages to labs

### For Lab Owners

1. **Register**: Click "Register Lab" to create an account
2. **Login**: Use your credentials to log in
3. **Manage Tests**: Add, edit, or delete tests from your dashboard
4. **Upload Excel**: Bulk import tests using Excel files
5. **View Messages**: Check messages sent to your lab

### For Administrators

1. **Admin Login**: Use the "Admin Login" link
2. **Manage Labs**: View, edit, or delete labs
3. **View Contacts**: See all contact messages
4. **Bulk Upload**: Import multiple labs and tests via Excel

## AI Features Details

### Chatbot Capabilities

The AI chatbot can help with:
- Finding specific tests
- Locating labs by location
- Getting price information
- Symptom-based test recommendations
- General questions about the platform

### Test Recommendations

The AI recommendation system analyzes symptoms and suggests relevant tests. It uses pattern matching to identify:
- Diabetes-related symptoms
- Heart and cardiac issues
- Thyroid problems
- Liver conditions
- Kidney issues
- Cholesterol concerns
- Blood count issues
- And more...

## API Endpoints

- `GET /` - Homepage
- `GET /search/` - Search for labs and tests
- `GET /chatbot/` - AI Chatbot interface
- `POST /api/chatbot/` - Chatbot API endpoint
- `GET /ai/recommendations/` - AI recommendations page
- `POST /ai/recommendations/` - Submit symptoms for recommendations
- `GET /chatbot/history/` - View chat history (requires authentication)

## Configuration

### Settings

Key settings in `labease_django/settings.py`:
- `DEBUG`: Set to `False` in production
- `ALLOWED_HOSTS`: Add your domain in production
- `DATABASES`: Configure your database (SQLite by default)
- `SECRET_KEY`: Change this in production!

### Environment Variables (Optional)

You can use environment variables for sensitive settings:
```bash
export DJANGO_SECRET_KEY='your-secret-key'
export DJANGO_DEBUG=False
```

## Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Database errors**: Run migrations
   ```bash
   python manage.py migrate
   ```

3. **Port already in use**: Change the port
   ```bash
   python manage.py runserver 8001
   ```

4. **Permission denied on scripts**: Make scripts executable
   ```bash
   chmod +x setup.sh start.sh
   ```

## Development

### Loading Sample Data

To populate the database with sample tests and labs:

```bash
python manage.py load_sample_data
```

This creates:
- 20 different medical tests (CBC, glucose, thyroid, etc.)
- 5 sample labs in different cities
- Test-lab associations

**Note**: Sample lab passwords are set to `sample123` for testing purposes.

### Running Tests

```bash
python manage.py test
```

### Creating Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### Accessing Django Admin

1. Create a superuser: `python manage.py createsuperuser`
2. Visit: `http://localhost:8000/admin/`
3. Login with your superuser credentials

## Production Deployment

### Important Security Notes

1. **Change SECRET_KEY**: Generate a new secret key for production
2. **Set DEBUG=False**: Disable debug mode
3. **Configure ALLOWED_HOSTS**: Add your domain
4. **Use a production database**: Consider PostgreSQL or MySQL
5. **Set up HTTPS**: Use SSL/TLS certificates
6. **Configure static files**: Use a proper static file server

### Recommended Production Setup

- Use PostgreSQL or MySQL instead of SQLite
- Set up a reverse proxy (Nginx)
- Use Gunicorn or uWSGI as WSGI server
- Configure proper logging
- Set up monitoring and backups

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available for use.

## Login Credentials

For testing purposes, sample lab accounts are available. See **[LOGIN_CREDENTIALS.md](LOGIN_CREDENTIALS.md)** for all login information.

**Quick Access:**
- Admin: Create with `python manage.py createsuperuser`

## Support

For issues, questions, or contributions, please contact the development team or open an issue in the repository.

## Changelog

### Version 1.0.0
- Initial release
- Lab and test management
- AI chatbot integration
- AI-powered test recommendations
- Excel import functionality
- User authentication system
- Contact messaging system

---

**Note**: This application is for demonstration and educational purposes. For production use, ensure proper security measures, database backups, and compliance with healthcare regulations (HIPAA, etc.) if handling real medical data.
