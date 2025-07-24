from django.db import models
from django.contrib.auth.models import User
from cryptography.fernet import Fernet
from django.conf import settings
import logging

logger = logging.getLogger('election')

class Position(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='candidates/', blank=True, null=True)
    position = models.ForeignKey(Position, on_delete=models.CASCADE, related_name='candidates')
    vote_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['position', 'name']
        unique_together = ['name', 'position']
    
    def __str__(self):
        return f"{self.name} - {self.position.name}"
    
    def get_vote_percentage(self):
        total_votes = sum(c.vote_count for c in self.position.candidates.filter(is_active=True))
        if total_votes == 0:
            return 0
        return round((self.vote_count / total_votes) * 100, 1)

class ElectionSettings(models.Model):
    name = models.CharField(max_length=200, default="Student Government Election")
    is_active = models.BooleanField(default=True)
    voting_start = models.DateTimeField(null=True, blank=True)
    voting_end = models.DateTimeField(null=True, blank=True)
    results_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Election Settings"
        verbose_name_plural = "Election Settings"
    
    def __str__(self):
        return self.name
    
    @classmethod
    def get_current(cls):
        return cls.objects.filter(is_active=True).first()

class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('LOGIN', 'Login'),
        ('LOGOUT', 'Logout'),
        ('VOTE', 'Vote Cast'),
        ('ADMIN_ACTION', 'Admin Action'),
        ('PDF_EXPORT', 'PDF Export'),
        ('CANDIDATE_ADD', 'Candidate Added'),
        ('CANDIDATE_UPDATE', 'Candidate Updated'),
        ('CANDIDATE_DELETE', 'Candidate Deleted'),
        ('POSITION_ADD', 'Position Added'),
        ('POSITION_UPDATE', 'Position Updated'),
        ('POSITION_DELETE', 'Position Deleted'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.action} - {self.user} - {self.timestamp}"
    
    @classmethod
    def log_action(cls, user, action, description, request=None):
        ip_address = None
        user_agent = ''
        
        if request:
            ip_address = cls.get_client_ip(request)
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        log_entry = cls.objects.create(
            user=user,
            action=action,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        # Also log to file
        logger.info(f"AUDIT: {action} - User: {user} - Description: {description} - IP: {ip_address}")
        
        return log_entry
    
    @staticmethod
    def get_client_ip(request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
