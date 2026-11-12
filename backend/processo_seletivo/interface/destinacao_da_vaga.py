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
        self._do_sorteio = {}

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

    # --- a lista de sorteio sem relação (155, R-007) ------------------------------------------

    def ausencia_de_concorrente(self, *, edital, perfil_id, marco_id, lista_id, at=None):
        """A ausência de concorrente na lista reservada de sorteio, lida na relação definitiva
        pertinente — `None` quando a pergunta não se coloca (155, D-011, FR-6332, FR-6333).

        `{"comprovada", "frase", "relacao"}`. **Comprovada são três fatos juntos** (R-007): a
        lista não tem inscrito (as inscrições encerradas e ninguém a declarou —
        `sorteios.previa.recortes_sem_inscrito`), a relação vigente da **ampla** do marco existe, e
        nenhum participante dela declarou a lista. Sem a relação da ampla, a lista é "relação não
        congelada", e não lista vazia: ausência de registro não é ausência de concorrente.

        `None` também para a lista que tem relação ou ordem, e para a que alguém declarou: essas
        têm o caminho de sempre, e a tela já diz o que falta nelas.
        """
        if lista_id is None:
            return None
        sorteio = self._sorteio_do_marco(edital, perfil_id, marco_id, at or self.at)
        if sorteio is None or str(lista_id) not in sorteio["semInscrito"]:
            return None
        if sorteio["relacaoDaAmpla"] is None:
            return {
                "comprovada": False,
                "relacao": None,
                "frase": (
                    "Relação não congelada: a relação de habilitados da ampla concorrência deste "
                    "marco ainda não foi congelada, e só ela comprova que ninguém concorre por "
                    "esta lista. Nenhum ato é oferecido antes dela."
                ),
            }
        if str(lista_id) in sorteio["declaradasNaAmpla"]:
            return {
                "comprovada": False,
                "relacao": sorteio["relacaoDaAmpla"],
                "frase": (
                    "A relação da ampla concorrência deste marco tem participante que declarou "
                    "esta lista: a ausência de concorrente não está comprovada, e nenhum ato é "
                    "oferecido."
                ),
            }
        return {"comprovada": True, "relacao": sorteio["relacaoDaAmpla"], "frase": ""}

    def _sorteio_do_marco(self, edital, perfil_id, marco_id, at):
        """Os fatos do sorteio do marco, lidos uma vez: `None` quando o marco não sorteia."""
        chave = (str(perfil_id), str(marco_id))
        if chave not in self._do_sorteio:
            from processo_seletivo.editais.domain import marcos
            from processo_seletivo.sorteios.application.previa import recortes_sem_inscrito
            from processo_seletivo.sorteios.application.selectors import relacao_vigente
            from processo_seletivo.sorteios.models import ParticipanteHabilitado

            conteudo = _conteudo(edital, at)
            if not marcos.marco_ordena_por_sorteio(
                conteudo, perfil_id=perfil_id, marco_id=marco_id
            ):
                self._do_sorteio[chave] = None
                return None
            sem_inscrito = {
                str(lista)
                for lista in recortes_sem_inscrito(
                    edital=edital,
                    conteudo=conteudo,
                    perfil_id=perfil_id,
                    marco_id=marco_id,
                    agora=at,
                )
                if lista
            }
            ampla = (
                relacao_vigente(edital=edital, perfil_id=perfil_id, marco_id=marco_id)
                if sem_inscrito
                else None
            )
            self._do_sorteio[chave] = {
                "semInscrito": sem_inscrito,
                "relacaoDaAmpla": str(ampla.id) if ampla is not None else None,
                # **A terceira prova, pela relação congelada, e não pelas inscrições de hoje**: é a
                # relação que fixou o universo do sorteio, e é ela a relação definitiva pertinente.
                "declaradasNaAmpla": {
                    str(modalidade)
                    for modalidade in ParticipanteHabilitado.objects.filter(relacao=ampla)
                    .values_list("inscricao__modality_id", flat=True)
                    .distinct()
                    if modalidade
                }
                if ampla is not None
                else set(),
            }
        return self._do_sorteio[chave]

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

    **Quatro casos ganham frase** (155, FR-6301): a reversão por esgotamento (a destinação), o
    Edital silente (FR-6321), a linha geral sem quem a ocupe (D-014) e a passagem entre cotas, que
    diz a limitação do GPS sem ato nenhum (UX-603). **Sob a reversão por saldo, nada muda** (R-010):
    nem na reserva, nem na linha geral do Perfil que a declara — a espera é da decisão do usuário,
    e a tela continua como estava.
    """
    from processo_seletivo.ocupacao.application.destinacao import leitura_da_vaga

    leitura = leitura_da_vaga(
        edital=edital,
        perfil_id=perfil_id,
        marco_id=marco_id,
        lista_id=lista_id,
        fatos_externos=composicao if composicao is not None else Composicao(at=at),
        at=at,
    )
    declaracao = leitura["declaracao"]
    if declaracao == nomes.REVERSAO_POR_SALDO:
        return None
    ausencia = leitura.get("ausencia")
    if ausencia and not ausencia["comprovada"]:
        # **O que falta, dito como o que é** (155, FR-6333): a relação não congelada não é lista
        # vazia, e nenhum ato é oferecido.
        return {
            **leitura["situacao"],
            "frase": ausencia["frase"],
            "impedimentos": [],
            "declarada": leitura["frase"],
            "ato": "",
            "disponivel": False,
            "destinacao": False,
            "naoPreenchida": False,
            "silente": False,
            "limitacao": False,
            "movimentos": [],
            "naoPreenchidas": [],
        }
    if lista_id is None and declaracao == nomes.PASSAGEM_ENTRE_COTAS:
        # A passagem entre cotas é da vaga reservada: a linha geral do Perfil que a declara não
        # ganha ato nem frase nesta entrega (FR-6318).
        return None
    situacao = leitura["situacao"]
    frase = frase_da_situacao(leitura, rotulo)
    if not frase:
        return None
    estado = situacao["estado"]
    destina = declaracao == nomes.REVERSAO_POR_ESGOTAMENTO and lista_id is not None
    return {
        **situacao,
        "frase": frase,
        "impedimentos": [
            {"codigo": i.codigo, "frase": _com_data(i), "ate": i.ate}
            for i in situacao["impedimentos"]
        ],
        "declarada": leitura["frase"],
        # **O ato que a vaga pede, pelo nome da tela** (UX-602): um ato por caminho.
        "ato": DESTINAR if destina else (DECLARAR if estado != conta.PASSAGEM_ENTRE_COTAS else ""),
        "disponivel": estado in (conta.DESTINACAO_DISPONIVEL, conta.NAO_PREENCHIDA_DISPONIVEL),
        "destinacao": estado == conta.DESTINACAO_DISPONIVEL,
        "naoPreenchida": estado == conta.NAO_PREENCHIDA_DISPONIVEL,
        # O Edital silente, na reserva (FR-6321): a frase e os dois caminhos.
        "silente": declaracao is None and lista_id is not None,
        "limitacao": estado == conta.PASSAGEM_ENTRE_COTAS,
        "movimentos": _movimentos_da_reserva(leitura["movimentos"], lista_id),
        "naoPreenchidas": leitura["naoPreenchidas"],
    }


def _movimentos_da_reserva(movimentos, lista_id):
    """As destinações da reserva e os desfazimentos delas, cada uma dizendo se ainda se desfaz.

    **Só a destinação por ato próprio se desfaz aqui** (R-005): o movimento que a apuração gravava
    antes da `155` conta como feita (FR-6316), e o desfazimento é a linha que cita a destinação.
    """
    if lista_id is None:
        return []
    desfeitos = {m.desfaz_id for m in movimentos if m.desfaz_id}
    lista = str(lista_id)
    return [
        {
            "registro": m,
            "desfazivel": m.especie == nomes.MOVIMENTO_REVERSAO
            and m.edital_id is not None
            and m.id not in desfeitos,
        }
        for m in movimentos
        if (m.especie == nomes.MOVIMENTO_REVERSAO and str(m.origem_lista_id or "") == lista)
        or (m.especie == nomes.MOVIMENTO_DESFAZIMENTO and str(m.destino_lista_id or "") == lista)
    ]


#: Os atos da vaga sem quem a ocupe, com as palavras que o Centro e a ocupação dizem.
DESTINAR = "Destinar à ampla concorrência"
DECLARAR = "Declarar a vaga não preenchida"
#: A frase da FR-6321, literal: o Edital que não diz o que acontece com a vaga da reserva.
EDITAL_SILENTE = "Este Edital não declara o que acontece com a vaga reservada não preenchida."
#: A limitação da passagem entre cotas, dita como limite do GPS (UX-603), e não do Edital.
LIMITACAO_DA_PASSAGEM = (
    "Este Edital manda a vaga passar antes por outras cotas, na ordem que ele estabelece, e o GPS "
    "ainda não aplica essa ordem: nenhum ato desta tela leva a vaga à ampla concorrência nem a "
    "declara não preenchida."
)


def chamadas_dependentes(
    *, edital, perfil_id, marco_id, lista_id, movimento_id=None, nao_preenchida_id=None, at=None
):
    """As chamadas que dependem do ato a desfazer — `[{id, rotulo, ocupa}]` (155, R-005).

    **Dependente é a chamada vigente do recorte cuja apuração leu o ato**: o movimento em
    `movimentosLidos`, ou a declaração em `naoPreenchidasLidas`. Ela foi feita sobre a conta que o
    ato mudou, e desfazê-lo tiraria a vaga de quem foi chamado para ela. Continua dependente
    enquanto não tem desfecho, ou quando o desfecho a pôs na vaga (efeito de inclusão); o desfecho
    que a tirou da vaga a libera.

    **Mora aqui, e não na ocupação** (155, R-004): a ocupação não importa a condução, e esta função
    é o *callable* que o ato recebe, como `pessoas_chamadas` no acréscimo.
    """
    from processo_seletivo.convocacao.application import selectors as conducao

    chave, alvo = (
        ("movimentosLidos", movimento_id)
        if movimento_id is not None
        else ("naoPreenchidasLidas", nao_preenchida_id)
    )
    alvo = str(alvo)
    lidas = [
        c
        for c in conducao.vigentes(
            conducao.convocacoes_do_recorte(
                edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id
            )
        )
        if alvo in {str(i) for i in ((c.apuracao.universo or {}).get(chave) or [])}
    ]
    dependentes = []
    for chamada in lidas:
        desfecho = conducao.desfecho_de(chamada)
        ocupa = desfecho is not None and desfecho.efeito.especie == nomes.EFEITO_INCLUSAO
        if desfecho is None or ocupa:
            dependentes.append((chamada, ocupa))
    if not dependentes:
        return []
    identidades = conducao.identidades_de({c.inscricao_id for c, _ in dependentes})
    return [
        {
            "id": str(chamada.id),
            "rotulo": _rotulo_da_pessoa(identidades.get(chamada.inscricao_id) or {}),
            "ocupa": ocupa,
        }
        for chamada, ocupa in dependentes
    ]


def _rotulo_da_pessoa(identidade):
    return " — ".join(
        parte for parte in (identidade.get("protocolo"), identidade.get("nome")) if parte
    )


def anotar_recortes(*, edital, perfil_id, marco_id, recortes, at=None):
    """A situação da vaga em cada recorte da ocupação, com uma composição para o marco inteiro.

    `recorte["vaga"]` fica `None` onde a tela não diz nada novo. Só o recorte apurado pergunta: sem
    apuração não há vaga a ocupar afirmada, e a leitura custaria consultas para dizer nada. A linha
    geral pergunta também (155, D-014): a ampla sem ninguém que ainda possa ocupá-la admite a
    declaração de não preenchida.
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
            if recorte.get("apuracao") is not None
            # **A lista de sorteio sem relação pergunta também** (155, R-007): sem apuração, a
            # vaga dela é lida pela relação da ampla — ou dita "relação não congelada".
            or composicao.ausencia_de_concorrente(
                edital=edital,
                perfil_id=perfil_id,
                marco_id=marco_id,
                lista_id=recorte.get("listaId"),
                at=at,
            )
            is not None
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
    # **"da lista «PPP»", e não "da PPP"** (155, UX-600): o rótulo é o nome publicado da
    # Modalidade, e "1 vaga da Pessoas pretas, pardas e indígenas" não concorda.
    lista = f"lista «{rotulo}»" if rotulo else "lista"
    reservada = leitura.get("listaId") is not None
    declaracao = leitura["declaracao"]
    destina = declaracao == nomes.REVERSAO_POR_ESGOTAMENTO and reservada
    silente = declaracao is None and reservada
    if destina:
        declara = f" O Edital declara: «{leitura['frase']}»" if leitura["frase"] else ""
    elif silente:
        declara = f" {EDITAL_SILENTE}"
    else:
        declara = ""
    estado = situacao["estado"]
    sem_relacao = bool((leitura.get("ausencia") or {}).get("comprovada"))
    if estado in (conta.DESTINACAO_DISPONIVEL, conta.NAO_PREENCHIDA_DISPONIVEL):
        quantidade = situacao["quantidade"]
        porque = (
            # A lista de sorteio sem relação não tem ordem (155, R-007): a prova é a relação.
            "ninguém concorreu por esta lista, como a relação da ampla concorrência congelada "
            "comprova."
            if sem_relacao
            else f"ninguém mais na ordem desta lista pode ocupá-la{'s' if quantidade != 1 else ''}."
        )
        return (
            f"{_vagas(quantidade)} da {lista} sem quem a{'s' if quantidade != 1 else ''} ocupe: "
            + porque
            + declara
        )
    if estado == conta.PASSAGEM_ENTRE_COTAS:
        if situacao["livres"]:
            # Com alguém livre na ordem, o caminho é chamá-lo, e a limitação ainda não pesa.
            return ""
        return f"{_vagas(leitura.get('saldo') or 0)} da {lista} a ocupar. {LIMITACAO_DA_PASSAGEM}"
    if estado == conta.IMPEDIDA:
        motivos = "; ".join(_com_data(i) for i in situacao["impedimentos"])
        ato = (
            "a destinação à ampla concorrência"
            if destina
            else "a declaração de vaga não preenchida"
        )
        return (
            f"{_vagas(leitura.get('saldo') or 0)} da {lista} a ocupar, e {ato} ainda não cabe: "
            f"{motivos}." + declara
        )
    if estado == conta.SEM_VAGA_A_DESTINAR and not leitura.get("saldo"):
        partes = []
        if situacao["destinadas"]:
            # **O movimento antigo conta como destinação feita** (US1.5, FR-6316): a tela o cita,
            # e nenhum ato a destina de novo.
            partes.append(
                f"{_vagas(situacao['destinadas'])} da {lista} já "
                + ("foi destinada" if situacao["destinadas"] == 1 else "foram destinadas")
                + " à ampla concorrência."
            )
        if leitura.get("declaradas"):
            # **Declarada, a vaga aparece como "não preenchida"** (FR-6326), e não como zero.
            partes.append(
                f"{_vagas(leitura['declaradas'])} da {lista} "
                + ("declarada" if leitura["declaradas"] == 1 else "declaradas")
                + " não preenchida"
                + ("" if leitura["declaradas"] == 1 else "s")
                + "."
            )
        return " ".join(partes)
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
    "DECLARAR",
    "DESTINAR",
    "EDITAL_SILENTE",
    "LIMITACAO_DA_PASSAGEM",
    "Composicao",
    "anotar_recortes",
    "chamadas_dependentes",
    "frase_da_situacao",
    "rotulo_do_recorte",
    "situacao_do_recorte",
]
