        NAMESPACE_ID=$1
        BASE_DIR="/containers/nameespaces/$NAMESPACE_ID"
        PID_FILE="$BASE_DIR/pid"
        
        
        PID=$(cat "$PID_FILE")
        sudo kill -TERM "$PID" 2>/dev/null
        rm -rf "$BASE_DIR/$NAMESPACE_ID"

        # Remove cgroups
        sudo rmdir "/sys/fs/cgroup/cpu/$NAMESPACE_ID" 2>/dev/null
        sudo rmdir "/sys/fs/cgroup/memory/$NAMESPACE_ID" 2>/dev/null

        echo "Namespace '$NAMESPACE_ID' deletado."
        ;;