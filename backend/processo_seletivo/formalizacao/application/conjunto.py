"""O seletor único: quem está apto para formalização, e o que sai de cada um (117, FR-3674).

**Um seletor, e só um** (FR-3674). A página, a verificação, o pacote e o manifesto leem daqui, e por
isso mostram o mesmo conjunto: se a página mostrasse uma regra e o pacote outra, o setor veria um
documento que não recebe, ou receberia um que não viu.

**Apto é lido na hora** (FR-3669, D-008): o desfecho vigente da convocação vigente da **chamada mais
recente** da inscrição, no Edital, é um dos que incluem — aceite ou regularização. Corrigir o aceite
para indeferimento tira a pessoa da próxima leitura sem ninguém fazer nada (SC-1103). A população da
`031` não serve, porque inclui quem não respondeu.

**O conjunto é a definição vigente aplicada à pessoa** (FR-3670):

- da **convocação**, o item da lista da chamada mais recente, pela apresentação julgada *conforme*
  na conferência vigente, com o hash conferido como esperado; o arquivo se resolve num passo, pela
  `fonte_do_arquivo` da `115`;
- da **inscrição**, o documento enviado, com o hash do envio como esperado, e sem conferência — o
  que a tela e o manifesto dizem (FR-3671, D-022).

O arquivo da inscrição aproveitado por referência num item da convocação sai **uma vez**, pelo item
(FR-3659).

**Em lote, e em número fixo de consultas** (SC-1111): as convocações do Edital numa leitura, as
listas das chamadas pela leitura da `115`, os documentos da inscrição numa consulta, e o histórico
de exportações numa outra. Nada aqui consulta por pessoa.

**Nada aqui lê arquivo.** As situações *indisponível* e *integridade* só se conhecem lendo, e quem
lê é a verificação (`exportar.py`), sobre este mesmo conjunto.
"""

from dataclasses import dataclass, field

from processo_seletivo.convocacao.application import documentos as documentos_da_convocacao
from processo_seletivo.convocacao.application.selectors import desfecho_de
from processo_seletivo.convocacao.domain import nomes as nomes_da_convocacao
from processo_seletivo.convocacao.models import (
    ConferenciaDeDocumento,
    Convocacao,
    ItemDaListaDaConvocacao,
)
from processo_seletivo.editais.domain.documentos import NAO_SE_APLICA as NAO_SE_APLICA_AO_PERFIL
from processo_seletivo.editais.domain.documentos import aplicabilidade
from processo_seletivo.formalizacao.application.definir import (
    _conteudos,
    perfis_do_edital,
    requisitos_do_edital,
)
from processo_seletivo.formalizacao.domain import nomes
from processo_seletivo.formalizacao.models import ExportacaoDeFormalizacao
from processo_seletivo.inscricoes.models import DocumentoSubmetido, Inscricao


@dataclass
class Documento:
    """Um requisito definido, aplicado a uma pessoa, com a situação dele (FR-3672)."""

    requisito_id: str
    chave: str
    nome: str
    momento: str
    ordem: int
    situacao: str
    origem: str = ""
    objeto_id: str = ""
    #: A apresentação ou o documento da inscrição: o agregado dos eventos deste documento.
    objeto: object = None
    #: Quem guarda o arquivo: ela mesma, o documento da inscrição ou a apresentação de origem.
    fonte: object = None
    hash_esperado: str = ""
    tamanho: int = 0
    enviado_em: object = None
    conferido_em: object = None

    @property
    def incluivel(self):
        return self.situacao == nomes.INCLUIDO

    @property
    def da_inscricao(self):
        return self.momento == nomes.DA_INSCRICAO

    @property
    def rotulo(self):
        return nomes.ROTULO_DA_SITUACAO[self.situacao]

    @property
    def sem_conferencia(self):
        return self.incluivel and self.origem == nomes.ORIGEM_DOCUMENTO


