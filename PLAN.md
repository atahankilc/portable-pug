# Configurable Full-Stack Application — Architecture Plan

## Overview

A monorepo architecture for building a **highly configurable application** that runs across multiple platforms and deployment modes from a single codebase.

**Core principle:** Write once, deploy anywhere — the same code serves mobile users, web users, and desktop users. The backend runs either in the cloud or packaged locally inside a desktop app. An ML/AI pipeline is included and can run locally or be offloaded to the cloud.

**Tech stack:**
- **Frontend:** Expo (React Native) — single codebase for iOS, Android, and Web
- **Backend:** Django + Django REST Framework + Celery
- **ML/AI:** Python pipeline (PyTorch/ONNX) integrated as a Django app
- **Database:** PostgreSQL (cloud) / SQLite (local)
- **Desktop:** Electron wrapping Expo web build + Django as a sidecar process
- **Infrastructure:** Docker Compose for cloud, PyInstaller for desktop bundling

---

## Target Monorepo Structure

```
conf-master/
├── frontend/                       # Single Expo codebase (mobile + web)
│   ├── app/                        # Expo Router — file-based routing
│   │   ├── _layout.tsx             # Root layout (providers, auth gate)
│   │   ├── index.tsx               # Entry redirect
│   │   ├── (auth)/                 # Auth group (login, register, etc.)
│   │   │   ├── _layout.tsx
│   │   │   ├── login.tsx
│   │   │   └── register.tsx
│   │   └── (tabs)/                 # Main app group (bottom tab bar)
│   │       ├── _layout.tsx
│   │       ├── home.tsx
│   │       ├── upload.tsx
│   │       └── results.tsx
│   ├── src/
│   │   ├── components/             # Shared UI components
│   │   ├── api/client.ts           # Unified API client (platform-aware)
│   │   ├── config/
│   │   │   └── environment.ts      # Runtime mode detection
│   │   ├── context/                # React contexts (auth, theme, etc.)
│   │   ├── hooks/
│   │   ├── theme/
│   │   ├── translations/           # i18n (i18next)
│   │   └── utils/
│   ├── app.config.js               # Expo config (API_URL, DEPLOYMENT_MODE)
│   └── package.json
│
├── backend/
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── pyinstaller.spec            # Desktop sidecar packaging
│   ├── run_server.py               # PyInstaller entry point
│   ├── core_api/                   # Django project
│   │   ├── settings/
│   │   │   ├── base.py             # Shared config
│   │   │   ├── cloud.py            # PostgreSQL + Redis + production
│   │   │   ├── local.py            # SQLite + synchronous tasks + debug
│   │   │   └── hybrid.py           # SQLite locally + cloud ML
│   │   ├── celery.py               # Celery app config
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── users/                      # User management app
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   └── ml/                         # ML/AI pipeline app
│       ├── models.py               # Job tracking model
│       ├── views.py                # DRF views (authenticated)
│       ├── serializers.py
│       ├── urls.py
│       ├── tasks.py                # Celery tasks (async or sync via config)
│       ├── pipeline/
│       │   ├── inference.py        # Model inference logic
│       │   └── features.py         # Input preprocessing
│       ├── model_registry/         # Model architecture definitions
│       ├── storage/
│       │   ├── local.py            # Local filesystem storage
│       │   └── cloud.py            # Cloud storage (S3/GCS)
│       └── weights/                # Trained model files (.pth/.onnx)
│
├── desktop/                        # Electron shell (packaging layer)
│   ├── main.ts                     # Main process — BrowserWindow + sidecar orchestration
│   ├── preload.ts                  # Context bridge (isElectron, deploymentMode)
│   ├── sidecar.ts                  # Django process spawner + health check
│   ├── package.json                # Electron + electron-builder dependencies
│   └── electron-builder.yml        # Packaging config (.dmg, .exe)
│
├── docker-compose.yml              # Cloud deployment
├── scripts/
│   ├── build-desktop-mac.sh        # PyInstaller + Expo export + electron-builder → .dmg
│   ├── build-desktop-win.sh        # Same → .exe
│   └── dev.sh                      # Local development (Django + Expo)
├── .env.example
├── .gitignore
├── Makefile                        # make dev, make cloud, make build-desktop
└── PLAN.md
```

