#!/bin/bash

docker run -d \
--name mysql-db \
-p 3306:3306 \
-e MYSQL_ROOT_PASSWORD=zedd-ai \
mysql:latest