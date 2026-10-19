"""Conferencia explicita e somente leitura. Administracao e baseline bloqueadas na revisao A1."""

import json
import os
import sys


def main():
    from contrato import IDENTIDADE, exigir_selecao, verificar_banco
    if sys.argv[1:] != ["conferir", IDENTIDADE] or os.environ.get("HOM_TAREFA") != "conferir":
        raise RuntimeError("Somente conferencia explicita e autorizavel nesta revisao")
    if any(os.environ.get(k) for k in ("HOM_ADMIN_PASSWORD", "HOM_MIGRATION_PASSWORD")):
        raise RuntimeError("Credencial privilegiada proibida nesta tarefa")
    exigir_selecao()
    import django
    django.setup()
    from django.db import connection, transaction
    try:
        with transaction.atomic():
            with connection.cursor() as cursor:
                cursor.execute("SET TRANSACTION READ ONLY")
                cursor.execute("SHOW transaction_read_only")
                if cursor.fetchone() != ("on",):
                    raise RuntimeError("Leitura exclusiva nao comprovada")
            verificar_banco(connection)
    finally:
        connection.close()
    print(json.dumps({"tarefa": "conferir", "estado": "sucesso", "banco": "somente leitura"}))


if __name__ == "__main__":
    main()
