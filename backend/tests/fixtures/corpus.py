"""O corpus da 070 nos testes: o conteúdo publicado, lido da cópia, e republicado pelo fluxo real.

**Duas camadas** (`specs/070-fonte-de-consulta-do-edital/research.md`, `R-016`; `FR-1450`).

- **Conteúdo.** O domínio da fonte de consulta é puro: recebe o conteúdo e devolve a resposta.
  `conteudo()` lê os bytes canônicos que o fluxo real publicou em 11/10/2026
  (`corpus_070/LEIA-ME.md`).
- **Banco.** O que depende de versão, fronteira de vigência, origem e desfecho só existe com as
  linhas de `publicacoes`. `publicar_do_corpus()` republica o mesmo conteúdo pelos comandos reais
  — rascunho, submissão, homologação, publicação e cada Retificação —, com as datas deslocadas.

**Por que deslocar.** O corpus tem datas de outubro e novembro de 2026, e a `028` recusa publicar
Edital cujo período de inscrições já terminou. Deslocar tudo pelo mesmo intervalo preserva o que os
casos afirmam — quem vem antes de quem, quantos dias de vigência futura — e não depende do dia em
que a suíte roda.
"""

import copy
import json
import re
from datetime import datetime, timedelta
from pathlib import Path

import pytest
from django.utils import timezone
from django.utils.dateparse import parse_datetime

from processo_seletivo.editais.application.requerimento import (
    atualizar_requerimento_de_matricula,
)
from processo_seletivo.editais.application.teto import atualizar_teto_de_inscricoes
from processo_seletivo.editais.domain import secoes, validation
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada
from processo_seletivo.seguranca.domain import Actor
from tests.fixtures.anexos import criar_anexo
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import create_retification, levar_a_publicacao, publish_retification

PASTA = Path(__file__).resolve().parent / "corpus_070"
EDITAIS = ("01", "91", "92")

#: A véspera da publicação do corpus. Deslocar a partir daqui leva o primeiro instante do corpus
#: para depois de agora, que é o que a publicação exige.
REFERENCIA = datetime.fromisoformat("2026-10-11T00:00:00+00:00")

INSTANTE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d{1,6})?[+-]\d{2}:\d{2}$")


def conteudo(edital, publicacao):
    """O conteúdo da versão consolidada depois da publicação `publicacao` (1, 2 ou 3)."""
    return json.loads(
        (PASTA / f"edital-{edital}-2026" / f"pub{publicacao}-canonico.json").read_text()
    )


def alteracoes(edital, publicacao):
    """As alterações da Retificação `publicacao`, no formato do estudo: `path`, `op`, `novo`."""
    return json.loads(
        (PASTA / f"edital-{edital}-2026" / f"pub{publicacao}-alteracoes.json").read_text()
    )


def publicacoes_do(edital):
    """Quantas publicações o Edital tem no corpus: a original e as Retificações."""
    return len(list((PASTA / f"edital-{edital}-2026").glob("pub*-canonico.json")))


def deslocamento_ate_agora(margem=timedelta(days=1)):
    """Quanto somar às datas do corpus para que a véspera dele caia em `agora + margem`."""
    return timezone.now() + margem - REFERENCIA


def deslocar(valor, deslocamento):
    """Soma `deslocamento` a todo instante do valor, na mesma forma em que ele estava escrito.

    Percorre o valor inteiro, e não campos nomeados: o instante aparece no cronograma, no método do
    sorteio e no valor novo de uma Retificação, e uma lista de campos esqueceria o próximo.
    """
    if isinstance(valor, dict):
        return {chave: deslocar(item, deslocamento) for chave, item in valor.items()}
    if isinstance(valor, list):
        return [deslocar(item, deslocamento) for item in valor]
    if isinstance(valor, str) and INSTANTE.match(valor):
        return (parse_datetime(valor) + deslocamento).isoformat()
    return valor


def _sem_nulos(valor):
    """O conteúdo publicado escreve a ausência como `null`; o rascunho a recusa em alguns campos.

    Em todos eles, ausente e nulo dizem o mesmo — é a regra de `elevar` e do snapshot —, e por isso
    tirar a chave não muda o que se publica. O ensaio da 070 (T004) prova que não muda.
    """
    if isinstance(valor, dict):
        return {chave: _sem_nulos(item) for chave, item in valor.items() if item is not None}
    if isinstance(valor, list):
        return [_sem_nulos(item) for item in valor]
    return valor