---

## Deployment Modes

The key architectural feature: the same codebase supports 4 deployment modes controlled by environment variables.

| Mode | Frontend | Backend | ML/AI | Database | Use Case |
|------|----------|---------|-------|----------|----------|
| **Full Cloud** | Expo web build on Nginx | Docker Django | Celery worker (async) | PostgreSQL | Production SaaS |
| **Desktop + Cloud** | Electron | Remote cloud API | Remote cloud | Remote PostgreSQL | Desktop users, cloud data |
| **Full Local** | Electron | PyInstaller sidecar | Synchronous (in-process) | SQLite | Offline / air-gapped |
| **Hybrid** | Electron | PyInstaller sidecar | Forward to cloud API | SQLite | Local data, cloud compute |

**Configuration switches:**
- `DEPLOYMENT_MODE` — `cloud` | `local` | `hybrid` (read by frontend)
- `DJANGO_SETTINGS_MODULE` — `core_api.settings.cloud` | `local` | `hybrid` (read by backend)
- `CELERY_TASK_ALWAYS_EAGER` — `True` in local mode (runs tasks synchronously, no broker needed)
- `IMAGE_STORAGE_BACKEND` — `local` | `gcs` | `s3`

---

## How Each Layer Adapts

### Frontend (Expo)
```
                    ┌──────────────────────────────────────┐
                    │        Single Expo Codebase           │
                    │    (app/ directory, Expo Router)       │
                    └───────┬──────────┬───────────┬────────┘
                            │          │           │
                      ┌─────▼──┐  ┌────▼────┐  ┌──▼──────────┐
                      │  iOS   │  │ Android │  │     Web      │
                      │  App   │  │  App    │  │ (browser or  │
                      │ Store  │  │  Store  │  │  Electron)   │
                      └────────┘  └─────────┘  └─────────────┘
```
- **Platform-aware token storage:** `localStorage` on web, `AsyncStorage` on mobile
- **Platform-aware API base URL:** Cloud URL or `localhost:8000` (sidecar)
- **Electron detection:** `window.electronAPI?.isElectron` via preload script

### Backend (Django)
```
                    ┌──────────────────────────────────────┐
                    │        Single Django Codebase          │
                    │     (settings split by environment)     │
                    └───────┬──────────┬───────────┬────────┘
                            │          │           │
                      ┌─────▼──┐  ┌────▼────┐  ┌──▼──────────┐
                      │ Cloud  │  │  Local  │  │   Hybrid    │
                      │ PostgreSQL│ │ SQLite │  │   SQLite    │
                      │ Redis  │  │ No broker│ │   + Cloud ML│
                      │ Gunicorn│ │ runserver│ │   runserver  │
                      └────────┘  └─────────┘  └─────────────┘
```
- **Settings split:** `base.py` (shared) → `cloud.py` / `local.py` / `hybrid.py`
- **Celery dual mode:** Async with Redis in cloud, synchronous (`ALWAYS_EAGER`) in local
- **PyInstaller frozen detection:** `sys.frozen` flag adjusts paths for bundled mode

### ML/AI Pipeline
```
                    ┌──────────────────────────────────────┐
                    │     ML Pipeline (Django App)           │
                    │   Same inference code everywhere        │
                    └───────┬──────────┬───────────┬────────┘
                            │          │           │
                      ┌─────▼──┐  ┌────▼────┐  ┌──▼──────────┐
                      │ Cloud  │  │  Local  │  │   Hybrid    │
                      │ Celery │  │ In-proc │  │  Forward to │
                      │ worker │  │ sync    │  │  cloud API  │
                      │ (GPU)  │  │ (CPU)   │  │             │
                      └────────┘  └─────────┘  └─────────────┘
```

