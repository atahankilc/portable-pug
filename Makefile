.PHONY: dev cloud build-desktop-mac build-desktop-win test-backend test-frontend

dev:
	./scripts/dev.sh

cloud:
	docker-compose up --build

build-desktop-mac:
	./scripts/build-desktop-mac.sh

build-desktop-win:
	./scripts/build-desktop-win.sh

test-backend:
	cd backend && DJANGO_SETTINGS_MODULE=core_api.settings.local python manage.py test

test-frontend:
	cd frontend && npx jest
