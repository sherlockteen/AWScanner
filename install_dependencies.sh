#!/bin/bash

# Функция для установки пакетов на Debian-подобных дистрибутивах
install_debian() {
    echo "Установка пакетов для Debian-подобного дистрибутива..."
    sudo apt update
    sudo apt install -y masscan wget jq
    pip install tls-scan
}

# Функция для установки пакетов на CentOS и RHEL
install_centos() {
    echo "Установка пакетов для CentOS/RHEL..."
    sudo yum install -y epel-release
    sudo yum install -y masscan wget jq
    pip install tls-scan
}

# Функция для установки пакетов на Arch Linux
install_arch() {
    echo "Установка пакетов для Arch Linux..."
    sudo pacman -Syu --noconfirm masscan wget jq
    pip install tls-scan
}

# Проверка дистрибутива
if [[ -f /etc/os-release ]]; then
    . /etc/os-release
    case "$ID" in
        ubuntu|debian|kali|linuxmint|pop)
            install_debian
            ;;
        centos|rhel)
            install_centos
            ;;
        arch)
            install_arch
            ;;
        *)
            echo "Неподдерживаемый дистрибутив: $ID"
            exit 1
            ;;
    esac
else
    echo "Не удалось определить дистрибутив."
    exit 1
fi

echo "Установка завершена!"
