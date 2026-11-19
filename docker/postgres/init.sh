#!/bin/sh
# 首次初始化（空数据目录）时由 postgres 官方 entrypoint 执行，之后不再运行。
# 参数来自容器环境：POSTGRES_APP_USER / POSTGRES_APP_PASSWORD / POSTGRES_APP_DB。
set -eu

POSTGRES_USER="${POSTGRES_USER:-postgres}"
: "${POSTGRES_APP_USER:?POSTGRES_APP_USER 未设置}"
: "${POSTGRES_APP_PASSWORD:?POSTGRES_APP_PASSWORD 未设置}"
: "${POSTGRES_APP_DB:?POSTGRES_APP_DB 未设置}"

# psql 变量：:"x" 按标识符引用、:'x' 按字符串字面量引用，安全处理特殊字符
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname postgres \
	-v app_user="$POSTGRES_APP_USER" \
	-v app_password="$POSTGRES_APP_PASSWORD" \
	-v app_db="$POSTGRES_APP_DB" <<'SQL'
CREATE USER :"app_user" WITH PASSWORD :'app_password';
CREATE DATABASE :"app_db" OWNER :"app_user";
SQL
