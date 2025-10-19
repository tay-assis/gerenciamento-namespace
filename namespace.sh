#   namespace create <namespace_id> <cpu> <mem> "<script>"
#   namespace execin <namespace_id> "<comando>"
#   namespace delete <namespace_id>  


SUBCOMMAND=$1
shift

case "$SUBCOMMAND" in

    create)
        # args: <namespace_id> <cpu> <mem> "<script>"
        NAMESPACE_ID=$1
        CPU=$2
        MEM=$3
        shift 3
        SCRIPT="$@"
        bash create_namespace.sh "$NAMESPACE_ID" "$CPU" "$MEM" "$SCRIPT"
        ;;

    execin)
        # args: <namespace_id> "<comando>"
        NAMESPACE_ID=$1
        shift
        CMD="$@"
        bash create_namespace.sh "$NAMESPACE_ID" "$CMD"
        ;;
    
    exec)
        # Shell interativo
        sudo nsenter --target "$PID" --mount --uts --ipc --net --pid bash
        ;;

    delete)
        bash delete_namespace.sh "$NAMESPACE_ID"
        ;;

    
    list)
    # Lista todos os namespaces e seus status
        bash list_namespaces.sh
        ;;


    *)
        echo "Subcomando inválido: $SUBCOMMAND"
        echo "Subcomandos disponíveis: create, execin, delete"
        exit 1
        ;;
esac
