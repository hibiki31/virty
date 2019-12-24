buildn:
	docker-compose build --no-cache
build:
	docker-compose build 
restart:
	docker-compose down
	docker-compose up -d
up:
	docker-compose up -d
down:
	docker-compose down
login:
	docker exec -it virty_main_1 bash
remove:
	docker system prune --volumes
log:
	tail -f docker/volume/uwsgi_log/uwsgi.log -n 50