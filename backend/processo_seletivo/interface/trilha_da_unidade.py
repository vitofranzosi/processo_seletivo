"""A trilha da unidade: os atos administrativos que até a `108` só se liam pelo `psql`.

**Só leitura, e de quem audita** (`D-001`). A página pede `auditoria:consultar`, a mesma permissão
com que o Auditor lê a trilha de todo Edital da unidade. A unidade é a ativa do ator, e nenhum
parâmetro a muda (`FR-3154`): não há identificador no endereço, e por isso não há 404 — a falta de
permissão é a recusa explicada da `033`.

**A linha se monta do próprio registro** (`D-005`). O `detalhe` da unidade, da autoridade, do modelo
e do vínculo guarda o nome do instante do ato, que é o que a trilha prova, e lê-lo dali poupa uma
consulta por linha. Só o aviso e a interrupção não nomeiam o Edital, e ganham **uma** consulta por
tipo, pelos identificadores da página (`D-006`, `FR-3168`).

**O que nunca sai do registro para a tela** (`FR-3164`): o `detalhe` do modelo, que traz o assunto e
o corpo do aviso; a correlação, que liga o ato ao log de acesso; a chave de idempotência; o
identificador interno de quem praticou. O nome de quem praticou é o da tag `nome_de_pessoa`, da
`107`.
"""

from datetime import date

from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from processo_seletivo.auditoria import selectors as auditoria_selectors
from processo_seletivo.interface import identidade
from processo_seletivo.interface.views import OPERACOES
from processo_seletivo.seguranca.acessos import ESCOPO_INSTITUCIONAL
from processo_seletivo.seguranca.application.authorization import (
    base_de_permissao,
    require_authorization_base,
)
from processo_seletivo.unidades.domain.nomes import IMPLANTACAO

CONSULTAR = "auditoria:consultar"

# A ordem é a do filtro. A chave é a do seletor (`ASSUNTOS_DA_UNIDADE`), e o guardião da feature
# cobra que os dois mapas tenham as mesmas chaves.
ASSUNTOS = {
    "unidade": "Unidade",
    "autoridades": "Autoridades",
    "modelos": "Modelos de aviso",
    "avisos": "Avisos",
    "acessos": "Acessos",
}
ASSUNTO_DO_TIPO = {
    tipo: chave
    for chave, tipos in auditoria_selectors.ASSUNTOS_DA_UNIDADE.items()
    for tipo in tipos
}

# As situações que os atos administrativos gravam, cada um na grafia do próprio app: a unidade e o
# modelo em maiúsculas e no gênero do objeto, a autoridade pela vigência (que a `060` grava em
# maiúsculas), o vínculo em minúsculas (`106`). Mapa daqui, e não o `SITUACOES` das telas do
# certame: `VIGENTE` e `REVOGADO` lá não querem dizer nada, e acrescentá-los mudaria o filtro de
# toda tela.
SITUACOES = {
    "ATIVA": "Ativa",
    "DESATIVADA": "Desativada",
    "ATIVO": "Ativo",
    "INATIVO": "Inativo",
    "FUTURA": "Futura",
    "VIGENTE": "Vigente",
    "ENCERRADA": "Encerrada",
    "vigente": "Vigente",
    "revogado": "Revogado",
}

# Os dados da unidade e da autoridade que a alteração mostra, com antes e depois (`FR-3163`). São os
# do cabeçalho dos atos publicados e os de quem os assina: públicos por natureza. A ordem é a da
# tela.
CAMPOS_LEGIVEIS = {
    "Unidade": {
        "sigla": "Sigla",
        "nome": "Nome",
        "cabecalho": "Cabeçalho",
        "local": "Local",
        # Desde a 109 a sincronização grava também o canal, e sem ele aqui a alteração só do canal
        # aparecia na trilha sem nenhum dado mudado. É o canal que o candidato vê: público.
        "atendimento": "Canal de atendimento",
        "ativa": "Situação",
    },
    "AutoridadeHabilitada": {
        "nome": "Nome",
        "cargo": "Cargo",
        "ato_de_nomeacao": "Ato de nomeação",
        "inicio_vigencia": "Início da vigência",
        "fim_vigencia": "Fim da vigência",
    },
}

