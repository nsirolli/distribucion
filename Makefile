ifndef BRANCH
BRANCH = master
endif

NGINX_CONF = ./nginx_conf_de_repo

prebuild:
	cat dockerfiles/dockerfile_header dockerfiles/dockerfile_body > Dockerfile

uba_prebuild:
	cat dockerfiles/dockerfile_header dockerfiles/uba_docker_setting dockerfiles/dockerfile_body > Dockerfile

build:
	docker build --build-arg BRANCH=${BRANCH} -t distribucion .
	docker create -ti --name borrar distribucion bash
	mkdir -p ${NGINX_CONF}
	docker cp borrar:/codigo/distribucion/nginx_conf/nginx.conf ${NGINX_CONF} 
	docker cp borrar:/codigo/distribucion/nginx_conf/ssl ${NGINX_CONF}
	docker rm borrar
	docker-compose build
	docker volume create --name=distribucion_pgdata
	docker-compose up --no-start
	@echo -e "\nsugerencia 1: correr \n\ndocker-compose run --rm web sh tools/create_db"
	@echo -e "\nsugerencia 2: correr \n\ndocker-compose run --rm bash python tools/dump_to_db.py"
	@echo -e "\nsugerencia 3: correr \n\ndocker-compose run -v ${PWD}:/tools --rm bash cp -R /codigo/distribucion/tools/ /tools"

rebuild:
	@echo "Voy a hacer un rebuild en la branch ${BRANCH}"
	docker build --build-arg BRANCH=${BRANCH} -t distribucion . --no-cache
	docker-compose build
	@echo -e "\nsugerencia 1: correr \n\ndocker-compose run --rm web python manage.py migrate"

empezar:
	docker-compose up nginx

terminar:
	docker-compose down

#FIXME el scraping no funciona con la html actual
populate:
	docker-compose run --rm web python tools/current_html_to_db.py 2024 1
	docker-compose run --rm web python tools/current_html_to_db.py 2024 2

#ver FIXME arriba
#demo: build populate
demo: build 
	docker-compose run --rm web python tools/inventar_encuestas.py -a 2019 -c S -d J
	docker-compose run --rm web python tools/inventar_encuestas.py -a 2019 -c S -d A1
	docker-compose run --rm web python tools/inventar_encuestas.py -a 2019 -c S -d A2

FECHA := $(shell date +%F_%T)
backup:
	docker run --rm -v distribucion_pgdata:/source:ro busybox tar -czC /source . > data_backup_$(FECHA).tar.gz

ULTIMO_BACKUP := $(shell ls data_backup*.tar.gz 2> /dev/null | tail -1)
restore:
	@echo Voy a parar el sistema de distribucion
	docker-compose stop
	@echo Voy a sobre-escribir la db con el backup $(ULTIMO_BACKUP)
	docker run --rm -i -v distribucion_pgdata:/target busybox tar -xzC /target < $(ULTIMO_BACKUP)
	@echo Levanto el sistema de nuevo
	docker-compose start

debug:
	docker-compose up -d db
	@echo -e "\n sugerencia 1: una vez en la consola, correr\n\n python manage.py runserver 0.0.0.0:8000"
	@echo -e "\n sugerencia 2: puede ser necesario correr\n\n python manage.py makemigrations\n python manage.py migrate\n"
	docker-compose run --rm -p 8000:8000 bash
