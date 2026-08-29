"""Política de privilégios dos papéis PostgreSQL (FR-019 da 003).

O projeto separa quem migra de quem executa: o papel de migração cria e altera esquema; o de
runtime, que é o da aplicação em serviço, só faz o que a operação normal exige. Sobre os registros
append-only ele recebe `SELECT` e `INSERT` e nada mais — nem `UPDATE`, nem `DELETE`.

Isso é a segunda camada da imutabilidade, independente das triggers. A trigger recusa a mutação
mesmo de quem tem privilégio; o privilégio ausente recusa antes, mesmo que a trigger seja removida.
Nenhuma das duas depende da aplicação se comportar.

Este módulo é a **única** fonte da política: o comando `provisionar_papeis` a aplica e os testes de
conformidade a verificam. Uma cópia nos testes verificaria a si mesma.
"""

# Tabelas cujo conteúdo é histórico normativo ou trilha de auditoria: nascem e não mudam mais.
# `Retificacao` e `AlteracaoNormativa` ficam de fora de propósito — mudam legitimamente enquanto o
# ato está em curso, e a imutabilidade delas é condicional ao estado final, o que só a trigger
# consegue expressar.
TABELAS_APPEND_ONLY = (
    "auditoria_registroauditoria",
    "processos_atoadministrativo",
    "publicacoes_documentopublicado",
    "publicacoes_publicacao",
    "publicacoes_revisaoedital",
    "publicacoes_versaoconsolidada",
)


def _citar(identificador: str) -> str:
    """Aspas duplas com escape, para nome de papel vindo de configuração."""
    return '"' + identificador.replace('"', '""') + '"'


def _literal(valor: str) -> str:
    return "'" + valor.replace("'", "''") + "'"


def comandos(*, database: str, migration_role: str, runtime_role: str, runtime_password: str):
    """Comandos SQL que estabelecem a política, na ordem em que devem ser executados.

    Idempotente: pode rodar sobre banco vazio ou já provisionado, quantas vezes for. Papel que já
    existe tem a senha reafirmada em vez de recriada, porque derrubá-lo exigiria desconectar a
    aplicação em serviço.
    """
    banco, migracao, runtime = _citar(database), _citar(migration_role), _citar(runtime_role)
    ordinarias = ", ".join(TABELAS_APPEND_ONLY)
    return [
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = {_literal(migration_role)}) THEN
                CREATE ROLE {migracao} LOGIN;
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = {_literal(runtime_role)}) THEN
                CREATE ROLE {runtime} LOGIN;
            END IF;
        END
        $$;
        """,
        f"ALTER ROLE {runtime} WITH PASSWORD {_literal(runtime_password)}",
        f"GRANT CONNECT ON DATABASE {banco} TO {migracao}, {runtime}",
        f"GRANT USAGE ON SCHEMA public TO {runtime}",
        f"GRANT USAGE, CREATE ON SCHEMA public TO {migracao}",
        # O papel de migração precisa de tudo: é ele que aplica as migrations.
        f"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO {migracao}",
        f"GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO {migracao}",
        # O de runtime recebe o necessário e depois perde o que não pode ter. A ordem importa:
        # conceder tudo e revogar o excesso cobre também tabela criada por migration futura.
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {runtime}",
        f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {runtime}",
        f"REVOKE UPDATE, DELETE ON {ordinarias} FROM {runtime}",
        # Tabelas e sequências criadas depois deste provisionamento herdam a mesma política.
        f"ALTER DEFAULT PRIVILEGES FOR ROLE {migracao} IN SCHEMA public "
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {runtime}",
        f"ALTER DEFAULT PRIVILEGES FOR ROLE {migracao} IN SCHEMA public "
        f"GRANT USAGE, SELECT ON SEQUENCES TO {runtime}",
    ]
