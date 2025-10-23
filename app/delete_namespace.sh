        NAMESPACE_ID=$1
        BASE_DIR="./containers/namespaces/$NAMESPACE_ID"
        PID_FILE="$BASE_DIR/pid"
        
        
        #mata o processo e remove pid 
        PID=$(cat "$PID_FILE")
        sudo kill -TERM "$PID"
        rm -rf "$BASE_DIR"

        # Remove cgroups
        sudo rmdir "/sys/fs/cgroup/$NAMESPACE_ID"
        echo "Namespace '$NAMESPACE_ID' deletado."