def rascunho_do_conteudo(publicado, deslocamento):
    """O conteúdo publicado como rascunho: a forma é a mesma (`replace_draft`, 070 `R-016`).

    Só as seções **textuais preenchidas** entram, porque é só o que a etapa de conteúdo grava; as
    geradas o snapshot recompõe pelo catálogo.
    """
    c = deslocar(copy.deepcopy(publicado), deslocamento)
    rascunho = {
        "profiles": _sem_nulos(c["profiles"]),
        "schedule": c["schedule"],
        "stages": c.get("stages") or [],
        "sections": [
            {"key": secao["key"], "content": secao["content"]}
            for secao in c.get("sections") or []
            if secao.get("type") == "TEXT" and secao.get("content")
        ],
        "documentRequirements": c.get("documentRequirements") or [],
    }
    if c.get("drawMethod"):
        rascunho["drawMethod"] = c["drawMethod"]
    return rascunho


ELABORADOR = Actor("preparador", "cefor", frozenset({"edital:elaborar"}))


def publicar_do_corpus(
    api_client,
    nome,
    *,
    ate=None,
    deslocamento=None,
    chave=None,
    mudar=None,
    catalogo_vigente=False,
):
    """Publica o Edital `nome` do corpus pelo fluxo real e aplica as Retificações até a `ate`.

    `mudar` recebe uma cópia do conteúdo original e a altera antes do rascunho: é como os casos que
    o corpus não tem — dois canais de dúvida, um anexo citado que não existe — chegam ao banco pelo
    mesmo caminho dos outros. Com `mudar`, as Retificações do corpus não são aplicadas.

    `catalogo_vigente` publica com o catálogo de hoje, como nasce todo Edital novo depois da `069`,
    em vez do da `054`, em que o corpus nasceu.

    Devolve `(edital, deslocamento)`: os casos precisam do deslocamento para falar das datas.
    """
    deslocamento = deslocamento if deslocamento is not None else deslocamento_ate_agora()
    # As reservas de idempotência exigem de 16 a 128 caracteres.
    chave = f"corpus-{chave or nome}-chave"
    original = conteudo(nome, 1)
    if mudar is not None:
        original = copy.deepcopy(original)
        mudar(original)
        ate = 1
    criado = api_client.post(
        "/api/v1/admin/processos",
        {
            "institutionalCode": f"{original['processoCode']}-{chave}"[:60],
            "title": original["processoTitle"],
            "firstEdital": {
                "number": original["number"],
                "year": original["year"],
                "title": original["title"],
                "description": original.get("description") or "",
            },
        },
        format="json",
        **actor_headers(
            "gestor-a",
            ["processo:criar", "processo:ativar", "edital:criar"],
            key=f"{chave}-processo",
        ),
    )
    assert criado.status_code == 201, criado.content
    edital = Edital.objects.get(processo_id=criado.json()["id"])

    # **Os anexos antes do rascunho**: documento vinculado a anexo leva o identificador dele, e o
    # rascunho recusaria vínculo a anexo que não existe.
    for anexo in original.get("attachments") or []:
        criar_anexo(
            edital,
            identificador=anexo["id"],
            rotulo=anexo["label"],
            order=anexo["order"],
            marca=str(anexo["order"]),
        )

    def teto_e_requerimento(edital):
        # O rascunho acabou de ser gravado pela API: a revisão em memória é a de antes dele.
        edital.refresh_from_db()
        if original.get("maxInscricoesPorCandidato") is not None:
            atualizar_teto_de_inscricoes(
                actor=ELABORADOR,
                edital_id=edital.id,
                expected_revision=edital.revision,
                teto=original["maxInscricoesPorCandidato"],
            )
            edital.refresh_from_db()
        if original.get("matriculationRequest"):
            atualizar_requerimento_de_matricula(
                actor=ELABORADOR,
                edital_id=edital.id,
                expected_revision=edital.revision,
                momento=original["matriculationRequest"]["moment"],
                declaracao=original["matriculationRequest"]["declarationText"],
            )
            edital.refresh_from_db()

    # **Os Editais do corpus nasceram no catálogo da `054`**, antes da `069`: os títulos e a ordem
    # das seções são os dele, e os parágrafos trazem a numeração digitada daquele documento ("4.1").
    # Publicados com o catálogo vigente, o snapshot levaria os títulos da `069` e a apresentação por
    # perguntas, que renumera as seções — e a numeração digitada do 92/2026 vira conflito impeditivo
    # (065). O catálogo se troca só na publicação original, como em
    # `tests/integration/publicacoes/test_retificacao_de_edital_antigo.py`: a Retificação confere a
    # topologia pelo Edital publicado, e não pelo catálogo.
    with pytest.MonkeyPatch.context() as antes_da_069:
        if not catalogo_vigente:
            antes_da_069.setattr(secoes, "CATALOGO", secoes.CATALOGO_DA_054)
            antes_da_069.setattr(validation, "CATALOGO", secoes.CATALOGO_DA_054)
        edital = levar_a_publicacao(
            api_client,
            edital,
            draft=rascunho_do_conteudo(original, deslocamento),
            antes_de_submeter=teto_e_requerimento,
            chave=f"{chave}-publicacao",
        )

    ultima = publicacoes_do(nome) if ate is None else ate
    for numero in range(2, ultima + 1):
        retificar_do_corpus(api_client, edital, nome, numero, deslocamento, chave=chave)
    return Edital.objects.get(pk=edital.pk), deslocamento