@dataclass
class Pessoa:
    """Uma pessoa apta para formalização, com o conjunto dela."""

    inscricao_id: str
    protocolo: str
    nome: str
    perfil_id: str
    perfil_nome: str
    perfil_ordem: int
    convocacao_id: str
    chamada_id: str
    chamada: int
    desfecho: object
    documentos: list = field(default_factory=list)
    ultima_exportacao: dict | None = None

    @property
    def incluiveis(self):
        return [documento for documento in self.documentos if documento.incluivel]

    @property
    def tamanho(self):
        return sum(documento.tamanho for documento in self.incluiveis)

    @property
    def tamanho_legivel(self):
        return tamanho_legivel(self.tamanho)


def tamanho_legivel(tamanho):
    """Em MB com uma casa, ou em KB abaixo de um megabyte, com a vírgula do português."""
    if tamanho < 1024 * 1024:
        return f"{max(1, round(tamanho / 1024))} KB"
    return f"{tamanho / (1024 * 1024):.1f} MB".replace(".", ",")


def _chamadas_mais_recentes(convocacoes):
    """`{inscricao_id: (raiz, vigente)}` da chamada mais recente de cada inscrição.

    A raiz é a convocação que não corrige outra; a vigente, a que ninguém sucedeu na cadeia dela.
    Tudo em memória, sobre a leitura única do Edital.
    """
    sucessora = {c.convocacao_anterior_id: c for c in convocacoes if c.convocacao_anterior_id}
    raizes = {}
    for convocacao in convocacoes:
        if convocacao.convocacao_anterior_id is not None:
            continue
        atual = raizes.get(convocacao.inscricao_id)
        if atual is None or (convocacao.criado_em, str(convocacao.id)) > (
            atual.criado_em,
            str(atual.id),
        ):
            raizes[convocacao.inscricao_id] = convocacao
    resultado = {}
    for inscricao_id, raiz in raizes.items():
        vigente = raiz
        while vigente.id in sucessora:
            vigente = sucessora[vigente.id]
        resultado[inscricao_id] = (raiz, vigente)
    return resultado


def _instante_do_envio(fonte):
    return getattr(fonte, "apresentado_em", None) or getattr(fonte, "uploaded_at", None)


def _da_convocacao(lido, requisito):
    """O documento de um item da lista, pela conferência vigente sobre a apresentação vigente."""
    base = {
        "requisito_id": str(lido.item.requisito_id),
        "chave": requisito.chave if requisito else lido.item.chave,
        "nome": requisito.nome if requisito else lido.nome,
        "momento": nomes.DA_CONVOCACAO,
        "ordem": requisito.ordem if requisito else int(lido.requisito.get("order") or 0),
    }
    if lido.item.situacao == ItemDaListaDaConvocacao.Situacao.NAO_SE_APLICA:
        return Documento(situacao=nomes.NAO_SE_APLICA, **base)
    apresentacao = lido.vigente
    conferencia = lido.conferencia
    if (
        conferencia is not None
        and conferencia.resultado == ConferenciaDeDocumento.Resultado.NAO_SE_APLICA
    ):
        return Documento(situacao=nomes.NAO_SE_APLICA, **base)
    if apresentacao is None:
        return Documento(situacao=nomes.NAO_APRESENTADO, **base)
    if (
        conferencia is None
        or conferencia.resultado != ConferenciaDeDocumento.Resultado.CONFORME
        or conferencia.apresentacao_id != apresentacao.id
    ):
        # A apresentação que chegou depois da conferência não sai: ninguém a julgou (FR-3671).
        return Documento(situacao=nomes.NAO_CONFERIDO, **base)
    fonte = documentos_da_convocacao.fonte_do_arquivo(apresentacao)
    return Documento(
        situacao=nomes.INCLUIDO,
        origem=nomes.ORIGEM_APRESENTACAO,
        objeto_id=str(apresentacao.id),
        objeto=apresentacao,
        fonte=fonte,
        hash_esperado=conferencia.hash_conferido,
        tamanho=fonte.tamanho or 0,
        enviado_em=_instante_do_envio(fonte),
        conferido_em=conferencia.conferido_em,
        **base,
    )


