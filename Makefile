up:
	docker compose -f deploy/docker-compose.yml up -d

down:
	docker compose -f deploy/docker-compose.yml down

logs:
	docker compose -f deploy/docker-compose.yml logs -f --tail=200

migrate:
	docker compose -f deploy/docker-compose.yml exec web bash -lc "python manage.py migrate"

schedule:
	docker compose -f deploy/docker-compose.yml exec web bash -lc "python manage.py schedule_sync"