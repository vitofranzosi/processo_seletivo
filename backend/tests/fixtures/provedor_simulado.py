"""O provedor institucional simulado (106, `FR-3024`): só aqui, sem rede, e marcado como de teste.

Faz o papel do provedor de verdade sem nenhum: o teste **emite** uma identidade, recebe um bilhete
opaco, e é com ele que o navegador volta. `concluir` troca o bilhete pela identidade uma vez só, e
não lê mais nada do pedido — nem cabeçalho, nem nome, nem e-mail mandados pelo cliente. É a mesma
forma do retorno de um OIDC: o que chega ao GPS é um código que só o provedor sabe resolver.

Mora em `tests.`, e `production.py` recusa qualquer provedor desse pacote; e se declara de teste,
que é a segunda recusa, para o caso de alguém o copiar para fora daqui.
"""

import secrets
from urllib.parse import urlencode

from django.shortcuts import redirect

from processo_seletivo.seguranca.autenticacao import IdentidadeAutenticada

CAMINHO = "tests.fixtures.provedor_simulado.ProvedorSimulado"
NOME = "simulado"

# Os bilhetes emitidos e ainda não usados, e o estado da última ida. Do processo, e não da sessão:
# o provedor é outra parte, e não lê a sessão do GPS.
_BILHETES = {}
_IDAS = []


def emitir(identificador, *, nome="", email="", provedor=NOME):
    """O bilhete que o provedor daria depois de autenticar esta pessoa."""
    bilhete = secrets.token_urlsafe(16)
    _BILHETES[bilhete] = IdentidadeAutenticada(provedor, identificador, nome, email)
    return bilhete


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
        return redirect(f"https://provedor.invalid/autorizar?{urlencode({'estado': estado})}")

    def concluir(self, request, *, estado):
        return _BILHETES.pop(request.GET.get("bilhete", ""), None)
