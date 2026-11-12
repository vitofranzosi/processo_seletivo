"""A vaga reservada sem quem a ocupe, lida pelas três telas e pelo ato (155, R-004, R-008).

**Por que mora na interface.** A condição é da ocupação (`ocupacao/domain/destinacao.py`), mas três
dos fatos que a impedem não são: o resultado do marco e o prazo de recurso são da divulgação, os
recursos pendentes são dos recursos, e quem foi chamado para a vaga é da condução. A ocupação não
importa a condução (`tests/test_dependencia_da_ocupacao.py`, `test_dependencia_da_convocacao.py`),
e o acréscimo da `097` já resolveu a mesma fronteira com um *callable* injetado. Este módulo é quem
o compõe — para a tela, que o lê uma vez, e para o ato, que o lê de novo sob a trava.

**Os fatos de cada marco são lidos uma vez** (155, R-008; FR-4686 da `135`): o detalhe do Edital tem
custo fixo por Edital, e a `Composicao` guarda o que já leu. O que é por recorte — as chamadas da
lista — é lido por recorte, e o número de recortes é o do quadro, e não o de inscritos.

**Uma frase só para as três telas** (155, D-004, UX-600): a ocupação, o Centro e a convocação dizem
a situação com as mesmas palavras, e a frase nomeia a lista, a quantidade e o que o Edital declara.
Nenhuma delas diz que alguém foi convocado, aceitou ou se matriculou (FR-6344): a chamada é "pessoa
chamada para esta vaga".
"""

from processo_seletivo.ocupacao.domain import destinacao as conta
from processo_seletivo.ocupacao.domain import nomes


class Composicao:
    """Os fatos externos de um Edital, guardados por marco e por recorte enquanto a tela é montada.

    É o *callable* que o ato e a leitura recebem como `fatos_externos`. Uma instância por pedido: o
    ato cria a dele sob a trava, e a guarda não sobrevive ao pedido que a criou.
    """

    def __init__(self, *, at=None):
        self.at = at
        self._do_marco = {}
        self._da_lista = {}

    def __call__(
        self,
        *,
        edital,
        perfil_id,
        marco_id,
        lista_id,
        etapa_governada_id=None,
        eliminados=(),
        at=None,
    ):
        momento = at or self.at
        marco = self._marco(edital, perfil_id, marco_id, momento)
        lista = self._lista(edital, perfil_id, marco_id, lista_id, momento)
        eliminacao = (
            self._eliminacao(edital, perfil_id, etapa_governada_id, eliminados, momento)
            if eliminados and etapa_governada_id
            else {}
        )
        return {
            "natureza_do_resultado": lista["natureza"],
            "prazo_recursal_ate": lista["prazo"],
            "recursos_pendentes": marco["recursos"],
            **eliminacao,
            "chamadas_em_curso": lista["chamadas"],
            "chamados": lista["chamados"],
        }

    # --- o que é do marco: os recursos sobre ele ---------------------------------------------

    def _marco(self, edital, perfil_id, marco_id, at):
        chave = (str(perfil_id), str(marco_id))
        if chave not in self._do_marco:
            from processo_seletivo.divulgacao.models import PublicacaoResultado
            from processo_seletivo.recursos.application import selectors as recursos

            conteudo = _marco_publicado(edital, perfil_id, marco_id, at)
            publicacoes = list(
                PublicacaoResultado.objects.filter(edital=edital, marco_id=marco_id).values_list(
                    "id", flat=True
                )
            )
            pendentes = (
                recursos.recursos_pendentes_do_marco(
                    edital=edital,
                    marco_id=marco_id,
                    marco=conteudo,
                    publicacoes_do_marco=publicacoes,
                )
                if publicacoes
                else []
            )
            self._do_marco[chave] = {"conteudo": conteudo, "recursos": len(pendentes)}
        return self._do_marco[chave]

    # --- o que é da lista: o resultado, o prazo e as chamadas ---------------------------------

    def _lista(self, edital, perfil_id, marco_id, lista_id, at):
        chave = (str(perfil_id), str(marco_id), str(lista_id) if lista_id else None)
        if chave not in self._da_lista:
            from processo_seletivo.divulgacao.application.selectors import vigente_do_marco
            from processo_seletivo.divulgacao.domain.publicabilidade import janela_aberta_ate

            marco = self._marco(edital, perfil_id, marco_id, at)
            vigente = vigente_do_marco(edital=edital, marco_id=marco_id, lista_id=lista_id)
            prazo = (
                janela_aberta_ate(
                    edital=edital,
                    marco_id=marco_id,
                    marco=marco["conteudo"],
                    at=at,
                    lista_id=lista_id,
                )
                if vigente is not None
                else None
            )
            chamadas, chamados = _chamadas_em_curso(edital, perfil_id, marco_id, lista_id)
            self._da_lista[chave] = {
                "natureza": vigente.natureza if vigente is not None else None,
                "prazo": prazo,
                "chamadas": chamadas,
                "chamados": chamados,
            }
        return self._da_lista[chave]

    # --- o que é da eliminação na Etapa que o corte governa ------------------------------------

    def _eliminacao(self, edital, perfil_id, etapa_id, eliminados, at):
        """O prazo e os recursos contra a eliminação de quem está na ordem da reserva (FR-6306).

        **A janela é a que a interposição aplica ao Resultado da Etapa** (`recursos/interpor.py`):
        a do resultado vigente de cada marco que enumera a Etapa, e a da publicação preliminar da
        análise das inscrições, quando é desta Etapa. Vale a que fecha por último, pela razão de
        lá — prazo que restringe direito interpreta-se a favor de quem recorre.
        """
        from django.utils import timezone

        from processo_seletivo.divulgacao.domain.publicabilidade import janela_aberta_ate
        from processo_seletivo.divulgacao.models import PublicacaoDasInscricoes
        from processo_seletivo.recursos.application import selectors as recursos
        from processo_seletivo.recursos.models import Recurso

        momento = at or timezone.now()
        conteudo = _conteudo(edital, at)
        prazos = []
        for perfil in conteudo.get("profiles") or []:
            if str(perfil.get("id")) != str(perfil_id):
                continue
            for marco in perfil.get("classificationMilestones") or []:
                if str(etapa_id) not in {str(e) for e in marco.get("stages") or []}:
                    continue
                fecha = janela_aberta_ate(
                    edital=edital, marco_id=marco.get("id"), marco=marco, at=momento
                )
                if fecha is not None:
                    prazos.append(fecha)
        preliminares = list(
            PublicacaoDasInscricoes.objects.filter(
                edital=edital, etapa_id=etapa_id, natureza="PRELIMINAR"
            ).order_by("publicado_em")
        )
        if preliminares:
            ultimo = preliminares[-1]
            if ultimo.admite_recurso and ultimo.recurso_ate and momento <= ultimo.recurso_ate:
                prazos.append(ultimo.recurso_ate)
        pendentes = recursos.recursos_pendentes_da_etapa(edital=edital, etapa_id=etapa_id)
        # Só os recursos de quem está eliminado na ordem desta lista: o de outra pessoa da Etapa não
        # devolve ninguém a esta reserva.
        contra = (
            Recurso.objects.filter(pk__in=pendentes, inscricao_id__in=list(eliminados)).count()
            if pendentes
            else 0
        )
        return {
            "prazo_da_eliminacao_ate": max(prazos) if prazos else None,
            "recursos_da_eliminacao": contra,
        }