def _da_inscricao(requisito, documento, aplica):
    base = {
        "requisito_id": requisito.id,
        "chave": requisito.chave,
        "nome": requisito.nome,
        "momento": nomes.DA_INSCRICAO,
        "ordem": requisito.ordem,
    }
    if documento is not None:
        return Documento(
            situacao=nomes.INCLUIDO,
            origem=nomes.ORIGEM_DOCUMENTO,
            objeto_id=str(documento.id),
            objeto=documento,
            fonte=documento,
            hash_esperado=documento.content_hash,
            tamanho=documento.tamanho or 0,
            enviado_em=documento.uploaded_at,
            **base,
        )
    if aplica is None:
        return None
    return Documento(situacao=nomes.NAO_APRESENTADO if aplica else nomes.NAO_SE_APLICA, **base)


def _aplicabilidade_na_inscricao(inscricoes):
    """`{(inscricao_id, requisito_id): bool}`: se o requisito da inscrição se aplicava à pessoa.

    Lida da versão que a pessoa aceitou ao enviar, com o Perfil e a Modalidade dela. Uma consulta
    pelas versões, e o cálculo uma vez por combinação.
    """
    from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada

    versoes = {
        versao.id: versao.content
        for versao in VersaoConsolidada.objects.filter(
            id__in={i.versao_aceita_id for i in inscricoes if i.versao_aceita_id}
        ).only("id", "content")
    }
    calculado = {}
    resultado = {}
    for inscricao in inscricoes:
        chave = (inscricao.versao_aceita_id, inscricao.profile_id, inscricao.modality_id)
        if chave not in calculado:
            conteudo = versoes.get(inscricao.versao_aceita_id)
            calculado[chave] = (
                {
                    str(veredito.requisito.get("id")): veredito.situacao != NAO_SE_APLICA_AO_PERFIL
                    for veredito in aplicabilidade(
                        conteudo,
                        profile_id=str(inscricao.profile_id),
                        modality_id=(
                            None if inscricao.modality_id is None else str(inscricao.modality_id)
                        ),
                    )
                }
                if conteudo
                else {}
            )
        for requisito_id, aplica in calculado[chave].items():
            resultado[(inscricao.id, requisito_id)] = aplica
    return resultado


def ultimas_exportacoes(edital, *, autores=True):
    """`{inscricao_id: {"em", "por"}}`: a exportação mais recente que incluiu cada pessoa.

    É o único dado por pessoa que a feature mostra (FR-3701, D-017): um fato, lido do histórico, e
    nunca uma situação de "obtida" ou "recebida".
    """
    from processo_seletivo.seguranca.application.acessos import nomes_dos_autores

    ultimas = {}
    for exportacao in ExportacaoDeFormalizacao.objects.filter(edital=edital).order_by(
        "-exportado_em", "-id"
    ):
        for pessoa in exportacao.incluidas:
            ultimas.setdefault(
                pessoa["inscricao"],
                {"em": exportacao.exportado_em, "por": exportacao.exportado_por},
            )
    if autores and ultimas:
        legiveis = nomes_dos_autores({u["por"] for u in ultimas.values()})
        for ultima in ultimas.values():
            ultima["por"] = legiveis.get(ultima["por"], ultima["por"])
    return ultimas


