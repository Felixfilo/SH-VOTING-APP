from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Sum
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils import timezone
from datetime import datetime
import io

from .models import Position, Candidate, ElectionSettings, AuditLog
from .forms import PositionForm, CandidateForm, ElectionSettingsForm, AdminRegistrationForm, StudentRegistryForm
from Voters.models import VoterProfile, Vote, EncryptedVote, StudentRegistry

# WeasyPrint for PDF generation
PDF_AVAILABLE = False
weasyprint_html = None

try:
    from weasyprint import HTML
    weasyprint_html = HTML
    PDF_AVAILABLE = True
except ImportError:
    pass

def is_admin(user):
    if not user.is_authenticated:
        return False
    try:
        profile = VoterProfile.objects.get(user=user)
        return profile.category == 'Admin' and profile.is_approved
    except VoterProfile.DoesNotExist:
        return user.is_staff or user.is_superuser

@login_required
@user_passes_test(is_admin)
def manage_students(request):
    students = StudentRegistry.objects.all().order_by('-created_at')
    form = StudentRegistryForm()

    if request.method == 'POST':
        form = StudentRegistryForm(request.POST)
        if form.is_valid():
            student = form.save()
            
            # Log the student registration
            AuditLog.log_action(
                user=request.user,
                action='ADMIN_ACTION',
                description=f"Added student to registry: {student.reg_number} - {student.full_name}",
                request=request
            )
            
            messages.success(request, f'Student {student.full_name} has been added to the registry.')
            return redirect('admin_manage_students')
        else:
            messages.error(request, 'Please correct the errors below.')

    context = {
        'students': students,
        'form': form
    }
    return render(request, 'admin/manage_students.html', context)

