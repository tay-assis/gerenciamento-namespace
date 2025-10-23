        NAMESPACE_ID=$1
        BASE_DIR="./containers/namespaces/$NAMESPACE_ID"
        PID_FILE="$BASE_DIR/pid"
        
        
        PID=$(cat "$PID_FILE")
        sudo nsenter --target "$PID" --mount --uts --ipc --net --pid /bin/sh