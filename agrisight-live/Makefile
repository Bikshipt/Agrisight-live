.PHONY: dev-start test lint build deploy-staging

dev-start:
	docker-compose -f backend/docker-compose.yml up --build -d
	cd frontend && npm install && npm run dev

test:
	cd backend && pytest
	cd frontend && npm run test

lint:
	cd backend && black . && isort .
	cd frontend && npm run lint

build:
	cd backend && docker build -t agrisight-backend .
	cd frontend && npm run build

deploy-staging:
	./infra/deploy.sh

.PHONY: demo-mode
demo-mode:
	# Run backend and frontend in mock Gemini mode for an end-to-end demo.
	MOCK_GEMINI=true docker-compose -f backend/docker-compose.yml up --build -d
	cd frontend && VITE_API_URL=http://localhost:8000 VITE_WS_URL=ws://localhost:8000/api npm install && npm run dev
