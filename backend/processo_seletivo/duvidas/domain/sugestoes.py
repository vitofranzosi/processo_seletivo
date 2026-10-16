"""A resposta da pergunta sugerida, composta para o painel do candidato (protótipo da Fase C).

**A `070` responde para a tela de validação**, com uma explicação e cartões. A explicação dela fala
a língua daquela tela — "está no cartão", "o Perfil INF-BJN", "sem modalidade", "certame" —, e num
balão de conversa isso lê mal; pior, ia ao modelo pelo histórico, e ele a repetia (avaliação de
14/10). Aqui a resposta é recomposta **a partir dos mesmos cartões, e de nada além deles**: muda a
redação, e não o conteúdo. O contrato da `070` não muda.

**As condições do Edital continuam.** A lista de documentos leva as instruções de cada um, o anexo
de modelo e o que cada vaga reservada acrescenta; a de vagas, o cadastro de reserva e a reversão.
Ficar curto não pode custar a exceção.

Duas perguntas têm composição própria — documentos e vagas, que são as das sugestões principais e
as que mais sofriam. As outras usam a explicação da `070`, com o Perfil trocado pelo nome da opção.

Os trechos saem no formato da troca do piloto: `explicacao`, `item` (com `detalhe`) e `aviso`. O
histórico repete ao modelo o que o candidato leu.
"""

from __future__ import annotations

import re

from processo_seletivo.duvidas.domain import catalogo, respostas
from processo_seletivo.duvidas.domain.estruturas import DADO

_DOCUMENTO = re.compile(r"Documento exigido “(.+)”")
_MODALIDADE = re.compile(r"Vagas da modalidade (\S+) — (.+)")


#: A pergunta como o candidato a leria. O catálogo da `070` diz "Perfil", que é a palavra do
#: sistema; no painel, a escolha é uma opção da seleção.
TEXTO_NO_PAINEL = {
    "P-03": "Quantas vagas há?",
    "P-04": "Quais são os requisitos?",
    "P-06": "Posso me inscrever em mais de uma opção?",
}


def texto_no_painel(codigo) -> str:
    return TEXTO_NO_PAINEL.get(codigo) or catalogo.POR_CODIGO[codigo].texto


def nome_da_opcao(perfil, perfis) -> str:
    """O nome que o candidato reconhece: o do curso e, quando os nomes se repetem, o do polo."""
    nome, lugar = perfil.get("name") or "", perfil.get("locality") or ""
    repetido = sum(1 for outro in perfis if (outro.get("name") or "") == nome) > 1
    if repetido:
        return lugar or f"{nome} ({perfil.get('code', '')})"
    if lugar and lugar not in nome:
        return f"{nome} — {lugar}"
    return nome


def _explicacao(texto, fontes=()):
    return {"natureza": "explicacao", "texto": texto, "fontes": list(fontes)}


def _item(texto, detalhe="", fontes=()):
    return {"natureza": "item", "texto": texto, "detalhe": detalhe, "fontes": list(fontes)}


def _avisos(resposta):
    return [{"natureza": "aviso", "texto": aviso.texto, "fontes": []} for aviso in resposta.avisos]


def _vaga_reservada(sigla, nome):
    return f"reservadas a {nome[0].lower()}{nome[1:]} ({sigla})"


def _documentos(resposta):
    """`nome → {obrigatoriedade, detalhes, fontes}`, na ordem dos cartões."""
    documentos = {}
    for referencia in resposta.referencias:
        achado = _DOCUMENTO.fullmatch(referencia.localizacao)
        if not achado:
            continue
        documento = documentos.setdefault(
            achado.group(1), {"obrigatoriedade": "", "detalhes": [], "fontes": []}
        )
        documento["fontes"].append(referencia.localizacao)
        if referencia.rotulo == "Obrigatoriedade":
            documento["obrigatoriedade"] = referencia.conteudo
        elif referencia.rotulo == "Anexo vinculado":
            documento["detalhes"].append(f"Modelo: {referencia.conteudo}")
        else:
            documento["detalhes"].append(referencia.conteudo)
    return documentos


