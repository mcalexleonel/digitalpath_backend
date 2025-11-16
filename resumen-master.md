# DigitalPath AI - Django Backend - Resumen Master

**Documentación Técnica Completa**
**Versión:** 1.0
**Última actualización:** 2025-11-16

---

## Tabla de Contenidos

1. [Arquitectura General](#arquitectura-general)
2. [Apps y Módulos](#apps-y-módulos)
3. [Modelos de Datos](#modelos-de-datos)
4. [API Endpoints](#api-endpoints)
5. [Sistema de Autenticación](#sistema-de-autenticación)
6. [Sistema de Emails (Celery)](#sistema-de-emails-celery)
7. [Variables de Entorno](#variables-de-entorno)
8. [Deployment](#deployment)
9. [Troubleshooting](#troubleshooting)

---

## Arquitectura General

### Stack Tecnológico

```
┌─────────────────────────────────────────────┐
│           Next.js Frontend                  │
│         (localhost:3000)                    │
└──────────────┬──────────────────────────────┘
               │ HTTP/REST API
┌──────────────▼──────────────────────────────┐
│         Django Backend (port 8000)          │
│  ┌─────────────────────────────────────┐   │
│  │      Django Ninja API Layer         │   │
│  │  - JWT Authentication               │   │
│  │  - REST Endpoints                   │   │
│  └─────────────┬───────────────────────┘   │
│                │                            │
│  ┌─────────────▼───────────────────────┐   │
│  │     Django Apps Layer               │   │
│  │  - contact    - projects            │   │
│  │  - waitlists  - core                │   │
│  └─────────────┬───────────────────────┘   │
│                │                            │
│  ┌─────────────▼───────────────────────┐   │
│  │       Django ORM Layer              │   │
│  └─────────────┬───────────────────────┘   │
└────────────────┼────────────────────────────┘
                 │
    ┌────────────┼────────────┐
    │            │            │
┌───▼────┐  ┌───▼─────┐  ┌──▼──────┐
│ Postgres│  │ Redis   │  │ Celery  │
│  (Neon) │  │ (Queue) │  │ Worker  │
└─────────┘  └─────────┘  └─────────┘
```

### Componentes Principales

1. **Django Core**: Configuración principal, settings, URLs
2. **Django Ninja**: API framework rápido y tipado
3. **PostgreSQL (Neon)**: Base de datos en producción
4. **Redis**: Message broker para Celery
5. **Celery**: Worker para tareas asíncronas (emails)
6. **Django Allauth**: Autenticación social (Google, GitHub)

---

## Apps y Módulos

### 1. **contact** - Gestión de Formularios de Contacto

**Propósito**: Manejar formularios de contacto del sitio web y enviar emails de forma asíncrona.

**Estructura**:
```
contact/
├── models.py           # ContactMessage model
├── tasks.py            # Celery task para envío de emails
├── admin.py            # Admin con status badges
├── views.py            # Views legacy (no usadas)
└── urls.py             # URLs legacy (no usadas)
```

**Funcionalidades**:
- Guardar mensajes de contacto en BD
- Envío asíncrono de emails via Celery
- Tracking de estado (pending/sent/failed)
- Reintentos automáticos en caso de fallo
- Fallback a envío síncrono si Celery no disponible

**Flujo de Trabajo**:
```
1. Usuario envía form → POST /api/contact
2. Django guarda en BD (status=pending)
3. Dispatch Celery task → send_contact_email_task.delay(msg_id)
4. Celery worker procesa task
5. Email enviado → status=sent, sent_at=timestamp
6. Si falla → status=failed, error_message=error
```

---

### 2. **core** - Configuración Central

**Propósito**: Configuración principal de Django y endpoints centrales de API.

**Estructura**:
```
core/
├── settings.py         # Django settings
├── urls.py             # URL routing
├── api.py              # API endpoints (Django Ninja)
├── celery.py           # Celery configuration
├── __init__.py         # Celery app initialization
├── wsgi.py             # WSGI application
└── asgi.py             # ASGI application
```

**Configuraciones Clave**:
- CORS para Next.js frontend
- JWT authentication
- Email settings (SMTP)
- Celery broker/backend (Redis)
- Database (PostgreSQL/SQLite)
- Django Allauth (Social auth)

**API Endpoints** (ver sección completa más abajo):
- Authentication (signup, login, verify email, reset password)
- Contact form
- User info

---

### 3. **projects** - Gestión de Proyectos

**Propósito**: Sistema completo de gestión de proyectos de clientes con datos, reportes y analytics.

**Estructura**:
```
projects/
├── models.py           # Project, DataSource, Report, Analytic, AIIntegration
├── views.py            # ViewSets REST API
├── serializers.py      # DRF serializers
├── admin.py            # Django admin
├── urls.py             # API URLs
└── management/         # Django management commands
```

**Modelos**:
1. **Project**: Proyecto principal
2. **DataSource**: Fuentes de datos del proyecto
3. **Report**: Reportes generados
4. **Analytic**: Analytics y métricas
5. **AIIntegration**: Integraciones de IA

**Funcionalidades**:
- CRUD completo de proyectos
- Nested resources (data sources, reports, analytics)
- Summary statistics endpoint
- Filtrado por status, cliente, etc.

---

### 4. **waitlists** - Lista de Espera

**Propósito**: Gestión de lista de espera para nuevos usuarios.

**Estructura**:
```
waitlists/
├── models.py           # Waitlist model
├── api.py              # Django Ninja router
├── forms.py            # Forms
├── admin.py            # Admin interface
└── schemas.py          # Pydantic schemas
```

**Funcionalidades**:
- Registro en lista de espera
- Validación de emails
- Notificaciones automáticas

---

### 5. **helpers** - Utilidades

**Propósito**: Funciones helper y adaptadores personalizados.

**Archivos**:
- `api_auth.py`: Helpers de autenticación para API
- `socialaccount_adapter.py`: Adapter personalizado para social auth

---

## Modelos de Datos

### ContactMessage (contact/models.py)

```python
class ContactMessage(models.Model):
    # User data
    name = models.CharField(max_length=200)
    email = models.EmailField()
    message = models.TextField()

    # Status tracking
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('sent', 'Sent'),
            ('failed', 'Failed'),
        ],
        default='pending'
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    sent_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True, null=True)
```

**Campos**:
- `name`: Nombre del contacto
- `email`: Email del contacto
- `message`: Mensaje del formulario
- `status`: Estado del envío (pending/sent/failed)
- `created_at`: Fecha de creación
- `sent_at`: Fecha de envío exitoso
- `error_message`: Mensaje de error si falla

**Admin Features**:
- List display con badges de color por status
- Filtros por status y fecha
- Búsqueda por nombre/email/mensaje
- Readonly timestamps

---

### Project (projects/models.py)

```python
class Project(models.Model):
    # Basic info
    name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=[
            ('active', 'Active'),
            ('completed', 'Completed'),
            ('on_hold', 'On Hold'),
            ('planning', 'Planning'),
        ]
    )
    description = models.TextField()
    progress = models.IntegerField(default=0)  # 0-100
    due_date = models.CharField(max_length=50)

    # Team
    team_size = models.IntegerField(default=1)
    digitalpath_responsible = models.CharField(max_length=100)
    client_responsible = models.CharField(max_length=100)
    client_company = models.CharField(max_length=255)

    # Tasks
    tasks_total = models.IntegerField(default=0)
    tasks_completed = models.IntegerField(default=0)

    # Details
    budget = models.CharField(max_length=50)
    implementation_time = models.CharField(max_length=50)
    last_update = models.CharField(max_length=50)
    full_scope = models.TextField()

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Relaciones**:
- `data_sources`: One-to-Many → DataSource
- `reports`: One-to-Many → Report
- `analytics`: One-to-Many → Analytic
- `ai_integration`: One-to-One → AIIntegration

---

### DataSource, Report, Analytic

Modelos relacionados al proyecto:

```python
class DataSource(models.Model):
    project = models.ForeignKey(Project, related_name='data_sources')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    description = models.TextField()
    order = models.IntegerField(default=0)

class Report(models.Model):
    project = models.ForeignKey(Project, related_name='reports')
    name = models.CharField(max_length=255)
    frequency = models.CharField(max_length=100)
    description = models.TextField()
    order = models.IntegerField(default=0)

class Analytic(models.Model):
    project = models.ForeignKey(Project, related_name='analytics')
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    description = models.TextField()
    order = models.IntegerField(default=0)
```

---

### AIIntegration

```python
class AIIntegration(models.Model):
    project = models.OneToOneField(Project, related_name='ai_integration')
    enabled = models.BooleanField(default=False)
    features = models.JSONField(default=list)  # Lista de features
    models = models.JSONField(default=list)    # Lista de modelos ML
```

---

### Waitlist (waitlists/models.py)

```python
class Waitlist(models.Model):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    company = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    notified = models.BooleanField(default=False)
```

---

## API Endpoints

### Autenticación

#### Signup
```http
POST /api/auth/signup
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "first_name": "John",
  "last_name": "Doe"
}

Response 200:
{
  "success": true,
  "message": "User created successfully. Please check your email...",
  "user": {
    "username": "johndoe",
    "email": "john@example.com",
    "is_authenticated": false
  }
}
```

#### Verify Email
```http
POST /api/auth/verify-email
Content-Type: application/json

{
  "key": "verification-key-from-email"
}

Response 200:
{
  "success": true,
  "message": "Email verified successfully. You can now log in."
}
```

#### Login (JWT)
```http
POST /api/token/pair
Content-Type: application/json

{
  "username": "johndoe",  # or email
  "password": "SecurePass123!"
}

Response 200:
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "username": "johndoe"
}
```

#### Refresh Token
```http
POST /api/token/refresh
Content-Type: application/json

{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}

Response 200:
{
  "access": "new-access-token..."
}
```

#### Forgot Password
```http
POST /api/auth/forgot-password
Content-Type: application/json

{
  "email": "john@example.com"
}

Response 200:
{
  "success": true,
  "message": "If an account exists with this email, you will receive..."
}
```

#### Reset Password
```http
POST /api/auth/reset-password
Content-Type: application/json

{
  "uid": "encoded-user-id",
  "token": "reset-token",
  "new_password": "NewSecurePass123!"
}

Response 200:
{
  "success": true,
  "message": "Password has been reset successfully."
}
```

---

### Contact Form

```http
POST /api/contact
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "message": "I'm interested in your services..."
}

Response 200:
{
  "success": true,
  "message": "Thank you for your message! We'll get back to you within 24 hours."
}

Response 400/500:
{
  "success": false,
  "message": "Error sending message: ..."
}
```

**Proceso interno**:
1. Crear `ContactMessage` en BD (status=pending)
2. Dispatch Celery task
3. Worker envía email asíncrono
4. Actualiza status a sent/failed

---

### Projects

#### List Projects
```http
GET /api/projects/
Authorization: Bearer {access_token}

Response 200:
[
  {
    "id": 1,
    "name": "Health Fund Analytics Platform",
    "status": "active",
    "progress": 75,
    "client_company": "Health Fund Australia",
    "created_at": "2025-01-15T10:30:00Z"
  },
  ...
]
```

#### Get Project Detail
```http
GET /api/projects/{id}/
Authorization: Bearer {access_token}

Response 200:
{
  "id": 1,
  "name": "Health Fund Analytics Platform",
  "status": "active",
  "description": "...",
  "progress": 75,
  "data_sources": [...],
  "reports": [...],
  "analytics": [...],
  "ai_integration": {...}
}
```

#### Create Project
```http
POST /api/projects/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "name": "New Project",
  "status": "planning",
  "description": "...",
  "client_company": "..."
}

Response 201:
{
  "id": 2,
  "name": "New Project",
  ...
}
```

#### Update Project
```http
PUT /api/projects/{id}/
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "progress": 80,
  "status": "active"
}

Response 200:
{
  "id": 1,
  "progress": 80,
  "status": "active",
  ...
}
```

#### Delete Project
```http
DELETE /api/projects/{id}/
Authorization: Bearer {access_token}

Response 204 No Content
```

#### Projects Summary
```http
GET /api/projects/summary/
Authorization: Bearer {access_token}

Response 200:
{
  "total": 10,
  "active": 6,
  "completed": 2,
  "on_hold": 1,
  "planning": 1,
  "average_progress": 68
}
```

---

### User Info

```http
GET /api/me
Authorization: Bearer {access_token}

Response 200:
{
  "username": "johndoe",
  "is_authenticated": true,
  "email": "john@example.com",
  "first_name": "John",
  "last_name": "Doe"
}
```

---

### Waitlists

Endpoints manejados por router de Django Ninja en `/api/waitlists/`.

---

## Sistema de Autenticación

### JWT Authentication

**Flow**:
```
1. Usuario → POST /api/token/pair (username/email + password)
2. Django valida credenciales
3. Django retorna access_token + refresh_token
4. Cliente guarda tokens
5. Cliente usa access_token en header: Authorization: Bearer {token}
6. Cuando access_token expira → POST /api/token/refresh
7. Django retorna nuevo access_token
```

**Token Lifetimes** (DEBUG mode):
- Access Token: 60 minutos
- Refresh Token: 7 días

**Headers**:
```http
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

---

### Social Authentication (OAuth)

**Providers**:
- Google OAuth 2.0
- GitHub OAuth

**Flow**:
```
1. Frontend → Redirect to Google/GitHub
2. User authorizes app
3. Provider → Redirect back with code
4. Django Allauth exchanges code for tokens
5. Django creates/updates user
6. Django returns JWT tokens
```

**Configuration**:
- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET`
- `GITHUB_CLIENT_ID` / `GITHUB_CLIENT_SECRET`

**Adapter**: Custom `socialaccount_adapter.py` para integración headless con JWT.

---

### Email Verification

**Flow**:
```
1. User signup → POST /api/auth/signup
2. Django creates user (is_active=False)
3. Django sends verification email
4. Email contains link: {FRONTEND_URL}/verify-email?key={key}
5. Frontend → POST /api/auth/verify-email {key}
6. Django verifies and activates user
```

**Email Template**:
- Subject: "DigitalPath AI - Please Confirm Your Email Address"
- From: `DEFAULT_FROM_EMAIL`
- Contains verification link to Next.js frontend

---

## Sistema de Emails (Celery)

### Arquitectura

```
┌──────────────┐      ┌─────────────┐      ┌──────────────┐
│   Django     │─────▶│   Redis     │◀─────│   Celery     │
│   API        │      │   (Broker)  │      │   Worker     │
└──────────────┘      └─────────────┘      └──────┬───────┘
                                                   │
                                                   ▼
                                            ┌──────────────┐
                                            │  SMTP Server │
                                            │  (Gmail)     │
                                            └──────────────┘
```

### Celery Configuration

**Archivo**: `src/core/celery.py`

```python
from celery import Celery

app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
```

**Settings** (`settings.py`):
```python
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
```

---

### Email Task

**Archivo**: `src/contact/tasks.py`

```python
@shared_task(bind=True, max_retries=3)
def send_contact_email_task(self, contact_message_id):
    try:
        # Get message from DB
        contact_message = ContactMessage.objects.get(id=contact_message_id)

        # Build email
        subject = f"New Contact Form Submission from {contact_message.name}"
        message = f"From: {contact_message.name} <{contact_message.email}>..."

        # Send email
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL,
                  [settings.EMAIL_HOST_USER])

        # Update status
        contact_message.status = 'sent'
        contact_message.sent_at = timezone.now()
        contact_message.save()

    except Exception as e:
        # Mark as failed
        contact_message.status = 'failed'
        contact_message.error_message = str(e)
        contact_message.save()

        # Retry after 60 seconds
        raise self.retry(exc=e, countdown=60)
```

**Features**:
- Máximo 3 reintentos
- Countdown de 60 segundos entre reintentos
- Tracking de estado en BD
- Logging de errores

---

### Email Configuration

**SMTP Settings**:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'your-email@gmail.com'
EMAIL_HOST_PASSWORD = 'your-app-password'  # App password, not regular password
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = 'noreply@digitalpathai.com'
```

**Gmail Setup**:
1. Enable 2FA en cuenta Gmail
2. Generar App Password: https://myaccount.google.com/apppasswords
3. Usar App Password en `EMAIL_HOST_PASSWORD`

---

### Fallback Mechanism

**Código** (`core/api.py`):
```python
try:
    # Try async
    send_contact_email_task.delay(contact_message.id)
except Exception as celery_error:
    # Fallback to sync
    logger.warning(f"Celery not available, sending email synchronously")
    send_contact_email_task(contact_message.id)
```

Si Celery no está disponible, el email se envía de forma síncrona.

---

### Testing Celery

**Script**: `src/test_celery.py`

```bash
cd src
python test_celery.py
```

Output:
```
============================================================
CELERY DIAGNOSTICS
============================================================

1. Celery Configuration:
   Broker URL: redis://localhost:6379/0
   Result Backend: redis://localhost:6379/0
   Task Serializer: json

2. Registered Tasks:
   Total registered tasks: 10
   Contact tasks: ['contact.tasks.send_contact_email_task']

3. Testing Task Dispatch:
   Using message ID: 1
   Status before: pending
   Task ID: 62589529-c064-472c-8282-08d2fa459436
   Task dispatched successfully!
   Waiting 5 seconds for worker to process...
   Status after: sent
   ✅ SUCCESS! Worker processed the task!
```

---

### Running Celery Worker

**Command**:
```bash
cd src
celery -A core worker -l info
```

**Output**:
```
 -------------- celery@hostname v5.5.3
--- ***** -----
-- ******* ---- Linux-6.14.0-35-generic-x86_64
- *** --- * ---
- ** ---------- [config]
- ** ---------- .> app:         core:0x73e4b64b5820
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     redis://localhost:6379/0
- *** --- * --- .> concurrency: 20 (prefork)
-- ******* ---- .> task events: OFF
--- ***** -----
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery

[tasks]
  . contact.tasks.send_contact_email_task

[INFO/MainProcess] Connected to redis://localhost:6379/0
[INFO/MainProcess] celery@hostname ready.
```

---

## Variables de Entorno

### Archivo: `.env`

```bash
# ============================================
# DJANGO CORE
# ============================================
DJANGO_SECRET_KEY=your-super-secret-key-here
DJANGO_DEBUG=1  # 0 for production
DATABASE_URL=postgresql://user:pass@host:port/dbname

# ============================================
# ALLOWED HOSTS & CORS
# ============================================
ENV_ALLOWED_HOSTS=digitalpathai.com,www.digitalpathai.com
CORS_ALLOWED_ORIGINS=https://digitalpathai.com,http://localhost:3000,http://127.0.0.1:3000

# ============================================
# FRONTEND
# ============================================
FRONTEND_URL=http://localhost:3000

# ============================================
# EMAIL (SMTP)
# ============================================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=digitalpathai.sydney@gmail.com
EMAIL_HOST_PASSWORD=your-gmail-app-password
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
DEFAULT_FROM_EMAIL=digitalpathai.sydney@gmail.com

# ============================================
# CELERY (REDIS)
# ============================================
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# ============================================
# OAUTH - GOOGLE
# ============================================
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret

# ============================================
# OAUTH - GITHUB
# ============================================
GITHUB_CLIENT_ID=your-github-client-id
GITHUB_CLIENT_SECRET=your-github-client-secret
```

### Variables Requeridas

**Mínimo para desarrollo**:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG`
- `EMAIL_HOST_USER`
- `EMAIL_HOST_PASSWORD`
- `FRONTEND_URL`

**Para producción adicional**:
- `DATABASE_URL` (PostgreSQL)
- `CELERY_BROKER_URL` (Redis)
- `CORS_ALLOWED_ORIGINS`
- OAuth credentials (si se usa social auth)

---

## Deployment

### Railway Deployment

**1. Preparación**:
```bash
# Asegurar que requirements.txt está actualizado
pip freeze > requirements.txt

# Commit changes
git add .
git commit -m "Prepare for deployment"
git push
```

**2. Railway Setup**:
1. Crear nuevo proyecto en Railway
2. Connect GitHub repository
3. Add PostgreSQL service (Neon)
4. Add Redis service

**3. Environment Variables** (Railway):
```
DJANGO_SECRET_KEY=...
DJANGO_DEBUG=0
DATABASE_URL=${{Postgres.DATABASE_URL}}
CELERY_BROKER_URL=${{Redis.REDIS_URL}}
CELERY_RESULT_BACKEND=${{Redis.REDIS_URL}}
FRONTEND_URL=https://yourdomain.com
CORS_ALLOWED_ORIGINS=https://yourdomain.com
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

**4. Deploy Commands**:

Railway auto-detecta Django. Si necesitas custom:

**`railway.json`**:
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "python src/manage.py migrate && gunicorn --chdir src core.wsgi:application",
    "restartPolicyType": "ON_FAILURE"
  }
}
```

**5. Celery Worker** (separate service):

Crear segundo servicio en Railway:
- Same repo
- Start command: `celery -A core worker -l info`
- Working directory: `src/`

**6. Static Files**:
```bash
# Collect static files
python manage.py collectstatic --noinput
```

**7. Migrations**:
```bash
# Run migrations
python manage.py migrate
```

---

### Docker Deployment (Alternativa)

**Dockerfile**:
```dockerfile
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/src

CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]
```

**docker-compose.yml**:
```yaml
version: '3.8'

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: digitalpathai
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  web:
    build: .
    command: gunicorn core.wsgi:application --bind 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    env_file:
      - .env

  celery:
    build: .
    command: celery -A core worker -l info
    volumes:
      - .:/app
    depends_on:
      - db
      - redis
    env_file:
      - .env

