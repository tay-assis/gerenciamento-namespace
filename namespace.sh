#   namespace create <namespace_id> <cpu> <mem> "<script>"
#   namespace execin <namespace_id> "<comando>"
#   namespace delete <namespace_id>  

BASE_DIR="/containers"

if [ "$#" -lt 1 ]; then
    echo "Uso: $0 <subcomando> [args]"
    exit 1
fi

SUBCOMMAND=$1
shift

case "$SUBCOMMAND" in

    create)
        # args: <namespace_id> <cpu> <mem> "<script>"
        if [ "$#" -lt 3 ]; then
            echo "Uso: $0 create <namespace_id> <cpu> <mem> \"<script>\""
            exit 1
        fi
        NAMESPACE_ID=$1
        CPU=$2
        MEM=$3
        shift 3
        SCRIPT="$@"
        bash create_namespace.sh "$NAMESPACE_ID" "$CPU" "$MEM" "$SCRIPT"
        ;;

    execin)
        # args: <namespace_id> "<comando>"
        if [ "$#" -lt 2 ]; then
            echo "Uso: $0 execin <namespace_id> \"<comando>\""
            exit 1
        fi
        NAMESPACE_ID=$1
        shift
        CMD="$@"
        PID_FILE="$BASE_DIR/$NAMESPACE_ID/pid"

        if [ ! -f "$PID_FILE" ]; then
            echo "Namespace '$NAMESPACE_ID' não encontrado."
            exit 1
        fi

        PID=$(cat "$PID_FILE")

        if [ ! -d "/proc/$PID" ]; then
            echo "Processo do namespace '$NAMESPACE_ID' não está em execução."
            exit 1
        fi

        nsenter --target "$PID" --mount --uts --ipc --net --pid bash -c "$CMD"
        ;;
    
    exec)
        if [ "$#" -lt 1 ]; then
            echo "Uso: $0 exec <namespace_id>"
            exit 1
        fi
        NAMESPACE_ID=$1
        PID_FILE="$BASE_DIR/$NAMESPACE_ID/pid"

        if [ ! -f "$PID_FILE" ]; then
            echo "Namespace '$NAMESPACE_ID' não encontrado."
            exit 1
        fi

        PID=$(cat "$PID_FILE")
        if [ ! -d "/proc/$PID" ]; then
            echo "Namespace '$NAMESPACE_ID' não está em execução."
            exit 1
        fi

        # Shell interativo
        sudo nsenter --target "$PID" --mount --uts --ipc --net --pid bash
        ;;

    delete)
        if [ "$#" -lt 1 ]; then
            echo "Uso: $0 delete <namespace_id>"
            exit 1
        fi
        NAMESPACE_ID=$1
        PID_FILE="$BASE_DIR/$NAMESPACE_ID/pid"

        if [ ! -f "$PID_FILE" ]; then
            echo "Namespace '$NAMESPACE_ID' não encontrado."
            exit 1
        fi

        PID=$(cat "$PID_FILE")
        sudo kill -TERM "$PID" 2>/dev/null
        rm -rf "$BASE_DIR/$NAMESPACE_ID"

        # Remove cgroups
        sudo rmdir "/sys/fs/cgroup/cpu/$NAMESPACE_ID" 2>/dev/null
        sudo rmdir "/sys/fs/cgroup/memory/$NAMESPACE_ID" 2>/dev/null

        echo "Namespace '$NAMESPACE_ID' deletado."
        ;;

    
    list)
    # Lista todos os namespaces e seus status
    echo "Namespaces existentes:"
    for name in "$BASE_DIR"/*; do
        [ -d "$name" ] || continue
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
    ;;


    *)
        echo "Subcomando inválido: $SUBCOMMAND"
        echo "Subcomandos disponíveis: create, execin, delete"
        exit 1
        ;;
esac
