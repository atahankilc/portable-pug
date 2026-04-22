# Portable Pug

A configurable full-stack application that runs across **desktop, web, and mobile** from a single codebase. Ships a backend, frontend, database, and image-processing / ML pipeline that can run fully in the cloud, fully on-device, or in a hybrid mode.

## Purpose

Deliver the same application — with user accounts, image uploads, and an ML inference pipeline — on whichever surface the user prefers, without rewriting per platform and without forcing a network dependency. The "local" mode lets the whole stack run on the user's machine (Electron + packaged Django sidecar + SQLite), so it works offline or in air-gapped environments.

## What's in the box

- **Frontend** — Expo (React Native) — one codebase for iOS, Android, and Web
- **Backend** — Django + DRF + Celery (JWT auth, REST API)
- **Database** — PostgreSQL in the cloud, SQLite on-device
- **Image processing / ML** — Python pipeline (PyTorch/ONNX) integrated as a Django app; runs in-process locally or via Celery workers in the cloud
- **Desktop** — Electron shell wrapping the Expo web build + Django packaged as a PyInstaller sidecar
- **Infra** — Docker Compose for cloud, PyInstaller + electron-builder for desktop installers

## Deployment modes

| Mode | Frontend | Backend | ML | Database |
|------|----------|---------|----|----------|
| Full Cloud | Expo web on Nginx | Docker Django | Celery worker (async) | PostgreSQL |
| Desktop + Cloud | Electron | Remote API | Remote | Remote PostgreSQL |
| Full Local | Electron | PyInstaller sidecar | In-process (sync) | SQLite |
| Hybrid | Electron | PyInstaller sidecar | Forwarded to cloud | SQLite |

Mode is selected via `DEPLOYMENT_MODE` and `DJANGO_SETTINGS_MODULE` — see `.env.example`.

## Repository layout

```
frontend/          Expo app (iOS, Android, Web)
backend/           Django project (users, ml apps; split settings)
desktop/           Electron shell + sidecar orchestration
nginx/             Web server config for cloud deployment
scripts/           Dev + desktop build scripts
docker-compose.yml Cloud deployment
Makefile           Common tasks
PLAN.md            Full architecture + implementation plan
```

## Getting started

```bash
# Local development (Django + Expo)
make dev

# Full cloud stack
make cloud

# Desktop installer (.dmg / .exe)
make build-desktop
```

See `PLAN.md` for the full architecture, per-phase implementation steps, and verification checklists.
