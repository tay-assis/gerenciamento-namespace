#!/bin/bash
set -e

echo "🚀 Iniciando e configurando MySQL..."
sudo systemctl enable mysql
sudo systemctl start mysql

DB_NAME="namespace"
DB_USER="user"
DB_PASS="password"

echo "🧩 Criando banco e usuário '$DB_USER'..."
sudo mysql <<EOF
CREATE DATABASE IF NOT EXISTS ${DB_NAME};
CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASS}';
GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';
FLUSH PRIVILEGES;
EOF

echo "✅ Banco '${DB_NAME}' e usuário '${DB_USER}' criados com sucesso!"
echo "   ➜ Usuário: ${DB_USER}"
echo "   ➜ Senha:   ${DB_PASS}"
echo "   ➜ Banco:   ${DB_NAME}"