volumes:
  postgres_data:
```

**Run**:
```bash
docker-compose up --build
```

---

## Troubleshooting

### Problema: Emails no se envían

**Síntomas**:
- Mensajes quedan en status `pending`
- No hay errores en logs

**Diagnóstico**:
```bash
cd src
python test_celery.py
```

**Soluciones**:

1. **Celery worker no corriendo**:
```bash
celery -A core worker -l info
```

2. **Redis no corriendo**:
```bash
# Ubuntu
sudo systemctl start redis

# macOS
brew services start redis

# Verificar
redis-cli ping  # Should return PONG
```

3. **Worker iniciado antes de configuración**:
- Detener worker (Ctrl+C)
- Reiniciar: `celery -A core worker -l info`

4. **Email config incorrecta**:
```python
# Test direct email
python manage.py shell
>>> from django.core.mail import send_mail
>>> from django.conf import settings
>>> send_mail('Test', 'Message', settings.DEFAULT_FROM_EMAIL, ['recipient@example.com'])
```

---

### Problema: CORS Errors

**Error**: `Access to fetch blocked by CORS policy`

**Solución**:
1. Verificar `CORS_ALLOWED_ORIGINS` en `.env`
2. Asegurar que incluye frontend URL
3. Verificar que frontend usa URL correcta:
```javascript
const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api";
```

---

### Problema: JWT Token Invalid

**Error**: `401 Unauthorized`

**Soluciones**:
1. Token expirado → Refresh token
2. Token malformado → Re-login
3. Header incorrecto:
```http
Authorization: Bearer {token}  ✓
Authorization: {token}          ✗
```

---

### Problema: Database Connection Failed

**Error**: `OperationalError: could not connect to server`

**Soluciones**:
1. Verificar `DATABASE_URL` en `.env`
2. PostgreSQL corriendo:
```bash
sudo systemctl status postgresql
```
3. Credentials correctos
4. Firewall/network permite conexión

---

### Problema: Migrations Conflict

**Error**: `Conflicting migrations detected`

**Solución**:
```bash
# Ver migrations
python manage.py showmigrations

