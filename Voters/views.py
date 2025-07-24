from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction, models
from django.http import Http404
from django.utils import timezone

from Voters.forms import CustomLoginForm, VoterRegistrationForm
from .models import VoterProfile, Vote, EncryptedVote, StudentRegistry
from Admin.models import Position, Candidate, ElectionSettings, AuditLog

def custom_404(request, exception):
    return render(request, '404.html', status=404)

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            category = form.cleaned_data['category']
            
            # Try to authenticate with username first
            user = authenticate(request, username=username, password=password)
            
            # If username auth fails and category is Voter, try with reg_number
            if not user and category == 'Voter':
                try:
                    profile = VoterProfile.objects.get(reg_number=username)
                    user = authenticate(request, username=profile.user.username, password=password)
                except VoterProfile.DoesNotExist:
                    pass
            
            if user is not None:
                # Get or create voter profile
                profile, created = VoterProfile.objects.get_or_create(
                    user=user,
                    defaults={'category': category}
                )
                
                # Check if user category matches and is approved
                if profile.category == category and profile.is_approved:
                    login(request, user)
                    
                    # Log the login
                    AuditLog.log_action(
                        user=user,
                        action='LOGIN',
                        description=f"User logged in as {category}",
                        request=request
                    )
                    
                    if category == 'Admin' or user.is_staff:
                        return redirect('admin_dashboard')
                    else:
                        return redirect('dashboard')
                else:
                    if not profile.is_approved:
                        messages.error(request, 'Your account is pending approval.')
                    else:
                        messages.error(request, 'Invalid login category for your account.')
            else:
                messages.error(request, 'Invalid credentials.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'registration/login.html', {'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = VoterRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Log the registration
            AuditLog.log_action(
                user=user,
                action='ADMIN_ACTION',
                description=f"New voter registered: {user.username}",
                request=request
            )
            
            messages.success(request, 'Registration successful! You can now log in.')
            return redirect('login')
    else:
        form = VoterRegistrationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    # Get or create voter profile
    profile, created = VoterProfile.objects.get_or_create(
        user=request.user,
        defaults={'category': 'Voter'}
    )
    
    # Redirect admin users to admin dashboard
    if profile.category == 'Admin' or request.user.is_staff:
        return redirect('admin_dashboard')
    
    # Check if voter is eligible
    if not profile.is_eligible_voter():
        messages.error(request, 'You are not eligible to vote. Please contact the administration.')
        return render(request, 'voters/not_eligible.html')
    
    # Check election settings
    election_settings = ElectionSettings.get_current()
    if not election_settings or not election_settings.is_active:
        messages.info(request, 'No active election at this time.')
        return render(request, 'voters/no_election.html')
    
    # Check voting period
    now = timezone.now()
    if election_settings.voting_start and now < election_settings.voting_start:
        messages.info(request, f'Voting has not started yet. Voting starts on {election_settings.voting_start}.')
        return render(request, 'voters/voting_not_started.html', {'election_settings': election_settings})
    
    if election_settings.voting_end and now > election_settings.voting_end:
        messages.info(request, 'Voting has ended.')
        return render(request, 'voters/voting_ended.html', {'election_settings': election_settings})
    
    positions = Position.objects.filter(is_active=True).prefetch_related(
        models.Prefetch(
            'candidates',
            queryset=Candidate.objects.filter(is_active=True)
        )
    )
    
    # Get user's votes
    user_votes = Vote.objects.filter(voter=profile).values_list('candidate_id', flat=True)
    
    # Check if user has voted in any position
    has_voted = Vote.objects.filter(voter=profile).exists()
    
    context = {
        'positions': positions,
        'profile': profile,
        'has_voted': has_voted,
        'user_votes': list(user_votes),
        'election_settings': election_settings,
    }
    
    return render(request, 'voters/voter_dashboard.html', context)

@login_required
def vote_confirm(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id, is_active=True)
    profile = get_object_or_404(VoterProfile, user=request.user)
    
    # Check if user is admin
    if profile.category == 'Admin':
        messages.error(request, 'Administrators cannot vote.')
        return redirect('admin_dashboard')
    
    # Check if voter is eligible
    if not profile.is_eligible_voter():
        messages.error(request, 'You are not eligible to vote.')
        return redirect('dashboard')
    
    # Check election settings
    election_settings = ElectionSettings.get_current()
    if not election_settings or not election_settings.is_active:
        messages.error(request, 'No active election at this time.')
        return redirect('dashboard')
    
    # Check voting period
    now = timezone.now()
    if election_settings.voting_start and now < election_settings.voting_start:
        messages.error(request, 'Voting has not started yet.')
        return redirect('dashboard')
    
    if election_settings.voting_end and now > election_settings.voting_end:
        messages.error(request, 'Voting has ended.')
        return redirect('dashboard')
    
    # Check if already voted for this position
    existing_vote = Vote.objects.filter(
        voter=profile,
        candidate__position=candidate.position
    ).first()
    
    if existing_vote:
        return render(request, 'voters/already_voted.html', {
            'candidate': candidate,
            'existing_candidate': existing_vote.candidate
        })
    
    if request.method == 'POST':
        with transaction.atomic():
            # Create traditional vote record
            Vote.objects.create(voter=profile, candidate=candidate)
            
            # Create encrypted vote for ballot secrecy
            EncryptedVote.cast_vote(profile, candidate)
            
            # Check if user has voted for all positions
            total_positions = Position.objects.filter(is_active=True).count()
            user_votes = Vote.objects.filter(voter=profile).count()
            
            if user_votes >= total_positions:
                profile.has_voted = True
                profile.save()
        
        return redirect('vote_success')
    
    return render(request, 'voters/vote_confirmation.html', {
        'candidate': candidate
    })

@login_required
def vote_success(request):
    profile = get_object_or_404(VoterProfile, user=request.user)
    return render(request, 'voters/vote_success.html', {'profile': profile})

@login_required
def already_voted_view(request):
    profile = get_object_or_404(VoterProfile, user=request.user)
    return render(request, 'voters/already_voted.html', {'profile': profile})

def logout_view(request):
    if request.method == 'POST':
        # Log the logout
        AuditLog.log_action(
            user=request.user,
            action='LOGOUT',
            description="User logged out",
            request=request
        )
        
        logout(request)
        messages.success(request, 'You have been logged out successfully.')
        return redirect('login')
    
    return render(request, 'registration/logout_confirmation.html')

# View for students not eligible to vote
def not_eligible_view(request):
    return render(request, 'voters/not_eligible.html')

# View when no election is active
def no_election_view(request):
    return render(request, 'voters/no_election.html')

# View when voting hasn't started
def voting_not_started_view(request):
    election_settings = ElectionSettings.get_current()
    return render(request, 'voters/voting_not_started.html', {'election_settings': election_settings})

# View when voting has ended
def voting_ended_view(request):
    election_settings = ElectionSettings.get_current()
    return render(request, 'voters/voting_ended.html', {'election_settings': election_settings})
