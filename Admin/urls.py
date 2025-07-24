from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_dashboard, name='admin_dashboard'),
    path('register/', views.admin_register, name='admin_register'),
    path('add-position/', views.add_position, name='add_position'),
    path('edit-position/<int:position_id>/', views.edit_position, name='edit_position'),
    path('delete-position/<int:position_id>/', views.delete_position, name='delete_position'),
    path('add-candidate/', views.add_candidate, name='add_candidate'),
    path('edit-candidate/<int:candidate_id>/', views.edit_candidate, name='edit_candidate'),
    path('delete-candidate/<int:candidate_id>/', views.delete_candidate, name='delete_candidate'),
    path('results/', views.results_view, name='results_view'),
    path('results/export/pdf/', views.export_results_pdf, name='export_results_pdf'),
    path('audit-logs/', views.audit_logs, name='audit_logs'),
    path('settings/', views.election_settings, name='election_settings'),
    path('manage-students/', views.manage_students, name='admin_manage_students'),
]
