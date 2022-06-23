#!/bin/sh
echo "Start Infpyng"


export ENV_HOSTS="${ENV_HOSTS:-''}"
export ENV_NETWORKS="${ENV_NETWORKS:-''}"
export ENV_TAGS="${ENV_TAGS:-''}"
export ENV_CONFIG_log_path="${ENV_CONFIG_log_path:-'stdout'}"
export ENV_CONFIG_log_level="${ENV_CONFIG_log_level:-'ERROR'}"
export ENV_CONFIG_maxBytes="${ENV_CONFIG_maxBytes:="1024000"}"
export ENV_CONFIG_backupCount="${ENV_CONFIG_backupCount:-"1"}"
export ENV_CONFIG_hostname=${ENV_CONFIG_hostname:-'localhost'}
export ENV_CONFIG_port="${ENV_CONFIG_port:-"8086"}"
export ENV_CONFIG_dbname="${ENV_CONFIG_dbname:-'infpyng'}"
export ENV_CONFIG_retention_name="${ENV_CONFIG_retention_name:-'week'}"
export ENV_CONFIG_retention_duration="${ENV_CONFIG_retention_duration:-'1w'}"
export ENV_CONFIG_replication="${ENV_CONFIG_replication:-1}"
export ENV_CONFIG_shard_duration="${ENV_CONFIG_shard_duration:-'1w'}"
export ENV_CONFIG_poll="${ENV_CONFIG_poll:-60}"
export ENV_CONFIG_count="${ENV_CONFIG_count:-1}"
export ENV_CONFIG_interval="${ENV_CONFIG_interval:-10}"
export ENV_CONFIG_period="${ENV_CONFIG_period:-1000}"
export ENV_CONFIG_timeout="${ENV_CONFIG_timeout:-500}"
export ENV_CONFIG_backoff="${ENV_CONFIG_backoff:-1.5}"
export ENV_CONFIG_retry="${ENV_CONFIG_retry:-3}"
export ENV_CONFIG_tos="${ENV_CONFIG_tos:-0}"

echo $ENV_HOSTS
echo $ENV_NETWORKS
echo $ENV_TAGS

#/usr/bin/envsubst < ../config/config.env >../config/config.toml
/usr/bin/envsubst < /infpyng/config/config.env >/infpyng/config/config.toml
/usr/bin/envsubst < /infpyng/config/hosts.env >/infpyng/config/hosts_env.toml
exec /usr/local/bin/python ./infpyng.py

