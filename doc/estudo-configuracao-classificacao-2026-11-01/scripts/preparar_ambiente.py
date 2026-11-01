import json
import os
import secrets
import subprocess
from pathlib import Path

raiz = Path(__file__).resolve().parents[3]
env = os.environ.copy()
env.update(
    LC_ALL="pt_BR.UTF-8",
    DJANGO_SETTINGS_MODULE="config.settings.development",
    DB_NAME="ps_ux_classificacao_20261101",
    DB_HOST="localhost",
    DB_PORT="5432",
    DB_ROLE="runtime",
    DB_RUNTIME_USER=os.environ["USER"],
    DB_RUNTIME_PASSWORD="",
    INTERFACE_SELETOR_IDENTIDADE="true",
)
senha = secrets.token_urlsafe(24)
config = {
    "DB_NAME": env["DB_NAME"],
    "DB_HOST": "localhost",
    "DB_ROLE": "runtime",
    "DB_RUNTIME_USER": "ps_uxclass_runtime",
    "DB_RUNTIME_PASSWORD": senha,
    "DJANGO_SETTINGS_MODULE": "config.settings.development",
    "INTERFACE_SELETOR_IDENTIDADE": "true",
    "LC_ALL": "pt_BR.UTF-8",
}
p = Path("/tmp/ps_uxclass_env.json")
p.write_text(json.dumps(config))
p.chmod(0o600)
subprocess.run(["createdb", env["DB_NAME"]], env=env, check=True)
provisionar = [
    "uv",
    "run",
    "python",
    "manage.py",
    "provisionar_papeis",
    "--migration-role",
    "ps_uxclass_migracao",
    "--migration-password",
    senha,
    "--runtime-role",
    "ps_uxclass_runtime",
    "--runtime-password",
    senha,
]
log = raiz / "doc/estudo-configuracao-classificacao-2026-11-01/preparacao.log"
with log.open("w") as f:
    for args, extra in [
        (provisionar, {}),
        (
            ["uv", "run", "python", "manage.py", "migrate"],
            {
                "DB_ROLE": "migration",
                "DB_MIGRATION_USER": "ps_uxclass_migracao",
                "DB_MIGRATION_PASSWORD": senha,
            },
        ),
        (provisionar, {}),
        (["uv", "run", "python", "manage.py", "semear_unidades"], config),
        (["uv", "run", "python", "manage.py", "migrate", "--check"], config),
        (
            [
                "uv",
                "run",
                "python",
                "manage.py",
                "seed_demo",
                "--codigo",
                "UX-CLASS-20261101",
                "--numero",
                "01",
            ],
            config,
        ),
    ]:
        subprocess.run(
            args,
            env=env | extra,
            cwd=raiz / "backend",
            stdout=f,
            stderr=subprocess.STDOUT,
            check=True,
        )
print("Banco exclusivo preparado; logs em", log)
