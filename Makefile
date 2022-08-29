CWD:="$(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))/.."

fix_owner:
	sudo chown -R ${USER}:${USER} ../

bash:
	cd ${CWD}; docker exec -it gbf_caching_proxy-server-1 bash

requirements:
	poetry lock && poetry export -f requirements.txt --output requirements.txt --without-hashes