def _conteudo(edital, at):
    from processo_seletivo.publicacoes.application.selectors import effective_version

    return effective_version(edital_id=edital.id, at=at).content or {}


def _marco_publicado(edital, perfil_id, marco_id, at):
    for perfil in _conteudo(edital, at).get("profiles") or []:
        if str(perfil.get("id")) != str(perfil_id):
            continue
        for marco in perfil.get("classificationMilestones") or []:
            if str(marco.get("id")) == str(marco_id):
                return marco
    return {}


def _chamadas_em_curso(edital, perfil_id, marco_id, lista_id):
    """As pessoas da lista chamadas para a vaga e sem desfecho — `([{rotulo, ate}], [inscrição])`.

    **Uma consulta para o recorte**, com os desfechos e as sucessoras em `prefetch`, e uma para os
    nomes. A sucedida foi corrigida, e só a vigente responde pela vaga.
    """
    from processo_seletivo.convocacao.application import selectors as conducao

    abertas = [
        c
        for c in conducao.vigentes(
            conducao.convocacoes_do_recorte(
                edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
            )
        )
        if conducao.desfecho_de(c) is None
    ]
    if not abertas:
        return [], []
    identidades = conducao.identidades_de({c.inscricao_id for c in abertas})
    chamadas = [
        {
            "rotulo": " — ".join(
                parte
                for parte in (
                    (identidades.get(c.inscricao_id) or {}).get("protocolo"),
                    (identidades.get(c.inscricao_id) or {}).get("nome"),
                )
                if parte
            ),
            "ate": c.vencimento,
        }
        for c in abertas
    ]
    return chamadas, [c.inscricao_id for c in abertas]


# --- A situação de cada recorte ------------------------------------------------------------------


