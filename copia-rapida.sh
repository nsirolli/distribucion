#!/bin/bash

rm -rf dockerfiles

BRANCH=master
curl --fail --silent --show-error --location https://codeload.github.com/nsirolli/distribucion/tar.gz/${BRANCH} | tar xvz -C . distribucion-${BRANCH}/Makefile distribucion-${BRANCH}/dockerfiles distribucion-${BRANCH}/docker-compose.yaml
mv distribucion-${BRANCH}/* .
rmdir distribucion-${BRANCH}

echo "Esta instalación se hace dentro de la uba?"
select uba in "Si" "No"; do
    case $uba in
        Si ) echo "generando el archivo de docker"; make uba_prebuild; break;;
        No ) echo "generando el archivo de docker"; make prebuild; break;;
    esac
done


cat << EOE

Si contestaste la pregunta anterior mal, podés hacer
$ make prebuild
o
$ make uba_prebuild


En cualquier caso, los pasos que siguen son:

$ make build
o, si querés una branch especial,
$ BRANCH=mi_branch_querida make build

$ docker-compose run --rm web sh tools/create_db

Con una db vacía se puede
$ docker-compose run --rm bash python tools/dump_to_db.py
$ make populate

Luego, editar nginx_conf_de_repo/nginx.conf y cambiar 'mi_host...' por tu dominio.
Y luego, si querés usarlo con HTTPS, entrar a nginx_conf_de_repo/ssl y leer el LEEME.

Si querés usar systemd, instalar los archivos de tools/distribucion.service y tools/distribucion_backup.*
en /lib/systemd/system.
Conviene editarlos y cambiar los paths en los .service

Y finalmente, para arrancar los servicios,
$ make empezar
EOE
