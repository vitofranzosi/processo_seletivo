"""Política de privilégios dos papéis PostgreSQL (FR-019 da 003).

O projeto separa quem migra de quem executa: o papel de migração cria e altera esquema; o de
runtime, que é o da aplicação em serviço, só faz o que a operação normal exige. Sobre os registros
append-only ele recebe `SELECT` e `INSERT` e nada mais — nem `UPDATE`, nem `DELETE`.

Isso é a segunda camada da imutabilidade, independente das triggers. A trigger recusa a mutação
mesmo de quem tem privilégio; o privilégio ausente recusa antes, mesmo que a trigger seja removida.
Nenhuma das duas depende da aplicação se comportar.

**A ordem de implantação é: provisionar, migrar, provisionar de novo.** Papel e privilégio default
existem antes de qualquer tabela; privilégio de tabela só pode ser concedido depois que ela existe.
Por isso todo comando que toca tabela é condicional à existência dela — a primeira execução, em
banco vazio, é um no-op silencioso em vez de um erro — e a segunda, depois das migrations, é a que
tranca de fato. O comando informa quantas tabelas protegeu, para que a etapa esquecida apareça no
momento em que é esquecida, e não numa auditoria meses depois.

Este módulo é a **única** fonte da política: o comando `provisionar_papeis` a aplica e os testes de
conformidade a verificam. Uma cópia nos testes verificaria a si mesma.
"""

# Tabelas cujo conteúdo é histórico normativo ou trilha de auditoria: nascem e não mudam mais.
# `Retificacao` e `AlteracaoNormativa` ficam de fora de propósito — mudam legitimamente enquanto o
# ato está em curso, e a imutabilidade delas é condicional ao estado final, o que só a trigger
# consegue expressar.
TABELAS_APPEND_ONLY = (
    "auditoria_registroauditoria",
    # A conclusão preservada da `012`: o que uma pessoa havia concluído antes de cada reabertura.
    # É histórico pela mesma razão que os demais — nasce e não muda —, e a garantia precisa valer
    # também para quem chegue por fora da aplicação (FR-094).
    "avaliacoes_conclusaoavaliacao",
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


def _lista_sql(valores) -> str:
    return "ARRAY[" + ", ".join(_literal(valor) for valor in valores) + "]"


def comandos_de_papeis(*, database, migration_role, runtime_role, migration_password,
                       runtime_password):
    """Papéis, senhas, acesso ao banco e privilégios default. Válido em banco vazio.

    `ALTER DEFAULT PRIVILEGES` é o que faz tabela criada por migration futura já nascer acessível
    ao runtime. Não cobre a restrição das append-only: privilégio default não sabe distinguir uma
    tabela da outra, e é por isso que a segunda passada continua sendo necessária.
    """
    banco, migracao, runtime = _citar(database), _citar(migration_role), _citar(runtime_role)
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
        # Senha reafirmada em vez de o papel ser recriado: derrubá-lo exigiria desconectar a
        # aplicação em serviço. O papel de migração também autentica — `.env.example` sempre
        # declarou `DB_MIGRATION_PASSWORD`, e criá-lo com LOGIN e sem senha deixava a variável
        # descrevendo uma credencial que não existia.
        f"ALTER ROLE {migracao} WITH PASSWORD {_literal(migration_password)}",
        f"ALTER ROLE {runtime} WITH PASSWORD {_literal(runtime_password)}",
        f"GRANT CONNECT ON DATABASE {banco} TO {migracao}, {runtime}",
        f"GRANT USAGE ON SCHEMA public TO {runtime}",
        f"GRANT USAGE, CREATE ON SCHEMA public TO {migracao}",
        f"ALTER SCHEMA public OWNER TO {migracao}",
        f"ALTER DEFAULT PRIVILEGES FOR ROLE {migracao} IN SCHEMA public "
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO {runtime}",
        f"ALTER DEFAULT PRIVILEGES FOR ROLE {migracao} IN SCHEMA public "
        f"GRANT USAGE, SELECT ON SEQUENCES TO {runtime}",
    ]


def comandos_de_privilegios(*, migration_role, runtime_role, tabelas=TABELAS_APPEND_ONLY):
    """Propriedade e privilégios sobre as tabelas que já existem. No-op em banco vazio.

    A transferência de propriedade não é detalhe: `GRANT ALL` deixa o papel de migração usar as
    tabelas, mas `ALTER TABLE` exige ser dono. Sem isto, um esquema criado pelo superusuário faz
    a próxima migration falhar em produção — no pior momento possível, com o deploy no meio.
    """
    migracao, runtime = _citar(migration_role), _citar(runtime_role)
    return [
        f"""
        DO $$
        DECLARE alvo record;
        BEGIN
            FOR alvo IN SELECT tablename FROM pg_tables WHERE schemaname = 'public' LOOP
                EXECUTE format('ALTER TABLE public.%I OWNER TO {migracao}', alvo.tablename);
            END LOOP;
            FOR alvo IN SELECT sequencename FROM pg_sequences WHERE schemaname = 'public' LOOP
                EXECUTE format('ALTER SEQUENCE public.%I OWNER TO {migracao}', alvo.sequencename);
            END LOOP;
        END
        $$;
        """,
        f"GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO {runtime}",
        f"GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO {runtime}",
        # Condicional à existência: em banco vazio não há o que revogar, e falhar ali obrigaria a
        # migrar antes de existir papel para migrar — a ordem não fecharia.
        f"""
        DO $$
        DECLARE nome text;
        BEGIN
            FOREACH nome IN ARRAY {_lista_sql(tabelas)} LOOP
                IF to_regclass('public.' || nome) IS NOT NULL THEN
                    EXECUTE format('REVOKE UPDATE, DELETE ON public.%I FROM {runtime}', nome);
                END IF;
            END LOOP;
        END
        $$;
        """,
    ]


def comandos(*, database, migration_role, runtime_role, runtime_password, migration_password):
    """A política inteira, na ordem de execução. Idempotente e segura em banco vazio."""
    return [
        *comandos_de_papeis(
            database=database,
            migration_role=migration_role,
            runtime_role=runtime_role,
            migration_password=migration_password,
            runtime_password=runtime_password,
        ),
        *comandos_de_privilegios(migration_role=migration_role, runtime_role=runtime_role),
    ]


CONSULTA_DE_CONFERENCIA = """
SELECT nome,
       has_table_privilege(%s, 'public.' || nome, 'UPDATE')
       OR has_table_privilege(%s, 'public.' || nome, 'DELETE') AS excessivo
FROM unnest(%s::text[]) AS nome
WHERE to_regclass('public.' || nome) IS NOT NULL
"""


def conferencia(runtime_role):
    """Argumentos de `CONSULTA_DE_CONFERENCIA`: quais append-only existentes ainda dão escrita.

    Conferir depois de aplicar é o que transforma "rodei o comando" em "a política está valendo".
    Sem isso, esquecer a segunda passada — a de depois das migrations — deixaria o runtime com
    UPDATE e DELETE sobre a trilha de auditoria, e nada avisaria.
    """
    return (runtime_role, runtime_role, list(TABELAS_APPEND_ONLY))
