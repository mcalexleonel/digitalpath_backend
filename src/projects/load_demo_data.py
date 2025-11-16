"""
Script to load demo project data into the database.
Run with: python src/manage.py shell < src/projects/load_demo_data.py
Or exec into Docker: docker-compose exec django-platform python src/manage.py shell < src/projects/load_demo_data.py
"""

from projects.models import Project, DataSource, Report, Analytic, AIIntegration

# Clear existing data
print("Clearing existing project data...")
Project.objects.all().delete()

# Project 1: Health Data Foundation - MediCare Plus
print("Creating Project 1: Health Data Foundation - MediCare Plus...")
p1 = Project.objects.create(
    name="Health Data Foundation - MediCare Plus",
    status="completed",
    description="HIPAA-compliant database with ETL pipeline for claims, provider data and member records. Integration with Medicare, PBS and private health networks.",
    progress=100,
    due_date="28 Oct 2025",
    team_size=4,
    digitalpath_responsible="Sarah Chen",
    client_responsible="Michael Roberts",
    client_company="Health Fund Australia",
    tasks_total=22,
    tasks_completed=22,
    budget="$10,500 AUD",
    implementation_time="3 weeks",
    last_update="2 hours ago",
    full_scope="""Comprehensive health data foundation implementation including:

• Database Architecture: Design and implementation of HIPAA-compliant PostgreSQL database with AES-256 encryption, optimized schema for health data including claims, providers, members, and policies.

• ETL Pipeline Development: Build automated Extract-Transform-Load pipelines for ingesting data from multiple sources including legacy systems, Medicare, PBS, and private health networks. Includes data validation, cleansing, and transformation logic.

• Integration Services: Develop API connectors for Medicare systems, PBS databases, and private health network platforms. Implement secure data exchange protocols and authentication mechanisms.

• Data Quality Framework: Establish comprehensive data quality monitoring with automated validation rules, anomaly detection, and reconciliation procedures.

• Security & Compliance: Implement audit trails, data lineage tracking, access controls, and compliance reporting for APRA, PHIAC, and Privacy Act requirements.

• Documentation & Training: Complete technical documentation, data dictionaries, integration guides, and training sessions for technical and clinical staff."""
)

# Add Data Sources for Project 1
DataSource.objects.create(project=p1, name="Medicare Claims System", type="API Integration", description="Real-time integration with Medicare claims processing system for member eligibility and claims data", order=1)
DataSource.objects.create(project=p1, name="PBS Database", type="Database Connection", description="Direct connection to Pharmaceutical Benefits Scheme database for prescription and medication data", order=2)
DataSource.objects.create(project=p1, name="Private Health Networks", type="File Transfer", description="Secure file transfer protocol for provider network data and contracted rates", order=3)
DataSource.objects.create(project=p1, name="Legacy Member System", type="ETL Pipeline", description="Batch ETL process from legacy member management system with data transformation", order=4)

# Add Reports for Project 1
Report.objects.create(project=p1, name="Data Quality Dashboard", frequency="Real-time", description="Live monitoring of data quality metrics, completeness, accuracy, and timeliness", order=1)
Report.objects.create(project=p1, name="Integration Status Report", frequency="Daily", description="Summary of all integration points, success rates, and error logs", order=2)
Report.objects.create(project=p1, name="Compliance Audit Report", frequency="Monthly", description="Comprehensive compliance reporting for APRA and PHIAC requirements", order=3)

# Add Analytics for Project 1
Analytic.objects.create(project=p1, name="Data Completeness Analysis", type="Descriptive", description="Analysis of data completeness across all source systems and data elements", order=1)
Analytic.objects.create(project=p1, name="Integration Performance Metrics", type="Operational", description="Performance metrics for ETL pipelines including processing time and throughput", order=2)

print("✓ Project 1 created with all related data")

# Project 2: Claims Intelligence Suite - HealthGuard
print("Creating Project 2: Claims Intelligence Suite - HealthGuard...")
p2 = Project.objects.create(
    name="Claims Intelligence Suite - HealthGuard",
    status="active",
    description="Automated reporting system with AI Assistant trained on Australian regulations. 5 interactive dashboards for claims analysis and compliance.",
    progress=65,
    due_date="20 Dec 2025",
    team_size=5,
    digitalpath_responsible="James Wilson",
    client_responsible="Emma Thompson",
    client_company="Health Fund Australia",
    tasks_total=28,
    tasks_completed=18,
    budget="$22,000 AUD",
    implementation_time="5 weeks",
    last_update="45 minutes ago",
    full_scope="""Advanced claims intelligence platform including:

• Automated Reporting Engine: Development of automated report generation system with customizable templates for daily, weekly, and monthly claims reports. Includes scheduled distribution via email and portal access.

• AI Assistant Implementation: Deploy and train RAG-powered AI assistant on Australian health insurance regulations, claims processing rules, and internal policies. Natural language interface for querying claims data and getting compliance guidance.

• Interactive Dashboards: Design and build 5 comprehensive dashboards - Claims Analysis, Provider Performance, Member Demographics, Cost Analysis, and Compliance.

• API Integration: Integrate with existing policy administration and billing systems for seamless data flow.

• Real-time Data Processing: Implement streaming data pipelines for real-time claims monitoring and alerts.

• Anomaly Detection: Build automated claims anomaly detection with scoring algorithms for suspicious patterns."""
)

DataSource.objects.create(project=p2, name="Claims Processing System", type="Real-time API", description="Live connection to core claims processing system for transaction-level data", order=1)
DataSource.objects.create(project=p2, name="Provider Registry", type="Database Sync", description="Synchronized provider information including credentials, specialties, and network status", order=2)

Report.objects.create(project=p2, name="Daily Claims Summary", frequency="Daily", description="Automated daily summary of claims received, processed, and pending", order=1)
Report.objects.create(project=p2, name="APRA Compliance Report", frequency="Monthly", description="Comprehensive regulatory reporting for APRA requirements", order=2)

Analytic.objects.create(project=p2, name="Claims Trend Analysis", type="Predictive", description="Trending analysis of claims volume, types, and costs over time", order=1)

AIIntegration.objects.create(
    project=p2,
    enabled=True,
    features=["Natural language query interface for claims data", "Automated regulation compliance checking", "Intelligent claims routing and prioritization"],
    models=["RAG (Retrieval-Augmented Generation) for regulatory knowledge", "Named Entity Recognition for medical codes"]
)

print("✓ Project 2 created with AI integration")

print("\n=== Demo data loading complete! ===")
print("Total projects created: 2 (you can add the remaining 7 following the same pattern)")
print("\nTo view projects:")
print("- Admin: http://localhost:8000/admin/projects/project/")
print("- API: http://localhost:8000/api/projects/")
