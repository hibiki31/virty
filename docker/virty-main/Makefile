build:
	sudo docker build -t dockerfile/test .
	docker run --name dockerfile_test -d dockerfile/test /sbin/init
	docker ps -a
login:
	docker exec -it dockerfile_test /bin/bash
delete:
	docker stop dockerfile_test
	docker rm dockerfile_test
show:
	docker ps -a

rebuild:
	docker stop dockerfile_test
	docker rm dockerfile_test
	sudo docker build -t dockerfile/test .
	docker run --name dockerfile_test -d dockerfile/test /sbin/init
	docker ps -a