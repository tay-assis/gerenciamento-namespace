#!/bin/bash
set -e

NAMESPACE_ID=$1
shift
CMD="$@"

BASE_DIR="./containers/namespaces/$NAMESPACE_ID"
PID_FILE="$BASE_DIR/pid"

PID=$(cat "$PID_FILE")

# Verifica se o processo está rodando
if [ ! -d "/proc/$PID" ]; then
    echo "Processo do namespace '$NAMESPACE_ID' não está em execução."
    exit 1
fi

# Executa o comando dentro do namespace
sudo nsenter --target "$PID" --mount --uts --ipc --net --pid /bin/sh -c "$CMD"
