#para se der erro
set -e

NAME=$1
CPU=$2
MEMORY=$3  
SCRIPT=$4   

ROOTFS_TAR="/containers/alphine.tar.gz"
ROOTFS_DIR="/containers/basefs"


mkdir -p "$ROOTFS_DIR"
tar -xzf "$ROOTFS_TAR" -C "$ROOTFS_DIR"

BASE_DIR="./containers/namespaces/$NAME"
ROOTFS_DIR="./containers/basefs"
CGROUP_BASE="/sys/fs/cgroup"



#cria diretorio do conteiner
# Cria namespaces (PID, NET, MOUNT)
# apos -c tudo está sendo executando dentro do namespace 
#mount --bind copia o filsesystem base para dentro do namespace
#pivot_root . old_root troca o diretorio raiz para o o diretorio base criado
#mount -t proc proc /proc monta o sistema de arquivos base no novo file system
#umount -l /old_root || truermdir /old_root || true demonta e remove o fileystem antigo 
unshare --fork --pid --mount --net --uts --ipc bash -c "
    set -e

    hostname $NAME

    mkdir -p /newroot
    mount --bind $ROOTFS_DIR /newroot

    cd /newroot
    mkdir -p old_root

    pivot_root . old_root

    mount -t proc proc /proc
    mount -t sysfs sys /sys
    mount -t tmpfs tmpfs /tmp
    mount -t devtmpfs devtmpfs /dev

    umount -l /old_root || true
    rmdir /old_root || true

    echo \"🌍 Container '$NAME' iniciado (PID: $$)\"

    if [ -n \"$SCRIPT\" ]; then
       
        /bin/sh -c \"$SCRIPT\"
        echo \"✅ Script finalizado.\"
        sleep 2
    else
        exec /bin/sh
    fi
    sleep infinity
" &

PID=$!
mkdir -p "$BASE_DIR"   # garante que o host tem o diretório
echo $PID > "$BASE_DIR/pid"
sleep 1  # espera o namespace inicializar


#cgroups


CPU_QUOTA=$((CPU * 1000))

mkdir -p $CGROUP_BASE/cpu/$NAME
mkdir -p $CGROUP_BASE/memory/$NAME

# Limita CPU
echo $CPU_QUOTA > sudo tee $CGROUP_BASE/cpu/$NAME/cpu.cfs_quota_us
echo 100000 > sudo tee $CGROUP_BASE/cpu/$NAME/cpu.cfs_period_us

# Limita memória
echo $((MEMORY * 1024 * 1024)) > sudo tee $CGROUP_BASE/memory/$NAME/memory.limit_in_bytes

# Adiciona o processo principal do container aos cgroups
echo $PID > sudo tee $CGROUP_BASE/cpu/$NAME/cgroup.procs
echo $PID > sudo tee $CGROUP_BASE/memory/$NAME/cgroup.procs

echo "✅ Container '$NAME' iniciado (PID=$PID)"
echo "   CPU: $CPU% | MEM: ${MEMORY}MB"
echo "   RootFS: $ROOTFS_DIR"
echo "   Para acessar: sudo nsenter --target $PID --mount --uts --ipc --net --pid /bin/sh"