def situacao_do_recorte(
    *, edital, perfil_id, marco_id, lista_id, rotulo="", at=None, composicao=None
):
    """A leitura da vaga do recorte e a frase de UX-600, ou `None` onde a tela não diz nada novo.

    **Só a reversão por esgotamento ganha frase nesta entrega.** Sob a por saldo a tela continua
    como estava (155, R-010); o Edital silente e a linha geral ganham a declaração de não
    preenchida no incremento seguinte, e a passagem entre cotas já tem a frase dela nas prévias.
    """
    from processo_seletivo.ocupacao.application.destinacao import leitura_da_vaga

    if lista_id is None:
        return None
    leitura = leitura_da_vaga(
        edital=edital,
        perfil_id=perfil_id,
        marco_id=marco_id,
        lista_id=lista_id,
        fatos_externos=composicao if composicao is not None else Composicao(at=at),
        at=at,
    )
    if leitura["declaracao"] != nomes.REVERSAO_POR_ESGOTAMENTO:
        return None
    situacao = leitura["situacao"]
    frase = frase_da_situacao(leitura, rotulo)
    if not frase:
        return None
    return {
        **situacao,
        "frase": frase,
        "impedimentos": [
            {"codigo": i.codigo, "frase": _com_data(i), "ate": i.ate}
            for i in situacao["impedimentos"]
        ],
        "declarada": leitura["frase"],
        "disponivel": situacao["estado"] == conta.DESTINACAO_DISPONIVEL,
        "movimentos": [
            m
            for m in leitura["movimentos"]
            if m.especie == nomes.MOVIMENTO_REVERSAO
            and m.origem_lista_id is not None
            and str(m.origem_lista_id) == str(lista_id)
        ],
    }


def anotar_recortes(*, edital, perfil_id, marco_id, recortes, at=None):
    """A situação da vaga em cada recorte da ocupação, com uma composição para o marco inteiro.

    `recorte["vaga"]` fica `None` onde a tela não diz nada novo. Só o recorte apurado pergunta: sem
    apuração não há vaga a ocupar afirmada, e a leitura custaria consultas para dizer nada.
    """
    composicao = Composicao(at=at)
    for recorte in recortes:
        recorte["vaga"] = (
            situacao_do_recorte(
                edital=edital,
                perfil_id=perfil_id,
                marco_id=marco_id,
                lista_id=recorte.get("listaId"),
                rotulo=recorte.get("rotulo") or "",
                at=at,
                composicao=composicao,
            )
            if recorte.get("listaId") and recorte.get("apuracao") is not None
            else None
        )
    return recortes


def rotulo_do_recorte(conteudo, perfil_id, lista_id):
    """O nome da lista como a ocupação o diz — o da derivação de `editais/domain/recortes.py`."""
    from processo_seletivo.editais.domain.recortes import recortes_do_perfil

    alvo = str(lista_id) if lista_id else None
    return next(
        (
            rotulo
            for identificador, rotulo in recortes_do_perfil(conteudo, perfil_id=perfil_id)
            if (str(identificador) if identificador else None) == alvo
        ),
        "",
    )


def frase_da_situacao(leitura, rotulo):
    """A frase de UX-600: a lista, a quantidade e o que o Edital declara, em palavras.

    Sem código de espécie nem identificador. Vazia onde nada há a dizer — a reserva que ainda tem
    quem a ocupe segue o caminho da fila, e a tela já o diz.
    """
    situacao = leitura["situacao"]
    lista = rotulo or "esta lista"
    declara = f" O Edital declara: «{leitura['frase']}»" if leitura["frase"] else ""
    estado = situacao["estado"]
    if estado == conta.DESTINACAO_DISPONIVEL:
        quantidade = situacao["quantidade"]
        return (
            f"{_vagas(quantidade)} da {lista} sem quem a{'s' if quantidade != 1 else ''} ocupe: "
            f"ninguém mais na ordem desta lista pode ocupá-la{'s' if quantidade != 1 else ''}."
            + declara
        )
    if estado == conta.IMPEDIDA:
        motivos = "; ".join(_com_data(i) for i in situacao["impedimentos"])
        return (
            f"{_vagas(leitura.get('saldo') or 0)} da {lista} a ocupar, e a destinação à ampla "
            f"concorrência ainda não cabe: {motivos}." + declara
        )
    if estado == conta.SEM_VAGA_A_DESTINAR and situacao["destinadas"] and not leitura.get("saldo"):
        # **O movimento antigo conta como destinação feita** (US1.5, FR-6316): a tela o cita, e
        # nenhum ato a destina de novo.
        return (
            f"{_vagas(situacao['destinadas'])} da {lista} já "
            + ("foi destinada" if situacao["destinadas"] == 1 else "foram destinadas")
            + " à ampla concorrência."
        )
    return ""


def _vagas(quantidade):
    return f"{quantidade} vaga" if quantidade == 1 else f"{quantidade} vagas"


def _com_data(impedimento):
    from processo_seletivo.shared.tempo import ZONA

    if impedimento.ate is None:
        return impedimento.frase
    return (
        f"{impedimento.frase}, até {impedimento.ate.astimezone(ZONA).strftime('%d/%m/%Y às %Hh%M')}"
    )


__all__ = [
    "Composicao",
    "anotar_recortes",
    "frase_da_situacao",
    "rotulo_do_recorte",
    "situacao_do_recorte",
]
