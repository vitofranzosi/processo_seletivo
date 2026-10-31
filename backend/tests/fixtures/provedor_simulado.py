"""O provedor institucional simulado (106, `FR-3024`): só aqui, sem rede, e marcado como de teste.

Faz o papel do provedor de verdade sem nenhum: o teste **emite** uma identidade, recebe um bilhete
opaco, e é com ele que o navegador volta. `concluir` troca o bilhete pela identidade uma vez só, e
não lê mais nada do pedido — nem cabeçalho, nem nome, nem e-mail mandados pelo cliente. É a mesma
forma do retorno de um OIDC: o que chega ao GPS é um código que só o provedor sabe resolver.

Mora em `tests.`, e `production.py` recusa qualquer provedor desse pacote; e se declara de teste,
que é a segunda recusa, para o caso de alguém o copiar para fora daqui.

**Tem uma subclasse fora da suíte**: `tests/homologacao/provedor.py`, que leva pessoas às telas da
gestão antes do SSO, num ambiente de homologação isolado (110, `D-018`). As duas recusas valem para
ela pela herança e pelo pacote — quem mexer aqui está mexendo também no que aquele ambiente usa.
"""

import secrets
from urllib.parse import urlencode

from django.shortcuts import redirect

from processo_seletivo.seguranca.autenticacao import IdentidadeAutenticada

CAMINHO = "tests.fixtures.provedor_simulado.ProvedorSimulado"
NOME = "simulado"

# Onde o navegador é mandado para autenticar. Nos testes de cliente ninguém segue o endereço; os de
# navegador (107) o trocam pelo da página de autorização que eles mesmos servem, e que também mora
# no código de teste (`tests/navegador/provedor.py`). `.invalid` não resolve em rede nenhuma.
ENDERECO_DE_AUTORIZACAO = "https://provedor.invalid/autorizar"

# Os bilhetes emitidos e ainda não usados, e o estado da última ida. Do processo, e não da sessão:
# o provedor é outra parte, e não lê a sessão do GPS.
_BILHETES = {}
_IDAS = []


def emitir(identificador, *, nome="", email="", provedor=NOME):
    """O bilhete que o provedor daria depois de autenticar esta pessoa."""
    bilhete = secrets.token_urlsafe(16)
    _BILHETES[bilhete] = IdentidadeAutenticada(provedor, identificador, nome, email)
    return bilhete


def descartar(bilhete):
    """Retira um bilhete emitido e não usado: a homologação descarta os da mesma página."""
    _BILHETES.pop(bilhete, None)


def ultima_ida():
    return _IDAS[-1]


def limpar():
    _BILHETES.clear()
    _IDAS.clear()


class ProvedorSimulado:
    nome = NOME
    apenas_para_testes = True

    def iniciar(self, request, *, retorno, estado):
        _IDAS.append({"retorno": retorno, "estado": estado})
        # `state` e `redirect_uri`, como um provedor OIDC: o estado é o nome que a volta usa, e o
        # que a gestão lê; o retorno é para onde a página de autorização do navegador (107) manda.
        consulta = urlencode({"state": estado, "redirect_uri": retorno})
        return redirect(f"{ENDERECO_DE_AUTORIZACAO}?{consulta}")

    def concluir(self, request, *, estado):
        return _BILHETES.pop(request.GET.get("bilhete", ""), None)