# Crear merge migration
python manage.py makemigrations --merge

# Aplicar
python manage.py migrate
```

---

### Problema: Social Auth Not Working

**Síntomas**:
- Redirect loop
- "Invalid credentials" después de OAuth

**Soluciones**:
1. Verificar OAuth credentials en `.env`
2. Configurar redirect URIs en Google/GitHub console:
```
http://localhost:8000/accounts/google/login/callback/
http://localhost:8000/accounts/github/login/callback/
```
3. Verificar `SITE_ID` en settings
4. Crear Social Application en Django admin:
```
/admin/socialaccount/socialapp/add/
```

---

### Logs y Debugging

**Django Logs**:
```bash
# Development
python manage.py runserver --verbosity 2

# Ver queries SQL
settings.py:
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

**Celery Logs**:
```bash
# Verbose logging
celery -A core worker -l debug

# Log to file
celery -A core worker -l info --logfile=celery.log
```

**Redis Logs**:
```bash
# Monitor commands
redis-cli monitor

# Check queue length
redis-cli LLEN celery
```

---

## Checklist de Deployment

### Pre-deployment

- [ ] `DEBUG=False` en producción
- [ ] `SECRET_KEY` único y seguro
- [ ] `ALLOWED_HOSTS` configurado
- [ ] `CORS_ALLOWED_ORIGINS` correcto
- [ ] Database backups configurados
- [ ] Email credentials válidos
- [ ] OAuth credentials de producción
- [ ] SSL/HTTPS habilitado

### Post-deployment

- [ ] Migrations aplicadas
- [ ] Static files collected
- [ ] Superuser creado
- [ ] Celery worker corriendo
- [ ] Redis corriendo
- [ ] Test email enviado
- [ ] Test API endpoints
- [ ] Test authentication flow
- [ ] Monitor logs por errores
- [ ] Setup monitoring (Sentry, etc.)

---

## Contacto y Soporte

Para soporte técnico:
- Revisar logs de Django/Celery/Redis
- Usar `test_celery.py` para diagnóstico
- Consultar esta documentación
- Verificar variables de entorno

---

**Fin de Resumen Master**
**Versión:** 1.0
**Última actualización:** 2025-11-16