ORIGENS_DO_AVISO = {"RESULTADO": "aviso de resultado", "CHAMADA": "aviso de chamada"}


@require_http_methods(["GET"])
def trilha_da_unidade(request):
    """Os atos administrativos da unidade ativa, do mais recente para o mais antigo (108)."""
    ator = identidade.ator_da_sessao(request)
    if ator is None:
        return identidade.pedir_identificacao(request)
    # No escopo institucional não há unidade a ler, e a recusa é a mesma da falta de permissão: quem
    # audita o nível institucional é pergunta do usuário (`D-003`, P1).
    require_authorization_base(
        ator.can(CONSULTAR) and ator.institution_scope != ESCOPO_INSTITUCIONAL,
        bases=[base_de_permissao("consultar a trilha de auditoria da unidade")],
    )
    assunto = request.GET.get("assunto")
    if assunto not in ASSUNTOS:
        # Valor fora do formulário vale como todos, e o seletor mostra "Todos" (`D-009`): nada
        # aparece filtrado sem que a tela o diga.
        assunto = None
    registros, proximo = auditoria_selectors.trilha_da_unidade(
        actor=ator,
        assunto=assunto,
        cursor=request.GET.get("cursor"),
        limit=auditoria_selectors.LIMITE_PADRAO,
    )
    nome_da_unidade = _nome_da_unidade(ator.institution_scope)
    return render(
        request,
        "interface/trilha_da_unidade.html",
        {
            "nome_da_unidade": nome_da_unidade,
            "assuntos": list(ASSUNTOS.items()),
            "assunto_filtro": assunto or "",
            "registros": linhas(registros, nome_da_unidade=nome_da_unidade),
            "proximo_cursor": proximo,
        },
    )


def _nome_da_unidade(codigo):
    from processo_seletivo.unidades.models import Unidade

    return Unidade.objects.filter(codigo=codigo).values_list("nome", flat=True).first() or codigo


def linhas(registros, *, nome_da_unidade):
    """Cada registro como a tela o lê: quando, o quê, sobre o quê, por quem, situação e motivo."""
    from processo_seletivo.seguranca.application.acessos import catalogo

    editais = _editais_dos_avisos(registros)
    papeis = catalogo()
    return [_linha(registro, editais, papeis, nome_da_unidade) for registro in registros]


def _editais_dos_avisos(registros):
    """O Edital e a origem de cada aviso e interrupção da página: no máximo uma consulta por tipo.

    O registro da confirmação não nomeia o Edital — o motivo cita o marco pelo identificador —, e
    sem o Edital a linha não diria a quem fiscaliza de que certame o aviso partiu.
    """
    from processo_seletivo.avisos.models import Aviso, InterrupcaoDoAviso

    por_tipo = {}
    for registro in registros:
        por_tipo.setdefault(registro.aggregate_type, []).append(registro.aggregate_id)
    encontrados = {}
    if por_tipo.get("Aviso"):
        for aviso in Aviso.objects.filter(pk__in=por_tipo["Aviso"]).select_related("edital"):
            encontrados[aviso.pk] = aviso
    if por_tipo.get("InterrupcaoDoAviso"):
        # **A interrupção tem chave inteira, e a trilha a grava como `UUID(int=pk)`** (066): o
        # `UUIDField` do registro converte o inteiro em silêncio. O identificador gravado é esse, e
        # a volta é pelo `.int` — registrado como achado na spec da 108, e não corrigido aqui.
        chaves = {
            identificador.int: identificador for identificador in por_tipo["InterrupcaoDoAviso"]
        }
        for interrupcao in InterrupcaoDoAviso.objects.filter(pk__in=list(chaves)).select_related(
            "aviso__edital"
        ):
            encontrados[chaves[interrupcao.pk]] = interrupcao.aviso
    return {
        chave: f"Edital {aviso.edital.number}/{aviso.edital.year}, "
        f"{ORIGENS_DO_AVISO.get(aviso.origem, aviso.origem)}"
        for chave, aviso in encontrados.items()
    }


