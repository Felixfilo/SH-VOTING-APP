from django.db import models
from django.contrib.auth.models import User
from Admin.models import Candidate, AuditLog
from cryptography.fernet import Fernet
from django.conf import settings
import json
import logging

logger = logging.getLogger('election')

class StudentRegistry(models.Model):
    """Model to store valid student registration numbers"""
    reg_number = models.CharField(max_length=20, unique=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    department = models.CharField(max_length=100)
    year_of_study = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.reg_number} - {self.full_name}"

class VoterProfile(models.Model):
    CATEGORY_CHOICES = [
        ('Admin', 'Admin'),
        ('Voter', 'Voter'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES, default='Voter')
    reg_number = models.CharField(max_length=20, unique=True, null=True, blank=True)
    has_voted = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)  # For admin approval workflow
    phone = models.CharField(max_length=15, blank=True)
    department = models.CharField(max_length=100, blank=True)
    year_of_study = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.category})"
    
    def is_eligible_voter(self):
        """Check if the voter is eligible to vote"""
        if self.category != 'Voter':
            return False
        
        # Check if registration number exists in student registry
        if self.reg_number:
            return StudentRegistry.objects.filter(
                reg_number=self.reg_number,
                is_active=True
            ).exists()
        
        return False

class EncryptedVote(models.Model):
    """Model to store encrypted votes for ballot secrecy"""
    voter_hash = models.CharField(max_length=64)  # Hashed voter identifier
    encrypted_vote_data = models.TextField()  # Encrypted vote information
    position_id = models.IntegerField()  # Position voted for
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['voter_hash', 'position_id']
    
    def __str__(self):
        return f"Encrypted Vote - Position {self.position_id} - {self.timestamp}"
    
    @classmethod
    def cast_vote(cls, voter, candidate):
        """Cast an encrypted vote"""
        import hashlib
        
        # Create a hash of the voter for anonymity
        voter_hash = hashlib.sha256(f"{voter.id}_{voter.reg_number}".encode()).hexdigest()
        
        # Prepare vote data
        vote_data = {
            'candidate_id': candidate.id,
            'candidate_name': candidate.name,
            'position_id': candidate.position.id,
            'position_name': candidate.position.name,
            'timestamp': str(timezone.now())
        }
        
        # Encrypt the vote data
        fernet = Fernet(settings.VOTE_ENCRYPTION_KEY.encode())
        encrypted_data = fernet.encrypt(json.dumps(vote_data).encode()).decode()
        
        # Store the encrypted vote
        encrypted_vote = cls.objects.create(
            voter_hash=voter_hash,
            encrypted_vote_data=encrypted_data,
            position_id=candidate.position.id
        )
        
        # Update candidate vote count
        candidate.vote_count += 1
        candidate.save()
        
        # Log the vote action
        AuditLog.log_action(
            user=voter.user,
            action='VOTE',
            description=f"Vote cast for position: {candidate.position.name}"
        )
        
        return encrypted_vote
    
    @classmethod
    def decrypt_vote(cls, encrypted_vote):
        """Decrypt a vote for admin purposes (if needed)"""
        try:
            fernet = Fernet(settings.VOTE_ENCRYPTION_KEY.encode())
            decrypted_data = fernet.decrypt(encrypted_vote.encrypted_vote_data.encode())
            return json.loads(decrypted_data.decode())
        except Exception as e:
            logger.error(f"Failed to decrypt vote: {e}")
            return None

class Vote(models.Model):
    """Traditional vote model for tracking (non-encrypted for admin purposes)"""
    voter = models.ForeignKey(VoterProfile, on_delete=models.CASCADE)
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['voter', 'candidate']
    
    def __str__(self):
        return f"Vote - Position: {self.candidate.position.name} - {self.timestamp}"

# Import timezone after models are defined
from django.utils import timezone
