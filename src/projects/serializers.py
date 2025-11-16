from rest_framework import serializers
from .models import Project, DataSource, Report, Analytic, AIIntegration


class DataSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = DataSource
        fields = ['id', 'name', 'type', 'description', 'order']


class ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Report
        fields = ['id', 'name', 'frequency', 'description', 'order']


class AnalyticSerializer(serializers.ModelSerializer):
    class Meta:
        model = Analytic
        fields = ['id', 'name', 'type', 'description', 'order']


class AIIntegrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = AIIntegration
        fields = ['id', 'enabled', 'features', 'models']


class ProjectListSerializer(serializers.ModelSerializer):
    """Serializer for list view - lighter data"""
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'status', 'description', 'progress',
            'due_date', 'team_size', 'tasks'
        ]

    def get_tasks(self, obj):
        return {
            'total': obj.tasks_total,
            'completed': obj.tasks_completed
        }


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Serializer for detail view - full data"""
    data_sources = DataSourceSerializer(many=True, read_only=True)
    reports = ReportSerializer(many=True, read_only=True)
    analytics = AnalyticSerializer(many=True, read_only=True)
    ai_integration = AIIntegrationSerializer(read_only=True)
    tasks = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'status', 'description', 'progress',
            'due_date', 'team_size', 'tasks', 'budget',
            'implementation_time', 'last_update',
            'digitalpath_responsible', 'client_responsible',
            'client_company', 'full_scope',
            'data_sources', 'reports', 'analytics', 'ai_integration',
            'created_at', 'updated_at'
        ]

    def get_tasks(self, obj):
        return {
            'total': obj.tasks_total,
            'completed': obj.tasks_completed
        }
