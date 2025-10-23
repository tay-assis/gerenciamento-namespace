# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/jammy64"
  config.vm.hostname = "flask-vm"

  # Portas expostas
  config.vm.network "forwarded_port", guest: 5000, host: 5000
  config.vm.network "forwarded_port", guest: 3306, host: 3307   # <-- corrigido: o MySQL usa 3306 dentro do guest

  # Sincronização da pasta do projeto
  config.vm.synced_folder "./app", "/vagrant/app"

  config.vm.provider "virtualbox" do |vb|
    vb.name = "Flask-MySQL-VM"
    vb.cpus = 2
    vb.memory = 4096
    vb.gui = false
  end

  # Provisionamento
  config.vm.provision "shell", inline: <<-SHELL
    echo "=== Atualizando pacotes ==="
    apt-get update -y
    apt-get install -y mysql-server python3 python3-pip libmysqlclient-dev

    echo "=== Corrigindo diretório do MySQL ==="
    mkdir -p /var/run/mysqld
    chown -R mysql:mysql /var/run/mysqld

    echo "=== Iniciando MySQL ==="
    systemctl enable mysql
    systemctl start mysql
    sleep 5

    echo "=== Resetando senha do root ==="
    sudo mysql --user=root --skip-password -e "
    ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'password';
    FLUSH PRIVILEGES;"

    echo "=== Criando banco e permissões ==="
    mysql -u root -ppassword -e "
    CREATE DATABASE IF NOT EXISTS namespace_db;
    CREATE USER IF NOT EXISTS 'vagrant'@'%' IDENTIFIED BY 'vagrant';
    GRANT ALL PRIVILEGES ON namespace_db.* TO 'vagrant'@'%';
    FLUSH PRIVILEGES;"

    echo "=== Criando tabela namespace ==="
    mysql -u root -ppassword -e "
    USE namespace_db;
    CREATE TABLE IF NOT EXISTS namespace (
        id INT AUTO_INCREMENT PRIMARY KEY,
        nome VARCHAR(100) NOT NULL
    );"

    echo "=== Instalando Flask e dependências ==="
    pip install flask mysql-connector-python
  SHELL
end