### Desktop Packaging (Electron)
```
    ┌─────────────────────────────────────────────────┐
    │  Electron App (.exe / .dmg)                      │
    │  ┌───────────────────────────────────────────┐   │
    │  │  Expo Web Build (static HTML/JS/CSS)       │   │
    │  │  → Loaded in Electron BrowserWindow         │   │
    │  └───────────────────────────────────────────┘   │
    │  ┌───────────────────────────────────────────┐   │
    │  │  Django Backend (PyInstaller executable)    │   │
    │  │  → Spawned as sidecar child process         │   │
    │  │  → Serves API on localhost:8000             │   │
    │  │  → SQLite database in user data directory   │   │
    │  └───────────────────────────────────────────┘   │
    │  ┌───────────────────────────────────────────┐   │
    │  │  ML Weights (.pth/.onnx files)             │   │  ← Optional
    │  │  → Bundled as extraResources                │   │
    │  │  → User can choose: local or cloud ML       │   │
    │  └───────────────────────────────────────────┘   │
    └─────────────────────────────────────────────────┘
```

---

# Implementation Plan

## Phase 0 — Repo Bootstrap

- [ ] Create directory skeleton: `frontend/`, `backend/`, `desktop/`, `scripts/`
- [ ] Create `.gitignore`:
  ```
  node_modules/
  __pycache__/
  *.pyc
  .env
  db.sqlite3
  dist/
  build/
  .expo/
  *.pth
  ```
- [ ] Create `.env.example` with all required variables:
  ```
  DEPLOYMENT_MODE=local
  DJANGO_SETTINGS_MODULE=core_api.settings.local
  DJANGO_SECRET_KEY=change-me
  API_URL=http://localhost:8000/api/
  POSTGRES_DB=appdb
  POSTGRES_USER=admin
  POSTGRES_PASSWORD=change-me
  CELERY_BROKER_URL=redis://localhost:6379/0
  IMAGE_STORAGE_BACKEND=local
  ```
- [ ] Create `Makefile`:
  ```makefile
  dev:          # Start Django + Expo for local development
  cloud:        # docker-compose up --build
  build-desktop: # PyInstaller + Expo export + electron-builder
  test-backend: # Django tests
  test-frontend: # Expo/Jest tests
  ```

---

## Phase 1 — Backend (Django + Celery + ML App)

### 1.1 — Django project + apps
- [ ] `django-admin startproject core_api backend/`
- [ ] `cd backend && python manage.py startapp users`
- [ ] `cd backend && python manage.py startapp ml`

### 1.2 — Settings split

**`backend/core_api/settings/base.py`** — Shared configuration:
- INSTALLED_APPS: `users`, `ml`, `rest_framework`, `corsheaders`, `django_celery_results`
- AUTH_USER_MODEL: `users.CustomUser`
- REST_FRAMEWORK: JWT default authentication
- SIMPLE_JWT: access token 1hr, refresh token 7 days
- ML_WEIGHTS_DIR, IMAGE_STORAGE_BACKEND, IMAGE_STORAGE_ROOT
- CORS, middleware, templates, static files

**`backend/core_api/settings/cloud.py`**:
- [ ] PostgreSQL database config (from env vars)
- [ ] `CELERY_BROKER_URL = redis://redis:6379/0`
- [ ] `CELERY_RESULT_BACKEND = "django-db"`
- [ ] `DEBUG = False`

**`backend/core_api/settings/local.py`**:
- [ ] SQLite database
- [ ] `CELERY_TASK_ALWAYS_EAGER = True` (synchronous, no broker)
- [ ] `CELERY_TASK_EAGER_PROPAGATES = True`
- [ ] `DEBUG = True`, `CORS_ALLOW_ALL_ORIGINS = True`
- [ ] PyInstaller frozen detection:
  ```python
  if getattr(sys, 'frozen', False):
      ML_WEIGHTS_DIR = Path(sys._MEIPASS) / "ml" / "weights"
      DATABASES.default.NAME = Path.home() / ".appname" / "db.sqlite3"
  ```

