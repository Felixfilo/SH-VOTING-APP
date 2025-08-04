# README.md

# Authors
#Bobitlmr188021
#Bobitlmr

## Project Overview

The Student Election System is a Django-based web application that manages student government elections. The system handles user authentication, student registration, candidate management, secure voting, and result tabulation.

## Technology Stack

### Core Technologies

1. **Django 4.x**
   - Primary web framework
   - Handles routing, views, models, and templates
   - Built-in admin interface
   - Form processing and validation
   - Security features (CSRF, XSS protection)

2. **SQLite3 Database**
   - Used for data persistence
   - Handles relations between models
   - Stores encrypted vote data
   - Maintains audit logs

3. **Bootstrap 5**
   - Frontend styling and layout
   - Responsive design components
   - Grid system
   - Form styling

### Key Libraries and Dependencies

1. **Cryptography**
   ```python
   from cryptography.fernet import Fernet
   ```
   - Used for vote encryption
   - Ensures vote privacy and security

2. **Pillow**
   ```python
   from PIL import Image
   ```
   - Handles image processing
   - Used for candidate photos

3. **WeasyPrint**
   ```python
   from weasyprint import HTML
   ```
   - Generates PDF reports
   - Used for election results export

## File Structure Conventions

1. **Models**
   - Located in `app_name/models.py`
   - Follow Django's model naming conventions
   - Include proper field types and relationships
   ```python
   class ModelName(models.Model):
       field_name = models.FieldType()
   ```

2. **Views**
   - Located in `app_name/views.py`
   - Use function-based views with decorators
   - Include proper authentication checks
   ```python
   @login_required
   @user_passes_test(is_admin)
   def view_name(request):
       # View logic
   ```

3. **Forms**
   - Located in `app_name/forms.py`
   - Extend Django form classes
   - Include proper widgets and validation
   ```python
   class FormName(forms.ModelForm):
       class Meta:
           model = ModelName
           fields = ['field1', 'field2']
   ```

4. **Templates**
   - Located in `templates/app_name/`
   - Extend base template
   - Use Bootstrap classes
   ```html
   {% extends 'base.html' %}
   {% block content %}
   <!-- Template content -->
   {% endblock %}
   ```

## Coding Standards

1. **Python Style**
   - Follow PEP 8
   - Use meaningful variable names
   - Include docstrings for complex functions
   - Add comments for non-obvious logic

2. **Django Best Practices**
   - Use class-based views when appropriate
   - Implement proper form validation
   - Handle exceptions gracefully
   - Use Django's built-in security features

3. **Template Guidelines**
   - Use template inheritance
   - Keep logic in views, not templates
   - Use proper indentation
   - Include proper CSRF tokens in forms

## Security Considerations

1. **Authentication**
   - Always use `@login_required` decorator
   - Check user roles with `@user_passes_test`
   - Validate user permissions

2. **Data Protection**
   - Encrypt sensitive data
   - Use Django's form validation
   - Implement proper access controls
   - Log security-related events

3. **Vote Security**
   - Encrypt votes before storage
   - Prevent double voting
   - Maintain vote anonymity
   - Log voting activities

## Common Tasks

1. **Adding New Features**
   - Create/update models
   - Add corresponding forms
   - Implement views
   - Create templates
   - Update URLs
   - Add to admin interface if needed

2. **Handling Forms**
   ```python
   if request.method == 'POST':
       form = FormName(request.POST)
       if form.is_valid():
           form.save()
   ```

3. **Adding Audit Logs**
   ```python
   AuditLog.log_action(
       user=request.user,
       action='ACTION_TYPE',
       description='Action description'
   )
   ```

## Testing Guidelines

1. **Unit Tests**
   - Test models
   - Test forms
   - Test views
   - Test authentication
   - Test permissions

2. **Integration Tests**
   - Test complete workflows
   - Test form submissions
   - Test vote processing
   - Test result calculation

## Maintenance Tasks

1. **Database Migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

2. **Static Files**
   ```bash
   python manage.py collectstatic
   ```

3. **Dependency Updates**
   - Regular requirements.txt updates
   - Security patch applications
   - Compatibility testing

### Registration System
- Uses custom registration numbers in format `SPUxxxxx/yy` (e.g. SPU02236/25)
- Student/Admin records must exist in `StudentRegistry` before registration
- Two-step verification: registration number + admin secret code for admins

### Database Models
- `StudentRegistry` - Pre-verified student/admin records
- `VoterProfile` - Extended user profile for voters
- `Position` & `Candidate` - Election configuration
- `ElectionSettings` - Controls election status/timing

### Template Structure
- Base template: `templates/base.html` 
- Admin views: `templates/Admin/`
- Voter views: `templates/voters/`
- Registration: `templates/registration/`

## Development Workflow

### Environment Setup
1. Install requirements: `pip install -r requirements.txt`
2. Configure database: `python manage.py migrate`
3. Load initial data:
```python
from Voters.models import StudentRegistry
StudentRegistry.objects.create(
    reg_number="SPU02236/25",
    full_name="Student Name", 
    email="student@example.com",
    department="Computer Science",
    is_active=True
)
```

### Authentication Flow
1. User selects category (Student/Admin) on login
2. Validates registration number exists in `StudentRegistry`
3. For admin access, requires additional secret code verification

### Key Files
- `Admin/views.py` - Core election management logic
- `Voters/models.py` - Data models and validation
- `templates/base.html` - Common layout and styling
- `static/css/style.css` - Custom styling using CSS variables

## Project Conventions

### Forms
- All forms extend Django's built-in form classes
- Use Bootstrap classes for styling (`form-control`, etc)
- Include placeholders showing expected formats

### Templates
- Extend `base.html` for consistent layout
- Use Font Awesome icons for visual elements
- Follow BEM-style CSS class naming

### Security
- Registration numbers must be pre-verified
- Admin actions require additional verification
- Session management for active elections

## Common Tasks

### Adding New Student Records
```python
python manage.py shell
from Voters.models import StudentRegistry
StudentRegistry.objects.create(
    reg_number="SPUxxxxx/yy",
    full_name="Name",
    email="email",
    department="Dept",
    is_active=True
)
```

### Managing Elections
1. Create positions through admin interface
2. Add candidates for each position
3. Configure election settings (timing, status)
4. Monitor results through admin dashboard
