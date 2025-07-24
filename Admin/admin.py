from django.contrib import admin
from .models import Position, Candidate, ElectionSettings, AuditLog

@admin.register(Position)
class PositionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'order', 'is_active', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')
    ordering = ('order', 'name')

@admin.register(Candidate)
class CandidateAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'vote_count', 'is_active', 'created_at')
    list_filter = ('position', 'is_active')
    search_fields = ('name', 'bio')
    ordering = ('position', 'name')

@admin.register(ElectionSettings)
class ElectionSettingsAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active', 'voting_start', 'voting_end', 'results_published')
    list_filter = ('is_active', 'results_published')
    search_fields = ('name',)

@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'user', 'action', 'description', 'ip_address')
    list_filter = ('action', 'timestamp')
    search_fields = ('user__username', 'description', 'ip_address')
    readonly_fields = ('timestamp', 'user', 'action', 'description', 'ip_address', 'user_agent')
    ordering = ('-timestamp',)

    def has_add_permission(self, request):
        return False  # Prevent manual creation of audit logs

    def has_change_permission(self, request, obj=None):
        return False  # Prevent editing of audit logs