**`backend/core_api/settings/hybrid.py`**:
- [ ] SQLite database (local data)
- [ ] `ML_INFERENCE_BACKEND = "cloud"` (forward ML requests to cloud)
- [ ] `ML_CLOUD_URL` from env var

### 1.3 — Users app (dummy)
- [ ] `CustomUser` model: email (unique, used for login), full_name, `is_active`
- [ ] `POST /api/register/` — create user (email + password + name)
- [ ] `POST /api/login/` — return JWT access + refresh tokens
- [ ] `GET /api/users/me/` — return authenticated user info (IsAuthenticated)
- [ ] `POST /api/logout/` — blacklist refresh token

### 1.4 — ML app (dummy)
- [ ] `MLJob` model: task_id, task_type, status (pending/running/success/failed), result (JSONField), created_at
- [ ] `POST /api/ml/upload/` — accept image file, save to disk, dispatch Celery task, return task_id
- [ ] `GET /api/ml/status/<task_id>/` — return task status + result
- [ ] `GET /api/results/` — list completed results

**Celery tasks:**
- [ ] `backend/core_api/celery.py` — Celery app configuration
- [ ] `backend/ml/tasks.py`:
  ```python
  @shared_task
  def predict_task(job_id, image_path):
      job = MLJob.objects.get(id=job_id)
      job.status = "running"
      job.save()
      # Dummy: sleep 2 seconds, return random prediction
      result = {"label": random.choice(["cat", "dog", "bird"]), "confidence": 0.95}
      job.status = "success"
      job.result = result
      job.save()
  ```
- [ ] In local mode (`CELERY_TASK_ALWAYS_EAGER=True`), this runs synchronously — no Redis needed
- [ ] In cloud mode, this runs async via Redis broker

### 1.5 — Docker setup
- [ ] `backend/Dockerfile` (python:3.11-slim, gunicorn)
- [ ] `docker-compose.yml`:
  - `backend` — Django + gunicorn on port 8000
  - `celery_worker` — same image, `celery -A core_api worker` command
  - `db` — postgres:15 on port 5432
  - `redis` — redis:7-alpine on port 6379
  - `frontend` — nginx serving Expo web export on port 3000

### 1.6 — requirements.txt
```
Django>=5.2
djangorestframework>=3.14
djangorestframework-simplejwt>=5.3
django-cors-headers>=4.3
celery>=5.3
django-celery-results>=2.5
redis>=5.0
gunicorn>=21.2
psycopg2-binary>=2.9
Pillow>=11.0
```

### Phase 1 Verification
```bash
# Local mode (no Docker, no Redis)
cd backend
DJANGO_SETTINGS_MODULE=core_api.settings.local python manage.py migrate
DJANGO_SETTINGS_MODULE=core_api.settings.local python manage.py runserver

curl -X POST localhost:8000/api/register/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test1234!","full_name":"Test User"}'

curl -X POST localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"Test1234!"}'
# → returns {access, refresh}

curl -H "Authorization: Bearer <token>" localhost:8000/api/users/me/
# → returns user info

curl -H "Authorization: Bearer <token>" \
  -F "image=@photo.jpg" localhost:8000/api/ml/upload/
# → returns {task_id, status: "success"} (synchronous in local mode)

# Cloud mode
docker-compose up --build
# Same curl tests against localhost:8000
```

---

## Phase 2 — Frontend (Expo + Expo Router)

### 2.1 — Create Expo project
- [ ] `npx create-expo-app frontend --template blank-typescript`
- [ ] Install dependencies:
  ```
  expo-router, expo-linking, expo-constants, expo-status-bar,
  axios, @react-native-async-storage/async-storage,
  expo-image-picker, styled-components
  ```
- [ ] Configure `app.config.js`:
  ```javascript
  export default ({ config }) => ({
    ...config,
    scheme: "confmaster",
    extra: {
      API_URL: process.env.API_URL ?? "http://localhost:8000/api/",
      DEPLOYMENT_MODE: process.env.DEPLOYMENT_MODE ?? "local",
    },
  });
  ```

