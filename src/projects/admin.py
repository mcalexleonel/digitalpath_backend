from django.contrib import admin
from .models import Project, DataSource, Report, Analytic, AIIntegration


class DataSourceInline(admin.TabularInline):
    model = DataSource
    extra = 1
    fields = ['name', 'type', 'description', 'order']


class ReportInline(admin.TabularInline):
    model = Report
    extra = 1
    fields = ['name', 'frequency', 'description', 'order']


class AnalyticInline(admin.TabularInline):
    model = Analytic
    extra = 1
    fields = ['name', 'type', 'description', 'order']


class AIIntegrationInline(admin.StackedInline):
    model = AIIntegration
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'progress', 'budget', 'due_date', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description', 'client_company']
    inlines = [DataSourceInline, ReportInline, AnalyticInline, AIIntegrationInline]

    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'status', 'description', 'progress', 'due_date')
        }),
        ('Team', {
            'fields': ('team_size', 'digitalpath_responsible', 'client_responsible', 'client_company')
        }),
        ('Tasks', {
            'fields': ('tasks_total', 'tasks_completed')
        }),
        ('Project Details', {
            'fields': ('budget', 'implementation_time', 'last_update', 'full_scope')
        }),
    )
