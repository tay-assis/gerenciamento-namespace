#!/bin/bash
set -e

NAME=$1
CPU=$2
MEMORY=$3
SCRIPT=$4
BASE_DIR="/containers/$NAME"
CGROUP_DIR="/sys/fs/cgroup/$NAME"

mkdir -p "$BASE_DIR"
mkdir -p "$CGROUP_DIR"

# 1️⃣ Cria namespaces (PID, NET, MOUNT)
sudo unshare --fork --pid --mount --net --uts --ipc bash -c "
    hostname $NAME
    mount -t proc proc /proc
    sleep infinity
" &

PID=$!
echo $PID > "$BASE_DIR/pid"

# 2️⃣ Configura cgroups
mkdir -p /sys/fs/cgroup/cpu/$NAME
mkdir -p /sys/fs/cgroup/memory/$NAME

# limita CPU (ex: 50% → quota 50000)
echo 50000 > sudo tee /sys/fs/cgroup/cpu/$NAME/cpu.cfs_quota_us
echo 100000 > sudo tee /sys/fs/cgroup/cpu/$NAME/cpu.cfs_period_us

# limita memória (ex: 512MB)
echo $((MEMORY * 1024 * 1024)) > sudo tee /sys/fs/cgroup/memory/$NAME/memory.limit_in_bytes

# adiciona o processo ao cgroup
echo $PID > sudo tee /sys/fs/cgroup/cpu/$NAME/cgroup.procs
echo $PID > sudo tee /sys/fs/cgroup/memory/$NAME/cgroup.procs

#if [ -n "$SCRIPT" ]; then
#    echo "$SCRIPT" > sudo tee "$BASE_DIR/startup.sh"
#    chmod +x "$BASE_DIR/startup.sh"
#    nsenter --target $PID --mount --uts --ipc --net --pid bash -c "$BASE_DIR/startup.sh > $BASE_DIR/output.log 2>&1 &"
#fi

echo "Namespace $NAME criado (PID=$PID)"

