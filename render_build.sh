#!/usr/bin/env bash

# Instala dependências
pip install -r requirements.txt

# Aplica migrações
python manage.py migrate

# Coleta arquivos estáticos (como admin)
python manage.py collectstatic --noinput