# Student Election System

A comprehensive web-based student election management system built with Django, designed to handle secure and efficient student government elections.

## Technologies Used

### Backend Framework
- **Django 4.x**: Main web framework
  - URL routing
  - Model-View-Template (MVT) architecture
  - Authentication and authorization
  - Form handling and validation
  - Database ORM
  - Admin interface

### Database
- **SQLite3**: Built-in database
  - Student registry storage
  - Vote records
  - Candidate information
  - Election settings
  - Audit logs

### Frontend Technologies
- **Bootstrap 5**: Frontend framework
  - Responsive layout
  - UI components
  - Grid system
  - Forms styling
  - Cards and tables
- **Font Awesome**: Icon library
  - UI icons
  - Navigation icons
  - Action buttons

### Security
- **Django's Built-in Security**:
  - CSRF protection
  - XSS prevention
  - SQL injection prevention
  - Password hashing
- **Cryptography**: For vote encryption
  - Secure vote storage
  - Data privacy

### Additional Libraries
- **WeasyPrint**: PDF generation
  - Election results export
  - Reports generation
- **Pillow**: Image handling
  - Candidate photo upload
  - Image resizing and optimization

## Features

1. **User Management**
   - Admin registration and authentication
   - Student voter registration
   - Role-based access control

2. **Student Registry**
   - Student information management
   - Registration number validation
   - Department and year tracking

3. **Election Management**
   - Position creation and management
   - Candidate registration
   - Election scheduling
   - Results tabulation and publishing

4. **Voting System**
   - Secure vote casting
   - Vote encryption
   - Prevention of double voting
   - Real-time vote counting

5. **Audit System**
   - Activity logging
   - Election monitoring
   - Security tracking

## Project Structure

```
StudentsElection/
├── Admin/                 # Admin management app
├── Voters/               # Voter management app
├── static/               # Static files (CSS, JS)
├── templates/            # HTML templates
├── candidates/           # Candidate photos
├── docs/                 # Documentation
└── StudentsElection/     # Project settings
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Run migrations:
   ```bash
   python manage.py migrate
   ```
5. Create a superuser:
   ```bash
   python manage.py createsuperuser
   ```
6. Run the development server:
   ```bash
   python manage.py runserver #For Linux
   py manage.py runserver #For Windows
   ```

## Security Considerations

- All passwords are hashed using Django's password hashers
- Votes are encrypted before storage
- CSRF protection is enabled
- Session security is enforced
- SQL injection protection is in place
- XSS prevention is implemented

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
  - Administrators
- **Registration Format**: 
  - Pattern: `SPUxxxxx/yy` (e.g., SPU02236/25)
  - Must be pre-registered in StudentRegistry

### 2. Core Modules

#### Admin Module (`Admin/`)
- Election management
- Candidate registration
- Position creation
- Results monitoring
- Audit logging

#### Voters Module (`Voters/`)
- Student registration
- Voting interface
- Vote verification
- Election status checking

### 3. Database Models

#### StudentRegistry
- Stores pre-verified student records
- Fields:
  - reg_number (unique)
  - full_name
  - email
  - department
  - is_active
  - is_admin

#### VoterProfile
- Extended user information
- Links to Django User model
- Stores voting status

#### Position & Candidate
- Election structure
- Candidate information
- Vote tracking

### 4. Templates Structure
```
templates/
├── base.html                  # Base template
├── 404.html                   # Error page
├── home.html                  # Landing page
├── Admin/
│   ├── admin_dashboard.html   # Admin control panel
│   ├── audit_logs.html       # System logs
│   ├── candidate_form.html   # Candidate management
│   ├── position_form.html    # Position management
│   └── results.html          # Election results
├── registration/
│   ├── admin_register.html   # Admin registration
│   ├── login.html           # User login
│   └── register.html        # Student registration
└── voters/
    ├── home.html            # Voter homepage
    ├── vote_confirmation.html
    ├── vote_success.html
    └── voter_dashboard.html
```

## Setup Instructions

### 1. Environment Setup
```bash
# Clone repository
git clone [repository-url]

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Setup database
python manage.py migrate
```
All Done
### 2. Initial Data Setup
```python
# Using Django shell
python manage.py shell

from Voters.models import StudentRegistry

# Add student record
StudentRegistry.objects.create(
    reg_number="SPU02236/25",
    full_name="Student Name",
    email="student@example.com",
    department="Computer Science",
    is_active=True
)

# Add admin record
StudentRegistry.objects.create(
    reg_number="SPU00001/25",
    full_name="Admin Name",
    email="admin@example.com",
    department="Administration",
    is_active=True,
)
```

## User Guides

### Administrator Guide

1. **Registration**
   - Use admin registration number (SPUxxxxx/25)
   - Provide admin secret code
   - Complete profile information

2. **Election Management**
   - Create/modify positions
   - Add/edit candidates
   - Set election timing
   - Monitor voting progress
   - View and export results

3. **System Management**
   - View audit logs
   - Manage student records
   - Handle election settings

### Student Voter Guide

1. **Registration**
   - Use student registration number (SPUxxxxx/25)
   - Complete profile setup
   - Verify email (if required)

2. **Voting Process**
   - Login during active election
   - View candidate information
   - Cast votes for positions
   - Receive confirmation

## Security Features

1. **Authentication**
   - Pre-verified registration numbers
   - Secure password handling
   - Session management

2. **Vote Security**
   - One vote per position
   - Vote confirmation
   - Audit logging
   - Prevention of double voting

3. **Admin Security**
   - Two-factor verification
   - Activity logging
   - Role-based access control

## Troubleshooting

### Common Issues

1. **Registration Issues**
   - Verify registration number format
   - Check StudentRegistry for pre-registration
   - Confirm email format

2. **Login Problems**
   - Verify user category selection
   - Check registration number format
   - Ensure account is active

3. **Voting Issues**
   - Confirm election is active
   - Check for previous votes
   - Verify position availability

## Development Guidelines

### Code Style
- Follow PEP 8 for Python code
- Use Django's coding style
- Implement proper documentation

### Testing
- Write unit tests for models
- Include integration tests
- Test security measures

### Version Control
- Use meaningful commit messages
- Branch for features
- Review before merge

## Maintenance

### Regular Tasks
1. Database backup
2. Log rotation
3. Security updates
4. User data cleanup

### System Updates
1. Backup data
2. Update dependencies
3. Test in staging
4. Deploy carefully
