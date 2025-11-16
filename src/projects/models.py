from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Project(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('on_hold', 'On Hold'),
        ('planning', 'Planning'),
    ]

    # Basic Information
    name = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    description = models.TextField()
    progress = models.IntegerField(default=0)  # 0-100
    due_date = models.CharField(max_length=50)

    # Team Information
    team_size = models.IntegerField(default=1)
    digitalpath_responsible = models.CharField(max_length=100)
    client_responsible = models.CharField(max_length=100)
    client_company = models.CharField(max_length=255, default='Health Fund Australia')

    # Tasks
    tasks_total = models.IntegerField(default=0)
    tasks_completed = models.IntegerField(default=0)

    # Project Details
    budget = models.CharField(max_length=50)
    implementation_time = models.CharField(max_length=50)
    last_update = models.CharField(max_length=50)
    full_scope = models.TextField()

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class DataSource(models.Model):
    project = models.ForeignKey(Project, related_name='data_sources', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    description = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class Report(models.Model):
    project = models.ForeignKey(Project, related_name='reports', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    frequency = models.CharField(max_length=100)
    description = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class Analytic(models.Model):
    project = models.ForeignKey(Project, related_name='analytics', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    description = models.TextField()
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.project.name} - {self.name}"


class AIIntegration(models.Model):
    project = models.OneToOneField(Project, related_name='ai_integration', on_delete=models.CASCADE)
    enabled = models.BooleanField(default=False)
    features = models.JSONField(default=list)  # List of features
    models = models.JSONField(default=list)  # List of ML models

    def __str__(self):
        return f"{self.project.name} - AI Integration"