def admin_register(request):
    if request.method == 'POST':
        form = AdminRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            
            # Log the admin registration
            AuditLog.log_action(
                user=user,
                action='ADMIN_ACTION',
                description=f"New admin registered: {user.username}",
                request=request
            )
            
            messages.success(request, 'Admin account created successfully! You can now log in.')
            return redirect('login')
    else:
        form = AdminRegistrationForm()
    
    return render(request, 'registration/admin_register.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def admin_dashboard(request):
    positions = Position.objects.filter(is_active=True)
    candidates = Candidate.objects.select_related('position').all()  # Removed is_active filter to see all candidates
    voters = VoterProfile.objects.filter(category='Voter', is_approved=True)
    votes = Vote.objects.all()
    encrypted_votes = EncryptedVote.objects.all()
    
    # Election settings
    election_settings = ElectionSettings.get_current()
    
    # Statistics
    total_voters = voters.count()
    voted_count = voters.filter(has_voted=True).count()
    total_votes = votes.count()
    total_encrypted_votes = encrypted_votes.count()
    
    # Recent audit logs
    recent_logs = AuditLog.objects.all()[:10]
    
    # Vote statistics by position
    vote_stats = []
    for position in positions:
        # Use Candidate model's reverse lookup instead of position.candidates
        position_candidates = Candidate.objects.filter(position=position, is_active=True)
        position_votes = Vote.objects.filter(candidate__in=position_candidates)
        vote_stats.append({
            'position': position,
            'candidates': position_candidates,
            'total_votes': position_votes.count()
        })
    
    
    
    context = {
        'positions': positions,
        'candidates': candidates,
        'total_voters': total_voters,
        'voted_count': voted_count,
        'total_votes': total_votes,
        'total_encrypted_votes': total_encrypted_votes,
        'vote_stats': vote_stats,
        'recent_logs': recent_logs,
        'election_settings': election_settings,
        'pdf_available': PDF_AVAILABLE,
    }
    
    
    return render(request, 'admin/admin_dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def add_position(request):
    if request.method == 'POST':
        form = PositionForm(request.POST)
        if form.is_valid():
            position = form.save()
            
            # Log the action
            AuditLog.log_action(
                user=request.user,
                action='POSITION_ADD',
                description=f"Position added: {position.name}",
                request=request
            )
            
            messages.success(request, f'Position "{position.name}" added successfully!')
            return redirect('admin_dashboard')
    else:
        form = PositionForm()
    
    return render(request, 'admin/position_form.html', {
        'form': form,
        'title': 'Add Position'
    })

@login_required
@user_passes_test(is_admin)
def edit_position(request, position_id):
    position = get_object_or_404(Position, id=position_id)
    
    if request.method == 'POST':
        form = PositionForm(request.POST, instance=position)
        if form.is_valid():
            position = form.save()
            
            # Log the action
            AuditLog.log_action(
                user=request.user,
                action='POSITION_UPDATE',
                description=f"Position updated: {position.name}",
                request=request
            )
            
            messages.success(request, f'Position "{position.name}" updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = PositionForm(instance=position)
    
    return render(request, 'admin/position_form.html', {
        'form': form,
        'title': 'Edit Position',
        'position': position
    })

@login_required
@user_passes_test(is_admin)
def delete_position(request, position_id):
    position = get_object_or_404(Position, id=position_id)
    position_name = position.name
    position.delete()
    
    # Log the action
    AuditLog.log_action(
        user=request.user,
        action='POSITION_DELETE',
        description=f"Position deleted: {position_name}",
        request=request
    )
    
    messages.success(request, f'Position "{position_name}" deleted successfully!')
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def add_candidate(request):
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES)
        if form.is_valid():
            candidate = form.save()
            
            # Log the action
            AuditLog.log_action(
                user=request.user,
                action='CANDIDATE_ADD',
                description=f"Candidate added: {candidate.name} for {candidate.position.name}",
                request=request
            )
            
            messages.success(request, f'Candidate "{candidate.name}" added successfully!')
            return redirect('admin_dashboard')
    else:
        form = CandidateForm()
    
    return render(request, 'admin/candidate_form.html', {
        'form': form,
        'title': 'Add Candidate'
    })

@login_required
@user_passes_test(is_admin)
def edit_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    
    if request.method == 'POST':
        form = CandidateForm(request.POST, request.FILES, instance=candidate)
        if form.is_valid():
            candidate = form.save()
            
            # Log the action
            AuditLog.log_action(
                user=request.user,
                action='CANDIDATE_UPDATE',
                description=f"Candidate updated: {candidate.name} for {candidate.position.name}",
                request=request
            )
            
            messages.success(request, f'Candidate "{candidate.name}" updated successfully!')
            return redirect('admin_dashboard')
    else:
        form = CandidateForm(instance=candidate)
    
    return render(request, 'admin/candidate_form.html', {
        'form': form,
        'title': 'Edit Candidate',
        'candidate': candidate
    })

@login_required
@user_passes_test(is_admin)
def delete_candidate(request, candidate_id):
    candidate = get_object_or_404(Candidate, id=candidate_id)
    candidate_name = candidate.name
    candidate.delete()
    
    # Log the action
    AuditLog.log_action(
        user=request.user,
        action='CANDIDATE_DELETE',
        description=f"Candidate deleted: {candidate_name}",
        request=request
    )
    
    messages.success(request, f'Candidate "{candidate_name}" deleted successfully!')
    return redirect('admin_dashboard')

@login_required
@user_passes_test(is_admin)
def results_view(request):
    election_settings = ElectionSettings.get_current()
    
    # Check if results should be published
    if not election_settings or not election_settings.results_published:
        messages.warning(request, 'Results are not yet published.')
        return redirect('admin_dashboard')
    
    positions = Position.objects.filter(is_active=True).prefetch_related('candidates')
    
    results_data = []
    for position in positions:
        # Get candidates through the reverse relationship
        candidates_data = []
        total_position_votes = 0
        
        # Use Candidate model's reverse lookup instead of position.candidates
        position_candidates = Candidate.objects.filter(position=position, is_active=True)
        for candidate in position_candidates:
            vote_count = Vote.objects.filter(candidate=candidate).count()
            candidate.vote_count = vote_count
            total_position_votes += vote_count
            candidates_data.append(candidate)
        
        # Calculate percentages
        for candidate in candidates_data:
            if total_position_votes > 0:
                candidate.percentage = round((candidate.vote_count / total_position_votes) * 100, 1)
            else:
                candidate.percentage = 0
        
        # Sort by vote count (descending)
        candidates_data.sort(key=lambda x: x.vote_count, reverse=True)
        
        results_data.append({
            'position': position,
            'candidates': candidates_data,
            'total_votes': total_position_votes
        })
    
    context = {
        'results_data': results_data,
        'total_voters': VoterProfile.objects.filter(category='Voter', is_approved=True).count(),
        'voted_count': VoterProfile.objects.filter(category='Voter', has_voted=True).count(),
        'election_settings': election_settings,
    }
    
    return render(request, 'admin/results.html', context)

@login_required
@user_passes_test(is_admin)
def export_results_pdf(request):
    if not PDF_AVAILABLE:
        messages.error(request, 'PDF export is not available. Please install WeasyPrint.')
        return redirect('results_view')
    
    election_settings = ElectionSettings.get_current()
    positions = Position.objects.filter(is_active=True).prefetch_related('candidates')
    
    results_data = []
    total_all_votes = 0
    
    for position in positions:
        candidates_data = []
        total_position_votes = 0
        
        # Use Candidate model's reverse lookup
        position_candidates = Candidate.objects.filter(position=position, is_active=True)
        for candidate in position_candidates:
            vote_count = Vote.objects.filter(candidate=candidate).count()
            candidate.vote_count = vote_count
            total_position_votes += vote_count
            candidates_data.append(candidate)
        
        # Calculate percentages
        for candidate in candidates_data:
            if total_position_votes > 0:
                candidate.percentage = round((candidate.vote_count / total_position_votes) * 100, 1)
            else:
                candidate.percentage = 0
        
        # Sort by vote count (descending)
        candidates_data.sort(key=lambda x: x.vote_count, reverse=True)
        
        results_data.append({
            'position': position,
            'candidates': candidates_data,
            'total_votes': total_position_votes
        })
        
        total_all_votes += total_position_votes
    
    context = {
        'results_data': results_data,
        'total_voters': VoterProfile.objects.filter(category='Voter', is_approved=True).count(),
        'voted_count': VoterProfile.objects.filter(category='Voter', has_voted=True).count(),
        'total_all_votes': total_all_votes,
        'generation_date': timezone.now(),
        'admin_name': request.user.get_full_name() or request.user.username,
        'election_settings': election_settings,
    }
    
    # Render HTML template
    html_string = render_to_string('admin/export_results.html', context)
    
    # Generate PDF
    if not weasyprint_html:
        messages.error(request, 'PDF export is not available. WeasyPrint HTML functionality is missing.')
        return redirect('results_view')
        
    html = weasyprint_html(string=html_string, base_url=request.build_absolute_uri())
    pdf = html.write_pdf()
    
    # Log the PDF export
    AuditLog.log_action(
        user=request.user,
        action='PDF_EXPORT',
        description="Election results exported to PDF",
        request=request
    )
    
    # Create response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="election_results_{timezone.now().strftime("%Y%m%d_%H%M%S")}.pdf"'
    
    return response

@login_required
@user_passes_test(is_admin)
def audit_logs(request):
    logs = AuditLog.objects.all()[:100]  # Last 100 logs
    return render(request, 'admin/audit_logs.html', {'logs': logs})

@login_required
@user_passes_test(is_admin)
def election_settings(request):
    settings_obj = ElectionSettings.get_current()
    
    if request.method == 'POST':
        if settings_obj:
            form = ElectionSettingsForm(request.POST, instance=settings_obj)
        else:
            form = ElectionSettingsForm(request.POST)
        
        if form.is_valid():
            settings_obj = form.save()
            
            # Log the action
            AuditLog.log_action(
                user=request.user,
                action='ADMIN_ACTION',
                description="Election settings updated",
                request=request
            )
            
            messages.success(request, 'Election settings updated successfully!')
            return redirect('admin_dashboard')
    else:
        if settings_obj:
            form = ElectionSettingsForm(instance=settings_obj)
        else:
            form = ElectionSettingsForm()
    
    return render(request, 'admin/election_settings.html', {
        'form': form,
        'settings_obj': settings_obj
    })