### 2.2 — API client (platform-aware)
- [ ] `src/api/client.ts`:
  ```typescript
  // Token storage: localStorage on web, AsyncStorage on mobile
  // Base URL: from environment config (cloud URL or localhost)
  // JWT interceptor: attach Bearer token to all requests
  // Refresh interceptor: auto-refresh expired tokens
  ```
- [ ] `src/config/environment.ts`:
  ```typescript
  // getDeploymentMode(): reads from Electron preload or Expo config
  // getApiBaseUrl(): cloud URL or localhost based on mode
  // isElectron(): detects Electron runtime
  ```

### 2.3 — Expo Router pages
```
app/
├── _layout.tsx              # Root: ThemeProvider + AuthProvider + <Slot />
├── index.tsx                # Redirect: token? → /(tabs)/home : /(auth)/login
│
├── (auth)/
│   ├── _layout.tsx          # Stack layout, no tab bar
│   ├── login.tsx            # Email + password → POST /api/login/ → store token
│   └── register.tsx         # Email + password + name → POST /api/register/
│
└── (tabs)/
    ├── _layout.tsx          # Bottom tab bar: Home | Upload | Results
    ├── home.tsx             # Welcome + user info (GET /api/users/me/)
    ├── upload.tsx           # Pick image → POST /api/ml/upload/ → show task_id
    └── results.tsx          # GET /api/results/ → list of predictions
```

### 2.4 — Auth context
- [ ] `src/context/AuthContext.tsx`:
  - Provides: `user`, `token`, `isLoading`, `login()`, `logout()`
  - On mount: check stored token, validate with `/api/users/me/`
  - Platform-aware: localStorage (web) vs AsyncStorage (mobile)

### 2.5 — Theme
- [ ] `src/theme/GlobalTheme.ts` — color palette, typography, spacing
- [ ] styled-components `ThemeProvider` wrapping the app in root layout

### Phase 2 Verification
```bash
# Mobile
cd frontend && npx expo start
# Login → Home → Upload → Results on iOS/Android simulator

# Web
npx expo start --web
# Same flow in browser, URL routing works (/login, /home, /upload, /results)

# End-to-end with backend
# Start backend (Phase 1) + frontend → full login → upload → result flow
```

---

## Phase 3 — Electron Shell + Desktop Packaging

### 3.1 — Electron setup
- [ ] `desktop/main.ts`:
  - Create BrowserWindow
  - Load Expo web build from `dist/index.html`
  - Spawn Django sidecar based on deployment mode
- [ ] `desktop/preload.ts`:
  - Expose `isElectron`, `deploymentMode` to renderer via contextBridge
- [ ] `desktop/sidecar.ts`:
  - Spawn PyInstaller Django binary as child process
  - Wait for health check on `localhost:8000`
  - Kill on app close
  - Skip if `DEPLOYMENT_MODE=cloud`

### 3.2 — PyInstaller build
- [ ] `backend/run_server.py` — entry point:
  ```python
  os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_api.settings.local')
  from django.core.management import execute_from_command_line
  execute_from_command_line(['manage.py', 'runserver', '127.0.0.1:8000', '--noreload'])
  ```
- [ ] `backend/pyinstaller.spec`:
  - Entry: `run_server.py`
  - Hidden imports: `users`, `ml`, `celery`, `django_celery_results`
  - Data files: `ml/weights/` (if any model files present)
- [ ] Frozen path detection in `local.py`:
  ```python
  if getattr(sys, 'frozen', False):
      BASE_DIR = Path(sys._MEIPASS)
      # Data directory in user home: ~/.appname/
  ```

### 3.3 — Build scripts
- [ ] `scripts/build-desktop-mac.sh`:
  1. `cd backend && pyinstaller pyinstaller.spec --noconfirm`
  2. `cd frontend && npx expo export --platform web`
  3. Copy Expo web build + sidecar into `desktop/resources/`
  4. `cd desktop && npx electron-builder --mac`
