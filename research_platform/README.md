## Research Platform (Django)

A full‑stack research collaboration platform built with Django. It provides user accounts, paper management (upload, categorize, rate, bookmark), collaborative groups, real‑time chat via WebSockets, REST APIs with JWT, search, and ML‑powered recommendations/summaries.

### Features
- **Accounts**: Register, login/logout, profile, dashboard, admin dashboard. Custom user model `accounts.User`.
- **Papers**: Upload/download PDFs, edit/delete, categories, bookmarks, ratings, admin approval workflow, per‑paper summaries, recommendations.
- **Groups**: Create/join/leave groups, manage members/roles, attach papers, view group details.
- **Chat**: Per‑paper and group chat rooms, real‑time messaging via Channels (websockets) at `ws/chat/<room_id>/`.
- **Search**: Basic and advanced search, suggestions, history.
- **API**: JWT‑secured REST API for auth, papers, search, bookmarks/ratings, recommendations.
- **ML**: Text processing and recommendation engine; optional local transformers cache and model assets under `ml_models/`.
- **Task Queue (optional)**: Celery/Redis wiring present for background tasks.

### Tech Stack
- Django, Django REST Framework, Django Channels
- JWT auth (`djangorestframework-simplejwt`)
- Celery + Redis (optional)
- Search: `elasticsearch-dsl` (code scaffolded)
- ML/NLP: `transformers`, `torch`, `scikit-learn`, `pandas`, etc.

### Project Layout
```
research_platform/
  manage.py
  requirements.txt
  research_platform/        # Project config (settings, urls, asgi, wsgi)
  apps/
    accounts/               # Auth, profiles, dashboards
    papers/                 # Paper CRUD, categories, bookmarks, ratings, summaries
    groups/                 # Groups and membership management
    chat/                   # Real-time chat (Channels)
    search/                 # Search views/APIs
    ml_engine/              # ML utils, chatbot, recommendation engine
    api/                    # REST API routing layer
  templates/                # HTML templates
  media/                    # Uploaded files (avatars, PDFs)
  ml_models/                # Deployed model scripts/assets
```

### Quick Start
1) Create and activate a virtualenv, then install deps:
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

2) Environment configuration:
- Defaults are development‑friendly (SQLite, DEBUG=True, open CORS for localhost).
- Set `DJANGO_SETTINGS_MODULE=research_platform.settings` (already used by manage scripts).
- For production, set a secure `SECRET_KEY`, tighten `ALLOWED_HOSTS`, configure databases/redis/channels.

3) Database setup:
```bash
python manage.py migrate
python manage.py createsuperuser
```

4) Run the dev server:
```bash
python manage.py runserver
```
Visit: http://127.0.0.1:8000/

5) Static/media:
- Media is served in DEBUG via `MEDIA_URL=/media/`.
- Static is served in DEBUG via `STATIC_URL=/static/`.

### Optional Services
- **Redis** (recommended for Channels/Celery in production): `redis://localhost:6379`
- **Celery** worker example:
```bash
celery -A research_platform worker -l info
```
- **Channels**: Dev uses in‑memory layer; for production configure `channels_redis` in `CHANNEL_LAYERS`.

### URLs (Server‑rendered)
- Home: `/`
- Admin: `/admin/`
- Accounts: `/accounts/`
  - `login/`, `register/`, `logout/`, `profile/`, `profile/edit/`, `dashboard/`, `admin-dashboard/`
- Papers: `/papers/`
  - ``, `upload/`, `<pk>/`, `<pk>/edit/`, `<pk>/delete/`, `<pk>/bookmark/`, `<pk>/rate/`, `<pk>/download/`
  - `bookmarks/`, `my-papers/`, `categories/`, `categories/<pk>/`, `pending-approval/`
  - `<pk>/approve/`, `<pk>/reject/`, `recommendations/`, `<pk>/summary/`, `admin-manage/`
- Groups: `/groups/`
  - ``, `create/`, `<pk>/`, `<pk>/edit/`, `<pk>/join/`, `<pk>/leave/`, `<pk>/add-paper/`
  - `my-groups/`, `<pk>/members/`, `<pk>/invite/`, `<pk>/remove/<user_id>/`, `<pk>/update-role/<user_id>/`
- Chat: `/chat/`
  - `paper/<paper_id>/`, `group/<group_id>/`, `room/<room_id>/`, `ajax/send/<room_id>/`, `my-chats/`, `500/`
- Search: `/search/`
  - ``, `advanced/`, `suggestions/`, `history/`

### WebSocket
- Pattern: `ws/chat/<room_id>/`
- ASGI via `research_platform.asgi.application` with `AuthMiddlewareStack`.

### REST API (prefix `/api/`)
- Auth:
  - `auth/register/` (POST)
  - `auth/login/` (POST)
  - `auth/profile/` (GET)
  - `auth/token/` (POST, obtain JWT)
  - `auth/token/refresh/` (POST)
- Papers:
  - `papers/` (GET, POST)
  - `papers/<pk>/` (GET, PUT/PATCH, DELETE)
  - `papers/<pk>/approve/` (POST)
- Bookmarks & Ratings:
  - `bookmarks/` (GET, POST)
  - `ratings/` (GET, POST)
- Search:
  - `search/` (GET)
  - `search/suggestions/` (GET)
- Recommendations:
  - `recommendations/` (GET)

All API endpoints default to `IsAuthenticated`. Use JWT Authorization: `Authorization: Bearer <token>`.

### Settings Highlights
- `AUTH_USER_MODEL = 'accounts.User'`
- `REST_FRAMEWORK` with JWT + Session auth, pagination, filters
- `CHANNEL_LAYERS`: in‑memory by default
- Media/Static roots under project base
- Logs to `logs/django.log` (directory auto‑created)

### Development Notes
- SQLite default; MySQL config scaffold is included (commented) in `settings.py`.
- For production, switch Channels to Redis, configure Celery broker/result backend to Redis, and secure all secrets.
- ML models live under `ml_models/` with additional assets in `apps/ml_engine/ml_models/`.

### Scripts and Management Commands
- Example commands under `apps/*/management/commands/` to seed users/papers.

### License
Proprietary or TBD by repository owner.


