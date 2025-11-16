# DigitalPath AI - Django Backend

Backend API para DigitalPath AI construido con Django, Django Ninja, Celery y PostgreSQL.

## 🚀 Quick Start

### 1. Setup Environment

```bash
# Create and activate virtual environment
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.sample .env
# Edit .env with your configuration
```

### 2. Run Migrations

```bash
cd src
python manage.py migrate
python manage.py createsuperuser
```

### 3. Start Services

**Terminal 1 - Django Server:**
```bash
cd src
python manage.py runserver
```

**Terminal 2 - Celery Worker (for emails):**
```bash
cd src
celery -A core worker -l info
```

**Terminal 3 - Redis (required for Celery):**
```bash
# Ubuntu/Debian
sudo systemctl start redis

# macOS
brew services start redis
```

## 📚 Documentation

Ver **resumen-master.md** para documentación completa del proyecto.

## 🔑 Key Features

- **Authentication**: JWT + Social Auth (Google, GitHub)
- **Contact Form**: Async email sending via Celery
- **Projects Management**: Full CRUD for client projects
- **Waitlists**: User waitlist management
- **Admin Panel**: Django admin at `/admin/`
- **API Docs**: Auto-generated at `/api/docs`

## 🛠️ Tech Stack

- Django 5.0
- Django Ninja (Fast API)
- Celery + Redis (Async tasks)
- PostgreSQL (Production)
- JWT Authentication
- Django Allauth (Social Auth)

## 🌐 API Endpoints

### Authentication
- `POST /api/auth/signup` - User registration
- `POST /api/auth/verify-email` - Email verification
- `POST /api/token/pair` - Login (JWT)
- `POST /api/token/refresh` - Refresh token

### Contact
- `POST /api/contact` - Submit contact form

### Projects
- `GET /api/projects/` - List all projects
- `GET /api/projects/{id}/` - Project detail
- `POST /api/projects/` - Create project

### Waitlists
- `/api/waitlists/` - Waitlist management

## 🧪 Testing

```bash
# Test Celery worker
cd src
python test_celery.py
```

## 📝 Environment Variables

Required in `.env`:

```bash
# Django
DJANGO_SECRET_KEY=your-secret-key
DJANGO_DEBUG=1
DATABASE_URL=postgresql://...

# Email
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Celery
CELERY_BROKER_URL=redis://localhost:6379/0

# Frontend
FRONTEND_URL=http://localhost:3000
CORS_ALLOWED_ORIGINS=http://localhost:3000

# OAuth (optional)
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

## 🏗️ Project Structure

```
django/
├── src/
│   ├── contact/          # Contact form + Celery emails
│   ├── core/             # Settings, API, URLs
│   ├── helpers/          # Auth helpers
│   ├── projects/         # Project management
│   ├── waitlists/        # Waitlist app
│   └── manage.py
├── env/                  # Virtual environment
├── .env                  # Environment variables
└── requirements.txt      # Python dependencies
```

## 🔗 Links

- API Documentation: http://localhost:8000/api/docs
- Admin Panel: http://localhost:8000/admin/
- Frontend: http://localhost:3000

## 📞 Support

Para detalles técnicos completos, consulta **resumen-master.md**.
