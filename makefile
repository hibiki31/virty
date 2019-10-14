install:
	ln -si $(shell pwd)/virty.py /usr/local/bin/virty
	chmod 755 /usr/local/bin/virty

buildn:
	docker-compose build --no-cache
build:
	docker-compose build 
up:
	docker-compose up -d
down:
	docker-compose down
login:
	docker exec -it virty_main_1 bash
remove:
	docker system prune --volumes