def _linha(registro, editais, papeis, nome_da_unidade):
    detalhe = registro.detalhe if isinstance(registro.detalhe, dict) else {}
    tipo = registro.aggregate_type
    linha = {
        "quando": registro.occurred_at,
        "operacao": _rotulo_da_operacao(registro),
        "assunto": ASSUNTOS.get(ASSUNTO_DO_TIPO.get(tipo), tipo),
        "sobre": "",
        "ator": registro.actor_subject,
        "por_implantacao": registro.actor_subject == IMPLANTACAO,
        "de": SITUACOES.get(registro.previous_state, registro.previous_state),
        "para": SITUACOES.get(registro.new_state, registro.new_state),
        "motivo": registro.reason,
        "mudancas": _mudancas(tipo, detalhe),
        "pessoa": "",
        "papel": "",
    }
    depois = detalhe.get("depois") if isinstance(detalhe.get("depois"), dict) else {}
    if tipo == "Unidade":
        linha["sobre"] = depois.get("nome") or nome_da_unidade
        if "trocas_excluidas" in detalhe:
            linha["motivo"] = _exclusao_do_piloto(detalhe)
    elif tipo == "AutoridadeHabilitada":
        # O motivo da autoridade é o rótulo dela — nome, cargo e ato de nomeação no instante do ato
        # (060) —, e por isso vai para "sobre o quê", e não entre aspas como se alguém o tivesse
        # dito.
        linha["sobre"], linha["motivo"] = registro.reason, ""
    elif tipo == "ModeloDeAviso":
        # Só o nome: o assunto e o corpo do modelo estão no mesmo `detalhe`, e não saem dele.
        linha["sobre"] = depois.get("nome", "")
    elif tipo in ("Aviso", "InterrupcaoDoAviso"):
        linha["sobre"] = editais.get(registro.aggregate_id, "")
    elif tipo == "Vinculo":
        linha["pessoa"] = detalhe.get("pessoa", "")
        papel = detalhe.get("papel", "")
        linha["papel"] = papeis.get(papel, (papel,))[0]
    return linha


def _rotulo_da_operacao(registro):
    """O ato em palavras. O do modelo de aviso sai da situação, porque a operação é uma só (066)."""
    if registro.operation == "AVISO_MODELO":
        antes, depois = registro.previous_state, registro.new_state
        if not antes:
            return "Criação de modelo de aviso"
        if antes == "ATIVO" and depois == "INATIVO":
            return "Inativação de modelo de aviso"
        if antes == "INATIVO" and depois == "ATIVO":
            return "Reativação de modelo de aviso"
        return "Edição de modelo de aviso"
    return OPERACOES.get(registro.operation, registro.operation)


def _mudancas(tipo, detalhe):
    """Os dados que mudaram, com antes e depois — só os públicos da unidade e da autoridade."""
    campos = CAMPOS_LEGIVEIS.get(tipo)
    antes, depois = detalhe.get("antes"), detalhe.get("depois")
    if not campos or not isinstance(antes, dict) or not isinstance(depois, dict):
        return []
    return [
        {"dado": rotulo, "antes": _valor(antes.get(campo)), "depois": _valor(depois.get(campo))}
        for campo, rotulo in campos.items()
        if antes.get(campo) != depois.get(campo)
    ]


def _valor(valor):
    if valor is None or valor == "":
        return "—"
    if isinstance(valor, bool):
        return "Ativa" if valor else "Desativada"
    if isinstance(valor, list):
        return " / ".join(str(parte) for parte in valor)
    if isinstance(valor, str) and len(valor) == 10 and valor[4] == "-" and valor[7] == "-":
        try:
            return date.fromisoformat(valor).strftime("%d/%m/%Y")
        except ValueError:
            return valor
    return str(valor)


def _exclusao_do_piloto(detalhe):
    quantas = detalhe.get("trocas_excluidas", 0)
    relatorio = _valor(detalhe.get("relatorio_final_em"))
    plural = "registro excluído" if quantas == 1 else "registros excluídos"
    return f"{quantas} {plural}; relatório final de {relatorio}."
