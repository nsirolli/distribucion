## Uno

para levantar el servicio no hay que usar

`
docker-compose up
`
sino
`
docker-compose up nginx
`

## Claves https

Hay que hacer un par de cosas. Una es generarte las claves pública y privada. Se hace con

`
mkcert -install
mkcert localhost
`

Los archivos localhost.pem y localhost-key.pem que crea mkcert corresponden, respectivamente, a fullchain.pem y privkey.pem

Después, fijate en
`
nginx_conf/nginx.conf
`


Ahí hay dos líneas
`
    ssl_certificate /etc/nginx/conf.d/ssl/pems/fullchain.pem;
    ssl_certificate_key /etc/nginx/conf.d/ssl/pems/privkey.pem;
`

Tenés que poner los dos archivos en esos lugares.
Pero hay una indirección más. Esa es la ruta dentro de docker. Si mirás docker-compose.yaml, vas a ver

`
      - ./nginx_conf_de_repo:/etc/nginx/conf.d:ro
`

Eso es que el directorio ./nginx_conf_de_repo de donde corras el docker-compose se ve dentro del docker como /etc/nginx/conf.d
Yo cambio en mi máquina esa línea por

`
      - ./nginx_conf:/etc/nginx/conf.d:ro
`

y dentro de nginx_conf hago un directorio
`
  ssl/pems
`
y ahí pongo los archivos

En el server del dm creo que estos pem se regeneran cada 3 meses, así que hay que ir cambiándolos. Después haceme acordar y te cuento cómo hacerlo.

Al Dockerfile:

`
COPY localhost.pem /etc/nginx/conf.d/ssl/pems/fullchain.pem
RUN chmod 644 /etc/nginx/conf.d/ssl/pems/fullchain.pem
COPY localhost-key.pem /etc/nginx/conf.d/ssl/pems/privkey.pem
RUN chmod 644 /etc/nginx/conf.d/ssl/pems/privkey.pem
RUN update-ca-certificates
`


## Postgres

Una cosa que necesité hacer fue usar la imagen de docker con el postgres de la misma versión que el dm. Para eso, en docker-compose.yaml puse

`
  db:
    image: postgres:11.2
    volumes:
      - distribucion_pgdata:/var/lib/postgresql/data
   .....
`

Algo que vamos a tener que hacer es hacer un update de ese postgres al actual. Pero por ahora esto anda.


## Terminar de levantar:

Con eso, podés tirar el comando que crea la base de datos, que es el que sale como sugerencia cuando hacés un make build

`
docker-compose run --rm web sh tools/create_db
`

Después, bajate el último backup del dm así tenés el mismo estado. Está en el server, web24.dm.uba.ar, en
`
/srv/backups_distribucion/
`
Por ej.
`
/srv/backups_distribucion/data_backup_2024-11-16_00:24:43.tar.gz
`

Ponelo donde está tu código y tirá un
`
make restore
`

Eso toma el archivo y lo carga a tu db local. Y luego de eso, un
`
docker-compose up nginx
`

Y con eso, deberías ver las materias de este cuatri en
`
https://localhost:8443/materias/20242
`

Otra cosa que podés correr, independiente de tener lo anterior andando, pero para probar que está todo bien, es correr los tests.
Con
`
docker-compose run --rm test
`
corrés todos. Y podés correr algunos con cosas como
`
docker-compose run --rm test materias.tests.TestPaginas
`

Si todo eso anda, vemos cómo seguir


## Nuevo Python

Una cosa: si cambiás en dockerfiles/dockerfile_header, en lugar de

`
FROM python:3.7.2-slim-stretch
`
ponés
`
FROM python:3.7.17-bullseye
`

## Debug

Fijate si te ayuda en lugar de levantar nginx, levantar nginx, levantar webtest

`
docker-compose up -d webtest
`

Eso levanta en el puerto 8000 y cuando falla algo te tira todo el traceback
Fijate por ej entrar a

`
http://localhost:8000/materias/
`

para chequear que anda, y después probá hacer lo que estabas haciendo.
También podés ver los logs desde la consola, con

`
docker-compose logs -f webtest
`
(o web, cuando levantás la página usual)

Y para hacer debugging como decís, lo que se puede hacer es

`
docker-compose up -d db
docker-compose run --rm -p 8000:8000 bash
`

eso te deja dentro de un docker corriendo bash. Y ahí podés tirar

`
python manage.py runserver 0.0.0.0:8000
`

Ahora tenés el server levantado y accedés también en http://localhost:8000/
Y en el código podés meter un

`
import pdb; pdb.set_trace()
`

que te deja en un debugger cuando pasa por ahí.
Y si te gusta más debuggear a la ipython, antes del python manage.py mandás

`
pip install ipdb
python manage.py.... (mismo comando)
`

pero ahora en lugar de pdb usás

`
import ipdb; ipdb.set_trace()
`

Bueno, eso pude recomponer de cómo laburaba yo.

Para codear, tocar docker-compose.yml:

`
  web:
    image: distribucion
    volumes:
      - ./encuestas:/codigo/distribucion/encuestas 
      - ./materias:/codigo/distribucion/materias
      - distribucion_pgdata:/var/lib/postgresql/data
      - static_volume:/codigo/distribucion/static
    working_dir: /codigo/distribucion
    command: gunicorn --chdir /codigo/distribucion/distribucion --bind :8000 distribucion.wsgi:application --reload
`

## Logs

Para ver logs en tiempo real:
`
docker-compose logs -f nginx
`
y también
`
docker-compose logs -f web
`

