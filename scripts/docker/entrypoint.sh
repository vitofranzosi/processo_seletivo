#!/bin/sh
# Prepara o banco antes de entregar o processo ao comando pedido.
#
# A ordem é a que o próprio `provisionar_papeis` documenta — **provisionar, migrar, provisionar de
# novo** — e não é redundância: papel e privilégio padrão precisam existir antes de qualquer
# tabela, e privilégio sobre tabela só pode ser concedido depois que ela existe. A primeira passada
# roda em banco vazio e não encontra o que proteger; a segunda é a que tranca.
#
# Os três passos são idempotentes, então reiniciar o container é seguro e `--force-recreate`
# também.
set -eu

: "${POSTGRES_USER:?defina POSTGRES_USER — é com ele que os papéis são criados}"
: "${POSTGRES_PASSWORD:?defina POSTGRES_PASSWORD}"
: "${DB_MIGRATION_USER:?defina DB_MIGRATION_USER}"
: "${DB_MIGRATION_PASSWORD:?defina DB_MIGRATION_PASSWORD}"
: "${DB_RUNTIME_USER:?defina DB_RUNTIME_USER}"
: "${DB_RUNTIME_PASSWORD:?defina DB_RUNTIME_PASSWORD}"

# Capturados antes de qualquer prefixo de ambiente. `provisionar_papeis` usa as mesmas variáveis
# para duas coisas diferentes — a conexão com o banco e os papéis a criar — e nesta chamada elas
# precisam divergir: conecta-se como superusuário para poder criar papel, mas quem se cria são os
# dois papéis da aplicação. Sem estas cópias, o prefixo abaixo reescreveria também o alvo.
migracao_usuario="$DB_MIGRATION_USER"
migracao_senha="$DB_MIGRATION_PASSWORD"
runtime_usuario="$DB_RUNTIME_USER"
runtime_senha="$DB_RUNTIME_PASSWORD"

provisionar() {
    DB_ROLE=runtime \
    DB_RUNTIME_USER="$POSTGRES_USER" \
    DB_RUNTIME_PASSWORD="$POSTGRES_PASSWORD" \
        python manage.py provisionar_papeis \
            --migration-role "$migracao_usuario" \
            --migration-password "$migracao_senha" \
            --runtime-role "$runtime_usuario" \
            --runtime-password "$runtime_senha"
}

echo "[entrypoint] provisionando papéis (1/2)"
provisionar

echo "[entrypoint] aplicando migrations"
DB_ROLE=migration python manage.py migrate --noinput

# A segunda passada é a que concede privilégio sobre as tabelas que a migration acabou de criar.
# O comando imprime quantas protegeu: zero aqui significa que algo saiu da ordem.
echo "[entrypoint] provisionando papéis (2/2)"
provisionar

echo "[entrypoint] pronto — executando: $*"
exec "$@"
