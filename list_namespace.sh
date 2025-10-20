    echo "Namespaces existentes:"
    #$BASE_DIR= "./containers/namespaces/"
    for name in "./containers/namespaces/"/*; do
        [ -d "./containers/namespaces/" ] || continue
        NS_NAME=$(basename "$name")
        PID_FILE="$name/pid"
        OUTPUT_LOG="$name/output.log"

        if [ ! -f "$PID_FILE" ]; then
            continue
        fi

        PID=$(cat "$PID_FILE")

        if [ -d "/proc/$PID" ]; then
            STATUS="Em execução"
        else
            STATUS="Terminado"
            if [ -f "$OUTPUT_LOG" ]; then
                LOG_CONTENT=$(cat "$OUTPUT_LOG" | tr '[:upper:]' '[:lower:]')
                if [[ "$LOG_CONTENT" == *"error"* ]] || [[ "$LOG_CONTENT" == *"exception"* ]]; then
                    STATUS="Erro"
                fi
            fi
        fi

        echo "Namespace: $NS_NAME | PID: $PID | Status: $STATUS"
    done