- [ ] `desktop/electron-builder.yml`:
  ```yaml
  appId: com.yourapp.desktop
  productName: YourApp
  mac:
    target: dmg
    extraResources:
      - from: resources/sidecar
        to: sidecar
      - from: resources/web
        to: web
  win:
    target: nsis
    extraResources:
      - from: resources/sidecar
        to: sidecar
      - from: resources/web
        to: web
  ```

### Phase 3 Verification
```bash
# Dev mode
cd desktop && npm start
# Window opens, sidecar starts, login → upload → results works

# Packaged build
scripts/build-desktop-mac.sh
# .dmg created, install and run on clean machine
# Login → Upload → Results with local SQLite
```

---

## Phase 4 — Full Pipeline Verification

All deployment modes tested end-to-end:

| Mode | How to start | Expected behavior |
|------|-------------|-------------------|
| **Full Cloud** | `docker-compose up` + browser | All services in Docker, PostgreSQL, async Celery |
| **Full Local** | Open .dmg/.exe | Electron + sidecar, SQLite, synchronous ML |
| **Desktop + Cloud** | .dmg with `DEPLOYMENT_MODE=cloud` | Electron UI, remote API, no sidecar |
| **Hybrid** | .dmg with `DEPLOYMENT_MODE=hybrid` | Local backend + SQLite, ML forwarded to cloud |
| **Mobile** | `npx expo start` on phone | Connects to cloud or local backend |
| **Web (dev)** | `npx expo start --web` | Browser, connects to local or cloud backend |

Checklist:
- [ ] **Full Cloud**: `docker-compose up` → register → login → upload → results
- [ ] **Full Local**: Electron → sidecar starts → register → login → upload → results (SQLite)
- [ ] **Desktop + Cloud**: Electron `DEPLOYMENT_MODE=cloud` → connects to remote API
- [ ] **Hybrid**: Electron → local backend, ML task forwards to cloud
- [ ] **Mobile**: `npx expo start` → phone connects to backend → full flow
- [ ] **Web**: `npx expo start --web` → browser → full flow

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| ML framework bundle size (PyTorch ~800MB) | Desktop installer too large | CPU-only builds (~200MB), ONNX Runtime (~50MB) as future option |
| Expo native modules on web | Camera, date pickers etc. may not work | `Platform.OS === 'web'` fallback for each module |
| SQLite vs PostgreSQL behavioral differences | Queries work on one, fail on other | Stick to Django ORM, never write raw SQL |
| Sidecar startup time | Slow first launch on desktop | Show loading screen, lazy-load ML models |
| Celery filesystem broker (local mode) | Not reliable for multi-user | Single-user only in local mode; Redis for anything shared |
| PyInstaller compatibility | Some packages break when frozen | Test early, add hidden imports as needed |

---

## Architecture Decision Records

### Why Django + Celery (not a separate FastAPI service for ML)?
- **Single auth system** — one JWT implementation, one permission model
- **Direct ORM access** — ML tasks write results directly to the database, no inter-service HTTP calls
- **Simpler desktop packaging** — one sidecar process instead of two
- **Celery dual mode** — async with Redis in cloud, synchronous (`ALWAYS_EAGER`) in local. Same code, different config.

### Why Expo (not separate React web + React Native)?
- **Single codebase** for iOS, Android, and Web
- **Expo Router** gives file-based routing that works on all platforms
- **Platform.OS** branching handles the few cases where behavior must differ
- **styled-components** works identically on native and web

### Why Electron (not Tauri or native)?
- **Web reuse** — Expo web build loads directly in Electron's Chromium
- **Node.js child_process** — trivial to spawn and manage the Django sidecar
- **electron-builder** — mature packaging for macOS (.dmg) and Windows (.exe)
- **Broad compatibility** — no Rust toolchain required, works on CI easily

### Why Django settings split (not feature flags)?
- **Zero runtime overhead** — the right config is loaded at startup, no branching in hot paths
- **Clear boundaries** — `local.py` guarantees SQLite + sync tasks, `cloud.py` guarantees PostgreSQL + async
- **PyInstaller-friendly** — frozen detection lives in `local.py` only, doesn't pollute cloud config
- **Standard Django pattern** — well-documented, easy for any Django developer to understand