def retificar_do_corpus(api_client, edital, nome, numero, deslocamento, *, chave="corpus"):
    """A Retificação `numero` do corpus, pela API, com a vigência e os valores deslocados.

    **A base é a versão vigente no início da vigência do ato**, e não a mais recente: é como o
    cliente elabora quando já há Retificação de vigência futura publicada (`create_retification`).
    """
    ato = alteracoes(nome, numero)
    vigencia = None
    if ato.get("vigencia") not in (None, "None"):
        vigencia = parse_datetime(ato["vigencia"].replace(" ", "T")) + deslocamento
    momento = vigencia or timezone.now()
    base = (
        VersaoConsolidada.objects.filter(edital=edital, valid_from__lte=momento)
        .order_by("-valid_from", "-materialized_at")
        .first()
    )
    # **A identidade da seção é `uuid5(edital:key)`** (`editais/domain/secoes.py`): o Edital
    # republicado tem outro identificador, e as suas seções, outras identidades. O caminho é
    # remapeado pela chave, que é o que a identidade codifica.
    chave_da_secao = {secao["id"]: secao["key"] for secao in conteudo(nome, 1)["sections"]}
    secao_da_chave = {secao["key"]: secao["id"] for secao in base.content["sections"]}

    def caminho(original):
        for antigo, chave_secao in chave_da_secao.items():
            original = original.replace(f"id={antigo}", f"id={secao_da_chave[chave_secao]}")
        return original

    mudancas = [
        {
            "targetPath": caminho(item["path"]),
            "operation": item["op"],
            **(
                {"newValue": deslocar(item["novo"], deslocamento)} if item["op"] != "REMOVE" else {}
            ),
        }
        for item in ato["alteracoes"]
    ]
    retificacao = create_retification(
        api_client,
        edital,
        mudancas,
        effective_at=vigencia.isoformat() if vigencia else None,
        base=base,
        suffix=f"{chave}-{numero}",
    )
    return publish_retification(api_client, retificacao, suffix=f"{chave}-{numero}")


# ---- a camada de conteúdo: o contexto da resposta, sem banco ---------------------------------

#: O corpus foi publicado em 11/10/2026; a ordem das publicações é a dos arquivos. A hora é
#: indiferente para os casos, desde que preserve a ordem.
PUBLICADO_EM = datetime.fromisoformat("2026-10-11T12:00:00-03:00")


def _atos_do_corpus(nome):
    """`AtoPublicado` de cada publicação do corpus, com a vigência e o que o documento contém.

    No corpus cada Retificação foi elaborada sobre a versão mais recente, e por isso o documento
    dela contém todas as anteriores — o cenário do achado de 12/10 não está no corpus; está nos
    testes de integração que o constroem.
    """
    from processo_seletivo.duvidas.domain.estruturas import ORIGINAL, RETIFICACAO, AtoPublicado

    atos = []
    for numero in range(1, publicacoes_do(nome) + 1):
        publicado = PUBLICADO_EM + timedelta(minutes=numero)
        vigente = publicado
        if numero > 1:
            vigencia = alteracoes(nome, numero).get("vigencia")
            if vigencia not in (None, "None"):
                vigente = parse_datetime(vigencia.replace(" ", "T"))
        atos.append(
            AtoPublicado(
                publicacao_id=f"{nome}-pub{numero}",
                ato=ORIGINAL if numero == 1 else RETIFICACAO,
                ordem=numero,
                publicado_em=publicado,
                vigente_desde=vigente,
                documento=f"/api/v1/public/publicacoes/{nome}-pub{numero}/documento",
                contem=tuple(f"{nome}-pub{anterior}" for anterior in range(1, numero + 1)),
            )
        )
    return atos