def _p05(lido, resposta, perfil, opcao):
    documentos = _documentos(resposta)
    obrigatorios = {n: d for n, d in documentos.items() if d["obrigatoriedade"] == "obrigatório"}
    facultativos = [n for n, d in documentos.items() if d["obrigatoriedade"] != "obrigatório"]
    trechos = []
    if obrigatorios:
        trechos.append(_explicacao(f"Na opção {opcao}, são obrigatórios:"))
        trechos += [
            _item(nome, " ".join(d["detalhes"]), d["fontes"]) for nome, d in obrigatorios.items()
        ]
    if len(facultativos) == 1:
        trechos.append(_explicacao(f"É facultativo: {facultativos[0]}."))
    elif facultativos:
        trechos.append(_explicacao(f"São facultativos: {'; '.join(facultativos)}."))
    # O que cada vaga reservada acrescenta: a autodeclaração não pode sumir da resposta só porque a
    # pergunta não disse a modalidade.
    for valor, rotulo in catalogo.opcoes_de_modalidade(_perfil(lido, perfil)):
        if valor in (catalogo.SEM_MODALIDADE, "AC") or " — " not in rotulo:
            continue
        da_vaga = _documentos(respostas.responder(lido, "P-05", perfil=perfil, modalidade=valor))
        novos = [nome for nome in da_vaga if nome not in documentos]
        if novos:
            sigla, nome = rotulo.split(" — ", 1)
            trechos.append(
                _explicacao(
                    f"Quem concorre às vagas {_vaga_reservada(sigla, nome)} envia também: "
                    f"{'; '.join(novos)}."
                )
            )
    trechos.append(
        _explicacao("A conferência dos documentos é feita na seleção, e não por este assistente.")
    )
    return trechos + _avisos(resposta)


def _p03(lido, resposta, perfil, opcao):
    dados = [r for r in resposta.referencias if r.natureza == DADO]
    total = next((r for r in dados if r.rotulo == "Vagas imediatas"), None)
    if total is None:
        return None
    trechos = [_explicacao(f"Na opção {opcao}, são {total.conteudo} vagas:", [total.localizacao])]
    for dado in dados:
        if dado is total:
            continue
        reservada = _MODALIDADE.fullmatch(dado.rotulo)
        if dado.rotulo == "Vagas da ampla concorrência":
            trechos.append(_item(f"{dado.conteudo} de ampla concorrência", "", [dado.localizacao]))
        elif reservada:
            sigla, nome = reservada.groups()
            texto = f"{dado.conteudo} {_vaga_reservada(sigla, nome)}"
            trechos.append(_item(texto, "", [dado.localizacao]))
        else:
            trechos.append(_explicacao(f"{dado.rotulo}: {dado.conteudo}.", [dado.localizacao]))
    return trechos + _avisos(resposta)


def _perfil(lido, codigo):
    return next(p for p in lido.conteudo.get("profiles") or [] if p.get("code") == codigo)


COMPOSICOES = {"P-05": _p05, "P-03": _p03}


def escolha(perfil, opcao, modalidade=None):
    """O trecho `contexto`: a opção que a sugestão escolheu, para o sistema dizer ao modelo.

    Não aparece no painel nem entra no texto do histórico. A lista de concorrência fica dita como
    não informada: escolher o polo não diz se a pessoa concorre por vaga reservada.
    """
    lista = (
        "não informada" if not modalidade or modalidade == catalogo.SEM_MODALIDADE else modalidade
    )
    return {
        "natureza": "contexto",
        "texto": (
            f"opção escolhida na pergunta sugerida: {opcao} (nas fontes, Perfil {perfil}). "
            f"Lista de concorrência: {lista}."
        ),
        "perfil": perfil,
        "fontes": [],
    }


def compor(lido, codigo, resposta, perfil=None):
    """Os trechos da resposta, para o painel e para o histórico."""
    opcao = ""
    if perfil:
        opcao = nome_da_opcao(_perfil(lido, perfil), lido.conteudo.get("profiles") or [])
    contexto = [escolha(perfil, opcao)] if perfil else []
    composta = COMPOSICOES.get(codigo)
    trechos = composta(lido, resposta, perfil, opcao) if composta and perfil else None
    if trechos is not None:
        return trechos + contexto
    explicacao = resposta.explicacao.conteudo
    if perfil:
        explicacao = re.sub(rf"\b[Oo] Perfil {re.escape(perfil)}\b", f"A opção {opcao}", explicacao)
        explicacao = re.sub(rf"\bPerfil {re.escape(perfil)}\b", f"opção {opcao}", explicacao)
    # Os dados vão ao histórico, e não ao balão: a explicação da `070` já os diz.
    dados = [
        {
            "natureza": "dado",
            "texto": f"{r.rotulo}: {r.conteudo}" if r.rotulo else r.conteudo,
            "fontes": [r.localizacao],
        }
        for r in resposta.referencias
        if r.natureza == DADO
    ]
    return [_explicacao(explicacao), *_avisos(resposta), *dados, *contexto]