def aptos(edital, *, definicao, perfis=None, inscricoes=None, com_exportacoes=True):
    """As pessoas aptas do Edital no alcance, com o conjunto de cada uma, na ordem do pacote.

    `perfis` vazio ou `None` é todos os Perfis; `inscricoes`, quando dado, restringe a leitura a
    elas. A ordem é Perfil, nome e protocolo — a mesma da página, do manifesto e do ZIP (SC-1108).
    """
    convocacoes = Convocacao.objects.filter(edital=edital).prefetch_related("desfechos")
    if inscricoes is not None:
        convocacoes = convocacoes.filter(inscricao_id__in=list(inscricoes))
    chamadas = _chamadas_mais_recentes(list(convocacoes))
    cobertos = {str(perfil) for perfil in perfis} if perfis else None
    candidatos = {}
    for inscricao_id, (raiz, vigente) in chamadas.items():
        desfecho = desfecho_de(vigente)
        if desfecho is None or desfecho.especie not in nomes_da_convocacao.DESFECHOS_QUE_INCLUEM:
            continue
        if cobertos is not None and str(vigente.perfil_id) not in cobertos:
            continue
        candidatos[inscricao_id] = (raiz, vigente, desfecho)
    if not candidatos:
        return []
    registros = {
        inscricao.id: inscricao
        for inscricao in Inscricao.objects.filter(id__in=list(candidatos)).only(
            "id", "protocolo", "nome", "profile_id", "modality_id", "versao_aceita_id"
        )
    }
    conteudos = _conteudos(edital)
    perfis_do = {perfil.id: perfil for perfil in perfis_do_edital(edital, conteudos)}
    definidos = {str(r) for r in (definicao.requisitos if definicao else [])}
    requisitos = {r.id: r for r in requisitos_do_edital(edital) if r.id in definidos}
    leituras = {}
    documentos_enviados = {}
    aplica = {}
    if requisitos:
        leituras = documentos_da_convocacao.leituras_por_chamada(
            [raiz for raiz, _, _ in candidatos.values()]
        )
        da_inscricao = [r.id for r in requisitos.values() if r.da_inscricao]
        if da_inscricao:
            for documento in DocumentoSubmetido.objects.filter(
                inscricao_id__in=list(candidatos), requirement_id__in=da_inscricao
            ).only(
                "id",
                "inscricao_id",
                "requirement_id",
                "arquivo",
                "tamanho",
                "content_hash",
                "uploaded_at",
            ):
                documentos_enviados[(documento.inscricao_id, str(documento.requirement_id))] = (
                    documento
                )
            aplica = _aplicabilidade_na_inscricao(list(registros.values()))
    ultimas = ultimas_exportacoes(edital) if com_exportacoes else {}
    pessoas = []
    for inscricao_id, (raiz, vigente, desfecho) in candidatos.items():
        registro = registros[inscricao_id]
        perfil = perfis_do.get(str(vigente.perfil_id))
        documentos = []
        if requisitos:
            da_convocacao = [
                _da_convocacao(lido, requisitos.get(str(lido.item.requisito_id)))
                for lido in getattr(leituras.get(raiz.id), "itens", [])
                if str(lido.item.requisito_id) in requisitos
            ]
            # O arquivo da inscrição que um item incluído aproveita sai uma vez, pelo item.
            aproveitados = {
                str(d.fonte.pk)
                for d in da_convocacao
                if d.incluivel and isinstance(d.fonte, DocumentoSubmetido)
            }
            for requisito in requisitos.values():
                if not requisito.da_inscricao:
                    continue
                enviado = documentos_enviados.get((inscricao_id, requisito.id))
                if enviado is not None and str(enviado.pk) in aproveitados:
                    continue
                documento = _da_inscricao(
                    requisito, enviado, aplica.get((inscricao_id, requisito.id))
                )
                if documento is not None:
                    documentos.append(documento)
            documentos.extend(da_convocacao)
            documentos.sort(key=lambda d: (not d.da_inscricao, d.ordem, d.nome, d.requisito_id))
        pessoas.append(
            Pessoa(
                inscricao_id=str(inscricao_id),
                protocolo=registro.protocolo or str(inscricao_id),
                nome=registro.nome,
                perfil_id=str(vigente.perfil_id),
                perfil_nome=perfil.nome if perfil else "Perfil",
                perfil_ordem=perfil.ordem if perfil else 0,
                convocacao_id=str(vigente.id),
                chamada_id=str(raiz.id),
                chamada=raiz.chamada,
                desfecho=desfecho,
                documentos=documentos,
                ultima_exportacao=ultimas.get(str(inscricao_id)),
            )
        )
    pessoas.sort(key=lambda p: (p.perfil_ordem, p.perfil_nome, p.nome.casefold(), p.protocolo))
    return pessoas
