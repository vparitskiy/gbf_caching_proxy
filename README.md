# gbf caching proxy

Local caching proxy for Granblue Fantasy assets because their CDN sucks ass  

Usage with docker

1) `cd` into project directory
2) `docker compose up -d`
3) Point your proxy settings to `http://127.0.0.1:8899/proxy-pac-config`

Usage from cmd

1) `cd` into project directory
2) `pip install -r ./requirements.txt`
3) `uvicorn server:app --port=8899`
4) Point your proxy settings to `http://127.0.0.1:8899/proxy-pac-config`
