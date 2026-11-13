"""Os Editais da auditoria de UX da Retificação, para os testes da `123` (R-011).

Dois portes, os mesmos da auditoria de 05/11/2026 (`doc/auditoria-ux-retificacao-2026-11-05/`):

- **o de demonstração**: o rascunho máximo da suíte (`rascunho_completo`), com três Perfis — um
  deles com Modalidades, quadro completo, marco com janela recursal e método de sorteio —, Etapas,
  Documentos, dois Anexos e as Seções do catálogo. É o que tem de tudo um pouco, como o 01/2026 do
  `seed_demo`, e publica pelos mesmos helpers que a suíte inteira usa;
- **o ampliado**: o mesmo conteúdo com o Perfil principal copiado até quatro e o Cronograma
  estendido a onze Eventos — o porte dos Editais 57 e 59/2026, que o script de captura da auditoria
  obtinha trocando `conteudo_base` em memória. Aqui a ampliação é **no rascunho, antes de
  publicar**: a tela, a conferência e o banco veem um Edital de verdade.

O `seed_demo` não serve: não roda na suíte, as datas são relativas e o elenco colide.
"""

import json
from datetime import timedelta
from uuid import NAMESPACE_URL, uuid5

from django.utils import timezone

from processo_seletivo.interface import retificacao as retificacao_ui
from processo_seletivo.publicacoes.models_retificacao import Retificacao, VersaoConsolidada
from tests.fixtures.edital import actor_headers
from tests.fixtures.publicacao import (
    create_retification,
    levar_a_publicacao,
    publish_original,
    retify,
)
from tests.fixtures.snapshot import evento, rascunho_completo

PERFIS_DO_AMPLIADO = 4
EVENTOS_DO_AMPLIADO = 11


def _identidades(no, acumulado):
    """Toda identidade declarada sob a chave `id`, em qualquer profundidade."""
    if isinstance(no, dict):
        if isinstance(no.get("id"), str):
            acumulado.add(no["id"])
        for valor in no.values():
            _identidades(valor, acumulado)
    elif isinstance(no, list):
        for valor in no:
            _identidades(valor, acumulado)
    return acumulado


def rascunho_ampliado():
    """O rascunho máximo com quatro Perfis e onze Eventos.

    As cópias do Perfil trocam **toda** identidade declarada dentro dele — Modalidades, linhas do
    quadro, marco, critérios —, e a troca é textual, como no script da auditoria, para que as
    referências internas (a ampla do Perfil, a Modalidade de cada linha) acompanhem. As identidades
    novas são `uuid5`, reproduzíveis: o teste que falha aponta para a mesma cópia.
    """
    base = rascunho_completo()
    modelo = base["profiles"][0]
    for copia in range(2, PERFIS_DO_AMPLIADO + 1):
        texto = json.dumps(modelo)
        for velha in _identidades(modelo, set()):
            texto = texto.replace(velha, str(uuid5(NAMESPACE_URL, f"ampliado:{copia}:{velha}")))
        perfil = json.loads(texto)
        perfil["code"] = f"CURSO-{copia}"
        perfil["name"] = f"Curso de Aperfeiçoamento {copia}"
        base["profiles"].insert(copia - 1, perfil)
    ultimo = base["schedule"][-1]
    for ordem in range(len(base["schedule"]) + 1, EVENTOS_DO_AMPLIADO + 1):
        novo = evento(
            str(uuid5(NAMESPACE_URL, f"ampliado:evento:{ordem}")),
            f"Evento {ordem}",
            ordem,
            ultimo["startAt"],
        )
        novo["description"] = f"Evento sintético {ordem}"
        base["schedule"].append(novo)
    # **Identidades próprias do Edital inteiro**, e não só das cópias: dois Editais não podem
    # declarar a mesma identidade de entidade, e o ampliado precisa caber no mesmo caso que o de
    # demonstração. A troca textual leva junto as referências (o Documento restrito ao Perfil, o
    # marco que enumera a Etapa).
    texto = json.dumps(base)
    for velha in _identidades(base, set()):
        texto = texto.replace(velha, str(uuid5(NAMESPACE_URL, f"ampliado:edital:{velha}")))
    return json.loads(texto)


