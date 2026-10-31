"""O provedor de homologação: pessoas reais validam a gestão antes do SSO (110, `D-017`, `D-018`).

**Uma subclasse do provedor simulado da `106`, e nada mais.** Herda o bilhete — aleatório, de uso
único, retirado do provedor no retorno — e a declaração de teste. Troca só a ida: em vez de mandar
a `provedor.invalid`, responde uma página com as pessoas que a implantação cadastrou para este
provedor (`conceder_administracao_institucional --provedor homologacao ...`), cada uma com um
bilhete já emitido. Quem valida escolhe como quem entrar, e a volta é a entrada institucional de
verdade: estado ligado à sessão, pessoa, vínculos, `Actor` recalculado, prazos.

**Por que não chega a produção.** As duas recusas que já valem para o simulado: o pacote `tests.` e
a declaração de teste, no *boot* (`production.py`) e em execução (`provedor_configurado`). Nenhuma
linha nova de proteção, e nenhuma criptografia própria.

**O que ele não é.** Autenticação. Dentro do ambiente, quem chega à página escolhe a pessoa; a
barreira é o perímetro do ambiente, e não esta página (`D-018`). Por isso ele lista só quem a
implantação cadastrou, e nunca aceita um identificador digitado — que criaria pessoa por digitação.

**Um processo só.** Os bilhetes ficam na memória do processo, como no simulado: serve ao `runserver`
da imagem de desenvolvimento, que é o ambiente desta validação. Num servidor de vários processos a
volta cairia noutro, que não acharia o bilhete.
"""

from urllib.parse import urlencode

from django.http import HttpResponse
from django.utils.html import format_html, format_html_join

from tests.fixtures import provedor_simulado

CAMINHO = "tests.homologacao.provedor.ProvedorDeHomologacao"
NOME = "homologacao"

# Os bilhetes de cada página, por bilhete. Escolher uma pessoa descarta os das outras: um bilhete
# que sobrasse valeria para quem copiasse o endereço de outra linha da mesma página.
_DA_MESMA_PAGINA = {}


def _pessoas():
    """As pessoas deste provedor, pelo nome, com os papéis vigentes em palavras.

    Os modelos se importam aqui, e não no topo: o caminho do adaptador é lido pelas settings antes
    de os apps existirem.
    """
    from processo_seletivo.seguranca.application import acessos
    from processo_seletivo.seguranca.models import IdentidadeExterna

    catalogo = acessos.catalogo()
    externas = (
        IdentidadeExterna.objects.filter(provedor=NOME)
        .select_related("pessoa")
        .order_by("pessoa__first_name", "identificador")
    )
    pessoas = []
    for externa in externas:
        papeis = [
            f"{catalogo.get(papel, (papel,))[0]} ({escopo})"
            for escopo, papel in acessos.vigentes_da_pessoa(externa.pessoa_id)
        ]
        pessoas.append((externa, acessos.nome_legivel(externa.pessoa), papeis))
    return pessoas


def _pagina(linhas):
    if linhas:
        corpo = format_html(
            "<ul>{}</ul>",
            format_html_join(
                "", '<li><a href="{}">{}</a> — {}</li>', ((v, n, p) for v, n, p in linhas)
            ),
        )
    else:
        corpo = format_html(
            "<p>Nenhuma pessoa cadastrada para este provedor. Cadastre pela implantação, com "
            "<code>--provedor {}</code>.</p>",
            NOME,
        )
    return format_html(
        '<!doctype html><html lang="pt-BR"><head><meta charset="utf-8">'
        "<title>Provedor de homologação</title></head><body>"
        "<h1>Provedor de homologação</h1>"
        "<p>Ambiente de validação, sem SSO. Esta página não existe em produção.</p>"
        "<p>Entrar como:</p>{}</body></html>",
        corpo,
    )


class ProvedorDeHomologacao(provedor_simulado.ProvedorSimulado):
    nome = NOME

    def iniciar(self, request, *, retorno, estado):
        linhas, bilhetes = [], []
        for externa, nome_legivel, papeis in _pessoas():
            pessoa = externa.pessoa
            bilhete = provedor_simulado.emitir(
                externa.identificador, nome=pessoa.first_name, email=pessoa.email, provedor=NOME
            )
            bilhetes.append(bilhete)
            volta = f"{retorno}?{urlencode({'state': estado, 'bilhete': bilhete})}"
            linhas.append((volta, nome_legivel, "; ".join(papeis) or "sem papel vigente"))
        for bilhete in bilhetes:
            _DA_MESMA_PAGINA[bilhete] = bilhetes
        return HttpResponse(_pagina(linhas))

    def concluir(self, request, *, estado):
        escolhido = request.GET.get("bilhete", "")
        for bilhete in _DA_MESMA_PAGINA.pop(escolhido, ()):
            _DA_MESMA_PAGINA.pop(bilhete, None)
            if bilhete != escolhido:
                provedor_simulado.descartar(bilhete)
        return super().concluir(request, estado=estado)


def limpar():
    _DA_MESMA_PAGINA.clear()
    provedor_simulado.limpar()
