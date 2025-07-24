from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import VoterProfile, StudentRegistry

class CustomLoginForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Username or Registration Number'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Password'
        })
    )
    category = forms.ChoiceField(
        choices=[('Voter', 'Student Voter'), ('Admin', 'Administrator')],
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        })
    )

class VoterRegistrationForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Email address'
        })
    )
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First name'
        })
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last name'
        })
    )
    reg_number = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '(e.g. SCT221-0000/2021)'
        })
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Phone number (optional)'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Username'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm password'
        })

    def clean_reg_number(self):
        reg_number = self.cleaned_data.get('reg_number')
        
        # Check if registration number exists in student registry
        if not StudentRegistry.objects.filter(reg_number=reg_number, is_active=True).exists():
            raise forms.ValidationError('Invalid registration number. Please contact the administration.')
        
        # Check if registration number is already used
        if VoterProfile.objects.filter(reg_number=reg_number).exists():
            raise forms.ValidationError('This registration number is already registered.')
        
        return reg_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        if commit:
            user.save()
            
            # Get student info from registry
            student = StudentRegistry.objects.get(reg_number=self.cleaned_data['reg_number'])
            
            VoterProfile.objects.create(
                user=user,
                category='Voter',
                reg_number=self.cleaned_data['reg_number'],
                phone=self.cleaned_data.get('phone', ''),
                department=student.department,
                year_of_study=student.year_of_study,
                is_approved=True
            )
        return user
