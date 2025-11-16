from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Project, DataSource, Report, Analytic, AIIntegration
from .serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    DataSourceSerializer,
    ReportSerializer,
    AnalyticSerializer,
    AIIntegrationSerializer
)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    API endpoint for projects
    List: GET /api/projects/
    Detail: GET /api/projects/{id}/
    Create: POST /api/projects/
    Update: PUT /api/projects/{id}/
    Delete: DELETE /api/projects/{id}/
    """
    queryset = Project.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectDetailSerializer

    @action(detail=False, methods=['get'])
    def summary(self, request):
        """
        GET /api/projects/summary/
        Returns summary statistics for projects
        """
        projects = self.get_queryset()
        total = projects.count()
        active = projects.filter(status='active').count()
        completed = projects.filter(status='completed').count()
        on_hold = projects.filter(status='on_hold').count()
        planning = projects.filter(status='planning').count()

        # Calculate average progress
        avg_progress = 0
        if total > 0:
            total_progress = sum(p.progress for p in projects)
            avg_progress = round(total_progress / total)

        return Response({
            'total': total,
            'active': active,
            'completed': completed,
            'on_hold': on_hold,
            'planning': planning,
            'average_progress': avg_progress
        })