def publicar_edital_da_auditoria(api_client, manager_headers, process_payload):
    edital = publish_original(
        api_client, manager_headers, process_payload, draft=rascunho_completo(), anexos=2
    )
    return edital


def publicar_edital_extenso(api_client, manager_headers, process_payload):
    """O ampliado num Processo e com chaves próprias: cabe no mesmo caso que o de demonstração.

    As reservas de idempotência são por ator, operação e chave; com as do outro, a criação do
    Processo reencenaria a primeira e o rascunho voltaria 409 (o defeito que `_gravar_rascunho`
    registra).
    """
    from processo_seletivo.processos.models import Edital

    criado = api_client.post(
        "/api/v1/admin/processos",
        {
            **process_payload,
            "institutionalCode": "PS-2026-AMPLIADO",
            "firstEdital": {**process_payload["firstEdital"], "number": "57"},
        },
        format="json",
        **{**manager_headers, "HTTP_IDEMPOTENCY_KEY": "ampliado-processo-0001"},
    )
    assert criado.status_code == 201, criado.content
    edital = Edital.objects.get(processo_id=criado.json()["id"])
    return levar_a_publicacao(
        api_client, edital, draft=rascunho_ampliado(), anexos=2, chave="ampliado-publicacao-01"
    )


def versao_mais_recente(edital):
    return VersaoConsolidada.objects.filter(edital=edital).latest("materialized_at")


def formulario(versao, **por_referencia):
    """O POST que a tela Retificar enviaria sem nada tocado, com os campos de `por_referencia`
    trocados (`g3c9="4"`). Os valores saem de `campos_editaveis`, como a tela os desenha."""
    grupos = retificacao_ui.campos_editaveis(versao.content)
    enviados = {"base": str(versao.id), "chave_idempotencia": "ui-teste-123"}
    enviados |= {f"campo:{c['referencia']}": c["valor"] for g in grupos for c in g["campos"]}
    enviados |= {f"campo:{ref}": valor for ref, valor in por_referencia.items()}
    return enviados


def referencia_do_campo(versao, titulo_do_grupo, rotulo):
    """`g3c9` do campo `rotulo` no primeiro grupo cujo título começa por `titulo_do_grupo`."""
    for grupo in retificacao_ui.campos_editaveis(versao.content):
        if grupo["titulo"].startswith(titulo_do_grupo):
            for campo in grupo["campos"]:
                if campo["rotulo"] == rotulo:
                    return campo["referencia"]
    raise LookupError(f"{titulo_do_grupo} · {rotulo}")


def retificacao_futura(api_client, edital, *, dias=14, suffix="futura"):
    """Uma Retificação **publicada** com vigência futura: a nova base ainda não vigora (RU-04)."""
    vigente = versao_mais_recente(edital)
    perfil = vigente.content["profiles"][-1]
    return retify(
        api_client,
        edital,
        [
            {
                "targetPath": f"/profiles/id={perfil['id']}/locality",
                "operation": "REPLACE",
                "newValue": "Serra",
            }
        ],
        effective_at=(timezone.now() + timedelta(days=dias)).isoformat(),
        suffix=suffix,
    )


def retificacao_devolvida(api_client, edital, changes, *, suffix="devolvida"):
    """Uma Retificação submetida e devolvida para elaboração, com motivo (103)."""
    retificacao = create_retification(api_client, edital, changes, suffix=suffix)
    api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/submissoes",
        format="json",
        **{
            **actor_headers("retificador", ["retificacao:submeter"], key=f"{suffix}-sub-0001"),
            "HTTP_IF_MATCH": '"1"',
        },
    )
    devolvida = api_client.post(
        f"/api/v1/admin/retificacoes/{retificacao.id}/devolucoes",
        {"reason": "Confira o quadro de vagas."},
        format="json",
        **{
            **actor_headers("homologador-r", ["retificacao:homologar"], key=f"{suffix}-dev-0001"),
            "HTTP_IF_MATCH": '"2"',
        },
    )
    assert devolvida.status_code < 400, devolvida.content
    retificacao = Retificacao.objects.get(pk=retificacao.pk)
    assert retificacao.status == Retificacao.Status.EM_ELABORACAO
    return retificacao
