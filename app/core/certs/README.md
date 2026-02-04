## Генерация ключей RSA для JWT

#### Для создания пары ключей (приватный/публичный), выполните следующие команды:

```shell
# Переход в certs директорию
cd app/core/certs/
```

```shell
# Генерация закрытого ключа (Private Key)
openssl genrsa -out jwt-private.pem 2048
```

```shell
Ограничение прав доступа (рекомендуется)
chmod 600 jwt-private.pem
```

```shell
# Извлечение открытого ключа (Public Key)
openssl rsa -in jwt-private.pem -outform PEM -pubout -out jwt-public.pem
```

#### Убедиться что ключи(jwt-public.pem, wt-private.pem) находятся в .gitignore

#### Важно: Никогда не передавать jwt-private.pem третьим лицам и не фиксировать его в системе контроля версий (Git)
