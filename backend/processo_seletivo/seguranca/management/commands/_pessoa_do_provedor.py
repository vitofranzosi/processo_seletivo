"""A pessoa de um par provedor e identificador, para os comandos de implantação (107).

Localiza, e nunca cria: suspender, reativar, retirar ou substituir supõe alguém que já existe. Pelo
par, como na entrada, e nunca pelo e-mail (`D-003` da `106`).
"""

from django.core.management.base import CommandError

from processo_seletivo.seguranca.models import IdentidadeExterna


def pessoa_do_provedor(provedor, identificador):
    externa = (
        IdentidadeExterna.objects.select_related("pessoa")
        .filter(provedor=(provedor or "").strip(), identificador=(identificador or "").strip())
        .first()
    )
    if externa is None:
        raise CommandError(f"nenhuma pessoa com a identidade {provedor}:{identificador}.")
    return externa.pessoa


def argumentos_da_pessoa(parser, prefixo=""):
    ajuda = f" ({prefixo.strip('-')})" if prefixo else ""
    parser.add_argument(
        f"--{prefixo}provedor", required=True, help=f"O nome do adaptador institucional{ajuda}."
    )
    parser.add_argument(
        f"--{prefixo}identificador",
        required=True,
        help=f"O identificador estável no provedor{ajuda}.",
    )
