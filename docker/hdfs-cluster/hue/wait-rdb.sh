#!/bin/sh
# wait-for-postgres.sh

# set -e
  
# host="$1"
# shift
  
# until PGPASSWORD=$POSTGRES_PASSWORD mysql -h "$host" -U "postgres" -c '\q'; do
#   >&2 echo "Postgres is unavailable - sleeping"
#   sleep 1
# done
  
# >&2 echo "Postgres is up - executing command"
# exec "$@"
sleep 5s