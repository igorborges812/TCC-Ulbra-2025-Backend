#!/usr/bin/env sh

# Exit script on any error
set -e

export DOMAIN=$1

if [ "$(id -u)" -ne "0" ] ; then
    echo "This script must be executed with root privileges."
    exit 1
fi

if [ -z "$DOMAIN" ]; then
    echo "A domain is needed as an argument to execute this script."
    exit 1
fi

USER_HOME=$(eval echo ~"${SUDO_USER:-$(whoami)}")
DATA_PATH="$USER_HOME/cooktogether/data/certbot"
APP_DIR="$USER_HOME/cooktogether"
DEPLOY_DIR="$APP_DIR/deploy"

echo "Utilizando domain $DOMAIN..."
sleep 5

docker compose -f $DEPLOY_DIR/docker-compose-cert-bootstrap.yml up -d nginx
docker compose -f $DEPLOY_DIR/docker-compose-cert-bootstrap.yml up certbot
docker compose -f $DEPLOY_DIR/docker-compose-cert-bootstrap.yml down

# some configurations for let's encrypt
mkdir -p "$DATA_PATH/conf"
echo "Obtendo arquivos de parâmetros TLS..."
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf > "$DATA_PATH/conf/options-ssl-nginx.conf"
curl -s https://raw.githubusercontent.com/certbot/certbot/master/certbot/certbot/ssl-dhparams.pem > "$DATA_PATH/conf/ssl-dhparams.pem"

echo "true" > "$APP_DIR/data/finished-cert-bootstrap"