def _proveniencias(nome, atos):
    pares = []
    for ato in atos:
        if ato.ordem == 1:
            continue
        for item in alteracoes(nome, ato.ordem)["alteracoes"]:
            pares.append((item["path"], ato.publicacao_id))
    return tuple(pares)


def contexto_do_corpus(
    nome,
    instante,
    *,
    desfecho=None,
    canal_institucional="",
    versao_anterior=None,
    conteudo_substituto=None,
):
    """O `Contexto` da resposta no instante dado, montado só com o corpus (camada de conteúdo).

    A versão vigente é a última publicação cuja vigência já começou; as de vigência futura entram
    como `futuras`. `conteudo_substituto` troca o conteúdo vigente por um sintético, para os casos
    que o corpus não tem (dois canais, anexo inexistente, negativa declarada).
    """
    from processo_seletivo.duvidas.domain.estruturas import (
        Contexto,
        VersaoConsultada,
        VersaoFutura,
    )

    todos = _atos_do_corpus(nome)
    em_ordem = sorted(todos, key=lambda ato: (ato.vigente_desde, ato.ordem))
    aplicados = [ato for ato in em_ordem if ato.vigente_desde <= instante]
    assert aplicados, "o instante é anterior à primeira publicação do corpus"
    ultimo = max(aplicados, key=lambda ato: ato.ordem)
    vigente = (
        conteudo_substituto if conteudo_substituto is not None else conteudo(nome, ultimo.ordem)
    )

    futuras = []
    for ato in em_ordem:
        if ato.vigente_desde > instante:
            aplicados_ate = [item for item in em_ordem if item.vigente_desde <= ato.vigente_desde]
            futuras.append(
                VersaoFutura(
                    vigente_desde=ato.vigente_desde,
                    conteudo=conteudo(nome, ato.ordem),
                    atos=tuple(aplicados_ate),
                    proveniencias=_proveniencias(nome, aplicados_ate),
                )
            )

    versao = VersaoConsultada(
        id=f"{nome}-v{ultimo.ordem}",
        identificador_curto=f"{nome}v{ultimo.ordem}".ljust(12, "0"),
        vigente_desde=max(ato.vigente_desde for ato in aplicados),
        publicada_em=todos[0].publicado_em,
        retificacoes=tuple(
            (ato.publicado_em, ato.vigente_desde) for ato in aplicados if ato.ordem > 1
        ),
    )
    anterior_aplicados = ()
    if versao_anterior is not None:
        # A versão "vN" aplica o que já vigorava quando o ato N passou a vigorar, como no banco:
        # pela vigência, e não pela ordem de publicação.
        numero = int(versao_anterior.rsplit("v", 1)[1])
        fronteira = next(ato for ato in todos if ato.ordem == numero).vigente_desde
        anterior_aplicados = tuple(ato for ato in em_ordem if ato.vigente_desde <= fronteira)
    return Contexto(
        edital_id=f"edital-{nome}",
        numero=vigente.get("number", ""),
        ano=vigente.get("year", 0),
        titulo=vigente.get("title", ""),
        instante=instante,
        versao=versao,
        conteudo=vigente,
        atos=tuple(aplicados),
        proveniencias=_proveniencias(nome, aplicados),
        fonte_da_versao=ultimo,
        futuras=tuple(futuras),
        desfecho=desfecho,
        canal_institucional=canal_institucional,
        pagina_publica=f"/selecoes/edital-{nome}/",
        anexos_publicos={
            str(anexo.get("artifactId")): f"/api/v1/public/anexos/{anexo.get('artifactId')}"
            for anexo in vigente.get("attachments") or []
            if anexo.get("artifactId")
        },
        versao_anterior=versao_anterior,
        atos_da_versao_anterior=anterior_aplicados,
    )
