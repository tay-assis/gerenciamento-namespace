#!/bin/bash
set -e

NAME=$1
CPU=$2
MEMORY=$3
IO=$4
SCRIPT=$5

ROOTFS_TAR="./containers/alpine.tar.gz"
ROOTFS_DIR="./containers/basefs"
BASE_DIR="./containers/namespaces/$NAME"
CGROUP_BASE="/sys/fs/cgroup"

#Cria o base SystemFile se não existir
if [ ! -d "$ROOTFS_DIR" ] || [ -z "$(ls -A "$ROOTFS_DIR")" ]; then
    mkdir -p "$ROOTFS_DIR"
    tar -xzf "$ROOTFS_TAR" -C "$ROOTFS_DIR"
fi


#CRIA O NAMESPACE
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

    echo \" Container '$NAME' iniciado (PID: $$)\"

    if [ -n \"$SCRIPT\" ]; then
        /bin/sh -c \"$SCRIPT\"
        echo \"Script finalizado.\"
        sleep 2
    fi
" &


PID=$!
mkdir -p "$BASE_DIR"
echo $PID > "$BASE_DIR/pid"
sleep 1

#CRIA O CGROUPS
CGROUP_TYPE=$(stat -fc %T /sys/fs/cgroup)
CPU_QUOTA=$((CPU * 1000))
MEM_LIMIT=$((MEMORY * 1024 * 1024))

sudo sh -c 'echo +io > /sys/fs/cgroup/cgroup.subtree_control'
IO_LIMIT=$((IO * 1048576))


CGROUP_PATH="$CGROUP_BASE/$NAME"

mkdir -p "$CGROUP_PATH"
echo "$CPU_QUOTA 100000" > "$CGROUP_PATH/cpu.max"
echo "$MEM_LIMIT" > "$CGROUP_PATH/memory.max"
echo "8:0 rbps=$IO_LIMIT" > "$CGROUP_PATH/io.max"

#ADICIONA NAMESPACE AO CGROUPS CRIADO
echo "$PID" > "$CGROUP_PATH/cgroup.procs"
echo "$PID" | sudo tee "$CGROUP_PATH/cgroup.procs"
