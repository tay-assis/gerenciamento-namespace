#!/bin/bash
set -e

NAME=$1
CPU=$2
MEMORY=$3
SCRIPT=$4

ROOTFS_TAR="./containers/alpine.tar.gz"
ROOTFS_DIR="./containers/basefs"
BASE_DIR="./containers/namespaces/$NAME"
CGROUP_BASE="/sys/fs/cgroup"

# 1️⃣ Garante que o rootfs existe
if [ ! -d "$ROOTFS_DIR" ] || [ -z "$(ls -A "$ROOTFS_DIR")" ]; then
    mkdir -p "$ROOTFS_DIR"
    tar -xzf "$ROOTFS_TAR" -C "$ROOTFS_DIR"
fi


mount --bind $ROOTFS_DIR /newroot
unshare --fork --pid --mount --net --uts --ipc bash -c "
    set -e
    hostname $NAME

    mkdir -p /newroot
    /bin/mount --bind $ROOTFS_DIR /newroot


    cd /newroot
    mkdir -p old_root
    pivot_root . old_root


    mount -t proc proc /proc
    mount -t sysfs sys /sys
    mount -t tmpfs tmpfs /tmp
    mount -t devtmpfs devtmpfs /dev || true


    umount -l /old_root || true
    rmdir /old_root || true

    echo \"🌍 Container '$NAME' iniciado (PID: $$)\"

    if [ -n \"$SCRIPT\" ]; then
        /bin/sh -c \"$SCRIPT\"
        echo \"✅ Script finalizado.\"
        sleep 2
    fi
" &


PID=$!
mkdir -p "$BASE_DIR"
echo $PID > "$BASE_DIR/pid"
sleep 1

# 3️⃣ Cgroups — detecção automática
CGROUP_TYPE=$(stat -fc %T /sys/fs/cgroup)
CPU_QUOTA=$((CPU * 1000))
MEM_LIMIT=$((MEMORY * 1024 * 1024))

if [ "$CGROUP_TYPE" = "cgroup2fs" ]; then
    CGROUP_PATH="$CGROUP_BASE/$NAME"
    sudo mkdir -p "$CGROUP_PATH"

    # Limites
    echo "$CPU_QUOTA 100000" | sudo tee "$CGROUP_PATH/cpu.max" >/dev/null
    echo "$MEM_LIMIT" | sudo tee "$CGROUP_PATH/memory.max" >/dev/null

    # Adiciona o processo
    echo "$PID" | sudo tee "$CGROUP_PATH/cgroup.procs" >/dev/null

else
    echo "⚙️ Usando cgroups v1"
    sudo mkdir -p $CGROUP_BASE/cpu/$NAME
    sudo mkdir -p $CGROUP_BASE/memory/$NAME

    echo $CPU_QUOTA | sudo tee $CGROUP_BASE/cpu/$NAME/cpu.cfs_quota_us >/dev/null
    echo 100000 | sudo tee $CGROUP_BASE/cpu/$NAME/cpu.cfs_period_us >/dev/null
    echo $MEM_LIMIT | sudo tee $CGROUP_BASE/memory/$NAME/memory.limit_in_bytes >/dev/null

    echo $PID | sudo tee $CGROUP_BASE/cpu/$NAME/cgroup.procs >/dev/null
    echo $PID | sudo tee $CGROUP_BASE/memory/$NAME/cgroup.procs >/dev/null
fi

# 4️⃣ Resumo
echo
echo "namespace '$NAME' iniciado (PID=$PID)"
echo "   CPU: $CPU% | MEM: ${MEMORY}MB"
echo "   RootFS: $ROOTFS_DIR"
echo "   Para acessar: sudo nsenter --target $PID --mount --uts --ipc --net --pid /bin/sh"
