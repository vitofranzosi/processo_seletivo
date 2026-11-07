"""O ato que chama uma pessoa para a vaga que falta — com as recusas que o tornam honesto (019).

**Tudo o que é autoridade, idempotência e trilha vem de onde já vinha**: o mesmo
`comando_de_comissao` que a emissão da ordem, a do corte e a da apuração percorrem. Uma capacidade
nova aqui inventaria autoridade que nenhum Edital distingue — é a decisão que a `014` tomou, e a
`016` já herdou.

**Esta feature não seleciona ninguém e não conta vagas.** Ela lê a faixa que o corte vigente
produziu, o Resultado que a `013` consolidou e a apuração que a `016` emitiu, e chama quem a ordem
indica. Quem escolhe é a `014`; quem conta é a `016`.

**Correção é sucessão** (`FR-272`). Convocar alguém que já tem convocação vigente é recusado — a
menos que venha motivo, e aí nasce a sucessora, sem tocar na anterior. É a mesma forma que
`emitir_apuracao` usa, e pela mesma razão: a tabela é append-only, e `UPDATE` não existe nela.
"""

from django.utils import timezone

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.classificacao.application.selectors import ato_vigente
from processo_seletivo.comissoes.application import comando_de_comissao
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.convocacao.application import selectors
from processo_seletivo.convocacao.domain import especie as especie_da_posicao
from processo_seletivo.convocacao.domain import fila, nomes
from processo_seletivo.convocacao.models import Convocacao
from processo_seletivo.ocupacao.domain.apuracao import chave_da_inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.application.selectors import effective_version
from processo_seletivo.shared.api.problems import DomainError

CONVOCAR = "CONVOCACAO_CONVOCAR"
# A mesma base de autoridade da ordem, do corte e da apuração. A autoridade é consumida, não
# inventada: nenhum Edital da amostra distingue quem convoca de quem publica o resultado.
ATO = "convocacao:convocar"


def convocar(
    *,
    actor,
    processo_id,
    edital_id,
    perfil_id,
    marco_id,
    inscricao_id,
    fundamento,
    idempotency_key,
    correlation_id,
    lista_id=None,
    vencimento=None,
    motivo="",
    justifica_precedencia=False,
    razao_adicional="",
    especie="",
    fundamento_por_especie=None,
    correcao=None,
):
    """Pratica a convocação e devolve o que ela declarou. Recusa antes de gravar qualquer coisa.

    **A espécie é derivada da posição** (050, `D-008`). Informá-la continua possível — é o que a API
    da `019` sempre recebeu —, mas a informada que diverge da derivada é recusada; vazia, vale a
    derivada. `razao_adicional` entra na trilha: é por onde a `050` registra a origem do vencimento.
    `fundamento_por_especie(especie, apuracao)`, quando vem, deriva o fundamento **sob a trava**,
    depois de a espécie ser conhecida — é o caminho da chamada individual da `050`.

    `correcao`, quando vem, é a correção pela tela da `120`: `{"convocacao_id", "assinatura"}`. Ela
    acrescenta duas conferências sob a trava — a convocação nomeada ainda é a que está em aberto
    (`FR-3843`), e a prévia que a pessoa viu ainda é a do ato (`FR-3857`) — e as recusas próprias de
    quem corrige: motivo e vencimento. Sem ela, o comando é o de sempre.
    """
    payload = {
        "edital": str(edital_id),
        "perfil": str(perfil_id),
        "marco": str(marco_id),
        "lista": str(lista_id) if lista_id else "",
        "inscricao": str(inscricao_id),
        "especie": (especie or "").strip(),
    }
    if correcao is not None:
        # **O que se assinou entra na reserva**: a mesma chave com outra prévia é outro pedido, e
        # recebe `idempotency_conflict`, como em todo comando.
        payload["corrige"] = str(correcao["convocacao_id"])
        payload["previa"] = correcao["assinatura"]
    with comando_de_comissao(
        actor=actor,
        processo_id=processo_id,
        operation=ATO,
        payload=payload,
        idempotency_key=idempotency_key,
    ) as ctx:
        if ctx.repetido:
            return ctx.desfecho_anterior
        edital = _edital_do_processo(ctx.processo, edital_id)
        perfil = identificador(perfil_id)
        marco = identificador(marco_id)
        lista = identificador(lista_id) if lista_id else None
        inscricao = identificador(inscricao_id)
        informada = _especie(especie) if (especie or "").strip() else ""
        texto_do_fundamento = (fundamento or "").strip()
        if not texto_do_fundamento and fundamento_por_especie is None:
            # O *"no interesse da Administração"* do 77/2026 entra aqui, e é o que faz a chamada
            # ser ato motivado em vez de linha numa planilha.
            raise DomainError(
                nomes.FUNDAMENTO_OBRIGATORIO,
                "Declare o fundamento da convocação.",
                422,
                campo="fundamento",
            )

        # **A ordem tem de ser a vigente** (`FR-265`): chamar segundo uma ordem já sucedida é
        # convocar pela lista de ontem, e a pessoa chamada pode não ser mais a próxima.
        ato = ato_vigente(edital=edital, marco_id=marco, lista_id=lista)
        if ato is None:
            raise DomainError(
                nomes.ORDEM_NAO_VIGENTE,
                "Este recorte não tem ordem vigente: não há de onde tirar quem é o próximo.",
                409,
            )

        contexto = selectors.contexto_do_recorte(
            edital=edital, perfil_id=perfil, marco_id=marco, lista_id=lista, at=ctx.now
        )
        apuracao = contexto["apuracao"]
        if apuracao is None:
            # **Chamar para vaga que ninguém apurou é prometer o que não se sabe existir.** Não é
            # o mesmo que "não há vaga": é não saber, e a recusa diz isso.
            raise DomainError(
                nomes.APURACAO_AUSENTE,
                "Este recorte não tem apuração de ocupação emitida: não há vaga faltante "
                "conhecida para a qual convocar.",
                409,
            )
        if contexto["causasDeObsolescencia"]:
            causas = ", ".join(contexto["causasDeObsolescencia"])
            raise DomainError(
                nomes.APURACAO_OBSOLETA,
                f"A apuração vigente deste recorte já se sabe para trás ({causas}): emita a "
                "apuração seguinte antes de convocar.",
                409,
            )

        anterior = _em_aberto_da_pessoa(contexto, inscricao)
        texto_do_motivo = (motivo or "").strip()
        if correcao is not None:
            # **Depois da repetição, e não antes** (`R-002` da `120`): o segundo clique do mesmo
            # formulário já voltou com o resultado do primeiro, lá em cima. O que chega aqui é outro
            # formulário — e, se ele viu uma convocação que já não está em aberto, é recusado.
            _conferir_a_nomeada(
                contexto,
                inscricao=inscricao,
                anterior=anterior,
                nomeada_id=correcao["convocacao_id"],
            )
            if not texto_do_motivo:
                raise DomainError(
                    nomes.MOTIVO_DA_CORRECAO_OBRIGATORIO,
                    "Declare o motivo da correção: ele fica na convocação e na trilha, ao lado da "
                    "convocação corrigida.",
                    422,
                    campo="motivo",
                )
        if anterior is not None:
            derivada = especie_da_posicao.especie_da_sucessora(
                inscricao,
                ocupando=contexto["ocupando"],
                alcancados=contexto["alcancados"],
                regularizaveis=contexto["regularizaveis"],
                anterior=anterior,
            )
        else:
            derivada = especie_da_posicao.derivada(
                inscricao,
                ocupando=contexto["ocupando"],
                alcancados=contexto["alcancados"],
                regularizaveis=contexto["regularizaveis"],
            )
        # Sem espécie derivável, a pessoa não é chamável por nenhuma: as recusas abaixo dizem por
        # quê, e a espécie de trabalho só decide qual delas se aplica.
        especie = informada or derivada or nomes.SUPLENCIA
        # **A versão é lida uma vez, sob a trava**, e serve à assinatura e à gravação: lida duas
        # vezes, uma Retificação entre as leituras gravaria um fundamento que a prévia não mostrou.
        versao = effective_version(edital_id=edital.id, at=ctx.now)
        if correcao is not None:
            _conferir_a_previa(
                correcao,
                anterior=anterior,
                apuracao=apuracao,
                versao=versao,
                perfil=perfil,
                especie=especie,
            )
        if anterior is not None and not texto_do_motivo:
            raise DomainError(
                nomes.CONVOCACAO_VIGENTE_EXISTENTE,
                "Esta Inscrição tem convocação neste recorte aguardando desfecho. Para corrigi-la, "
                "declare o motivo da sucessão; para chamá-la de novo, registre antes o desfecho da "
                "chamada anterior.",
                409,
            )

        # **A ordem é conferida antes do déficit, e a ordem das recusas é ela mesma uma decisão.**
        # Quem tenta convocar alguém fora da faixa num recorte sem vaga faltante recebe duas
        # verdades, e só uma delas diz o que fazer: *"não há vaga"* manda emitir apuração, e o
        # problema era outro. A recusa mais específica vem primeiro.
        if especie == nomes.PARA_REGULARIZAR:
            _recusar_por_regularizacao(
                contexto,
                inscricao=inscricao,
                sucede=anterior,
                justifica_precedencia=justifica_precedencia,
            )
        else:
            _recusar_por_ordem(
                contexto,
                inscricao=inscricao,
                sucede=anterior,
                justifica_precedencia=justifica_precedencia,
            )
        _recusar_por_deficit(
            contexto,
            especie=especie,
            inscricao=inscricao,
            apuracao=apuracao,
            sucede=anterior,
        )
        # **Depois das recusas de ordem e de vaga, e a ordem é deliberada.** Quem convoca alguém
        # fora da faixa "para vaga inicial" precisa ouvir que a pessoa está fora da faixa — a
        # espécie errada é o sintoma, e não o problema.
        if informada and derivada and informada != derivada:
            raise DomainError(
                nomes.ESPECIE_DIVERGENTE_DA_POSICAO,
                "A espécie informada não é a que a posição desta pessoa determina: "
                f"{_ESPECIE_POR_EXTENSO[derivada]}. A espécie é consequência da posição na fila, "
                "e não escolha.",
                422,
                campo="especie",
            )

        if fundamento_por_especie is not None:
            texto_do_fundamento = fundamento_por_especie(especie, apuracao)
        # **A sucessora copia o número da raiz que corrige**; a chamada nova recebe o seguinte. É
        # a diferença entre corrigir um ato e praticar outro, dita por dado.
        chamada = (
            anterior.chamada
            if anterior is not None
            else _proxima_chamada(contexto, inscricao=inscricao)
        )
        convocacao = Convocacao(
            edital=edital,
            perfil_id=perfil,
            marco_id=marco,
            lista_id=lista,
            inscricao_id=inscricao,
            especie=especie,
            vencimento=vencimento,
            fundamento=texto_do_fundamento,
            apuracao=apuracao,
            ato_de_ordenacao_id=ato.id,
            corte_id=contexto["corte"].id if contexto["corte"] is not None else None,
            versao=versao,
            convocacao_anterior=anterior,
            motivo_da_sucessao=texto_do_motivo if anterior is not None else "",
            chamada=chamada,
            criado_por=str(getattr(actor, "subject", actor)),
            criado_em=ctx.now,
        )
        convocacao.save()
        # **A lista da chamada nasce com ela, no mesmo ato** (115, FR-3572): a raiz grava, e a
        # sucessora que corrige vencimento ou fundamento herda pela raiz (D-009).
        from processo_seletivo.convocacao.application.documentos import gravar_lista_da_chamada

        gravar_lista_da_chamada(convocacao, versao=versao)
        return _concluir(
            ctx,
            convocacao,
            actor,
            correlation_id,
            idempotency_key,
            precedencia_justificada=bool(justifica_precedencia)
            and bool(fila.precedencia(contexto["fila"], inscricao)),
            razao_adicional=razao_adicional,
        )


# **Os rótulos do modelo, e não uma segunda grafia**: renomear a espécie na tela e esquecer a recusa
# faria as duas dizerem coisas diferentes.
_ESPECIE_POR_EXTENSO = {
    valor: rotulo[:1].lower() + rotulo[1:]
    for valor, rotulo in Convocacao._meta.get_field("especie").choices
}


def _especie(valor):
    especie = (valor or "").strip()
    if especie not in nomes.ESPECIES_DE_CONVOCACAO:
        raise DomainError(
            nomes.ESPECIE_DE_CONVOCACAO_INVALIDA,
            "A convocação é para vaga inicial, para suplência ou para regularizar, e nada mais.",
            422,
            campo="especie",
        )
    return especie


def _proxima_chamada(contexto, *, inscricao):
    """Quantas vezes esta pessoa já foi chamada neste recorte, mais um.

    Conta **todas** as convocações dela, inclusive as sucedidas: o número identifica a chamada, e
    uma chamada corrigida continua sendo aquela chamada.
    """
    alvo = chave_da_inscricao(inscricao)
    numeros = [
        convocacao.chamada
        for convocacao in contexto["convocacoes"]
        if chave_da_inscricao(convocacao.inscricao_id) == alvo
    ]
    return max(numeros, default=0) + 1


def _em_aberto_da_pessoa(contexto, inscricao):
    """A convocação desta pessoa que **ainda não teve desfecho**, ou `None`.

    **Chamada em aberto, e não "chamada vigente"** — a distinção é o que faz a segunda convocação
    da mesma pessoa ser possível quando ela cabe. Uma convocação com desfecho está **concluída**: a
    pessoa respondeu, ou a Administração concluiu por ela. Chamá-la de novo — porque foi
    reclassificada, ou porque a vaga voltou a vagar — é uma **chamada nova**, e não a correção da
    anterior.

    *A primeira versão bloqueava por convocação vigente, sem olhar o desfecho, e produzia um beco:
    o reclassificado voltava ao fim da fila, chegava a vez dele, e a chamada era recusada com
    `convocacao_vigente_existente`. A saída oferecida — declarar motivo de sucessão — era pior:
    sucessão pula as guardas de ordem, de modo que a única forma de chamá-lo furava a fila.*

    **Vigente continua sendo a que ninguém sucedeu**: sucessão cria linha nova, e a anterior segue
    legível. O que muda é que a sucessão passa a ser o que ela sempre foi — correção de um ato
    ainda pendente de resposta.
    """
    alvo = chave_da_inscricao(inscricao)
    for convocacao in selectors.vigentes(contexto["convocacoes"]):
        if chave_da_inscricao(convocacao.inscricao_id) != alvo:
            continue
        if selectors.desfecho_de(convocacao) is None:
            return convocacao
    return None


def _quando(instante):
    """O instante na hora local, como as frases da condução o dizem."""
    return timezone.localtime(instante).strftime("%d/%m/%Y às %Hh%M")


def _conferir_a_nomeada(contexto, *, inscricao, anterior, nomeada_id):
    """A convocação que o formulário corrige ainda é a que está em aberto (120, `FR-3843`).

    **Sem esta conferência, o formulário velho praticaria outro ato.** O comando corrige a
    convocação em aberto *no instante do ato*: se outra pessoa já a corrigiu, ele corrigiria a
    sucessora, com um motivo escrito para a anterior; se ela teve desfecho, não haveria nada em
    aberto, e a chamada seguiria como **chamada nova**, com o motivo ignorado. As duas recusas dizem
    o que aconteceu, e as duas param o ato.

    A nomeada que não é do recorte, ou não é desta inscrição, é referência fora do escopo do ato, e
    recebe o 404 de sempre: a resposta não diz se ela existe em outro lugar.
    """
    from processo_seletivo.comissoes.application import nao_encontrado

    alvo = chave_da_inscricao(inscricao)
    nomeada = next(
        (c for c in contexto["convocacoes"] if str(c.id) == str(nomeada_id)),
        None,
    )
    if nomeada is None or chave_da_inscricao(nomeada.inscricao_id) != alvo:
        raise nao_encontrado()
    if anterior is None or anterior.id != nomeada.id:
        desfecho = selectors.desfecho_de(nomeada)
        if desfecho is not None:
            raise DomainError(
                nomes.CONVOCACAO_CORRIGIDA_COM_DESFECHO,
                f"Esta convocação teve desfecho em {_quando(desfecho.registrado_em)} "
                f"({desfecho.get_especie_display().lower()}), depois que você abriu o formulário: "
                "não há mais o que corrigir nela, e nada foi gravado.",
                409,
            )
        sucessora = next(
            (c for c in contexto["convocacoes"] if c.convocacao_anterior_id == nomeada.id),
            None,
        )
        raise DomainError(
            nomes.CONVOCACAO_CORRIGIDA_SUCEDIDA,
            (
                f"Esta convocação já foi corrigida em {_quando(sucessora.criado_em)}, depois que "
                "você abriu o formulário. Nada foi gravado: confira a convocação vigente antes de "
                "corrigir de novo."
            )
            if sucessora is not None
            else "Esta convocação não está mais em aberto. Nada foi gravado.",
            409,
        )
    if nomeada.vencimento is None:
        raise DomainError(
            nomes.CORRECAO_SEM_VENCIMENTO,
            "Esta convocação não tem vencimento, porque o Edital não publica prazo: não há prazo a "
            "corrigir nela.",
            409,
        )


def _conferir_a_previa(correcao, *, anterior, apuracao, versao, perfil, especie):
    """O que a prévia mostrou ainda é o que o ato vai gravar (120, `FR-3857`, `D-010`).

    **Nomear a convocação não basta.** A apuração seguinte, emitida por outra pessoa no intervalo,
    muda a data que o fundamento cita sem tocar na convocação; uma Retificação muda os rótulos; a
    contagem nova pode mudar a espécie. A assinatura é recalculada aqui, sob a trava, com o que o
    ato vai usar — e a recusa recarrega a tela, que monta a prévia nova.
    """
    from processo_seletivo.convocacao.application.fluxo import forma_vigente
    from processo_seletivo.convocacao.domain import alcance

    agora = alcance.assinatura_da_correcao(
        convocacao_id=anterior.id,
        apuracao_id=apuracao.id,
        versao_id=getattr(versao, "id", None),
        forma=forma_vigente(versao, perfil),
        especie=especie,
    )
    if agora != (correcao.get("assinatura") or ""):
        raise DomainError(
            nomes.PREVIA_DA_CORRECAO_SUPERADA,
            "A prévia mudou desde que você abriu este formulário — a apuração, o Edital ou a "
            "posição da pessoa não são mais os mesmos. Nada foi gravado: confira o fundamento e a "
            "espécie abaixo antes de confirmar.",
            409,
        )


def _recusar_por_deficit(contexto, *, especie, inscricao, apuracao, sucede):
    """Chamar **acrescentaria** um ocupante, e não há vaga faltante que o receba (`sem_deficit`).

    **A pergunta não é "há déficit", é "esta chamada acrescenta alguém".** Pela contagem da `016`,
    o titular ocupa vaga desde a emissão da apuração — antes de ser chamado. Convocá-lo é formalizar
    o que o número já diz, e exigir déficit ali recusaria **a primeira convocação de todo certame**:
    com 40 vagas e 40 titulares habilitados, `faltando` é zero, e é justamente esse o recorte em que
    as 40 pessoas precisam ser chamadas. A `FR-266` confirma a leitura, e nomeia só duas recusas
    ligadas à apuração: ausente e obsoleta.

    Quem **não** está no conjunto de ocupantes — o suplente — é quem acrescenta, e para ele a vaga
    precisa existir.

    **O déficit é descontado das chamadas em aberto, e não lido cru da apuração.** Convocar não
    produz efeito nenhum, de modo que a apuração vigente continua dizendo o mesmo número enquanto
    ninguém responde: lido cru, ele autorizaria chamar dois suplentes para a mesma vaga. Os dois
    aceitariam, o conjunto de ocupantes passaria do teto, e o `min` da contagem devolveria o número
    certo escondendo o fato — que é o pior desfecho possível, porque nada acusaria.

    A própria chamada em aberto da pessoa que se está corrigindo não conta contra ela: corrigir uma
    convocação não é abrir uma segunda.

    **`PARA_REGULARIZAR` passa por aqui como qualquer outra**, e a regra da `US3` é a mesma dita de
    outro jeito: ela só é admitida quando as matrículas deferidas do recorte são **menos** que as
    vagas — que é exatamente `faltando > 0`. O indeferido não é ocupante, logo acrescenta.
    """
    ocupando = contexto["ocupando"]
    alvo = chave_da_inscricao(inscricao)
    if alvo in ocupando:
        return
    # As chamadas em aberto que **também** acrescentariam alguém. As de titulares não disputam
    # vaga faltante nenhuma, e contá-las bloquearia a suplência sem razão.
    acrescentam = {i for i in contexto["emAberto"] if chave_da_inscricao(i) not in ocupando}
    if sucede is not None:
        acrescentam.discard(sucede.inscricao_id)
    if apuracao.faltando - len(acrescentam) > 0:
        return
    raise DomainError(
        nomes.SEM_DEFICIT,
        (
            "A apuração vigente deste recorte não registra vaga faltante."
            if apuracao.faltando == 0
            else (
                f"As {apuracao.faltando} vaga(s) faltante(s) deste recorte já estão cobertas por "
                f"{len(acrescentam)} convocação(ões) aguardando resposta."
            )
        ),
        409,
    )


def _recusar_por_regularizacao(contexto, *, inscricao, sucede, justifica_precedencia):
    """A fila da convocação para regularizar é a dos **indeferidos**, e tem ordem própria (`US3`).

    **Quem regulariza não está na fila de chamada**, e não podia estar: ele não habilitou, e a fila
    de chamada é de quem pode ocupar vaga. Conferi-lo contra aquela lista recusaria toda convocação
    para regularizar com `fora_da_faixa` — a recusa certa para o caso errado.

    **A ordem entre os indeferidos é a de classificação**, e o item 8.2 do 77/2026 não abre exceção
    para quem corrige: chamar o terceiro indeferido antes do primeiro é a mesma quebra de ordem que
    chamar o terceiro classificado antes do primeiro.
    """
    regularizaveis = contexto["regularizaveis"]
    if sucede is not None:
        return
    if not fila.esta_na_faixa(regularizaveis, inscricao):
        raise DomainError(
            nomes.FORA_DA_FAIXA,
            "Esta Inscrição não está entre as que podem ser convocadas para regularizar neste "
            "recorte: ou está fora da faixa, ou o Resultado dela não está indeferido, ou ela já "
            "foi chamada.",
            409,
        )
    anteriores = fila.precedencia(regularizaveis, inscricao)
    if anteriores and not justifica_precedencia:
        raise DomainError(
            nomes.PRECEDENCIA_NA_ORDEM,
            f"Há {len(anteriores)} Inscrição(ões) indeferida(s) antes desta na ordem, ainda sem "
            "convocação para regularizar: convoque-as, ou registre o desfecho de cada uma.",
            409,
        )


def _recusar_por_ordem(contexto, *, inscricao, sucede, justifica_precedencia=False):
    """As recusas que a ordem impõe: estar na faixa, e ser a próxima (`FR-266`, `FR-267`).

    **`fora_da_faixa` não é detalhe de validação.** Convocar quem a faixa não alcançou é
    **selecionar**, e seleção é ato da `014` — fazê-la aqui contornaria o corte publicado.

    **`precedencia_na_ordem` recusa pular alguém em silêncio, e não pular.** A `FR-267` admite a
    precedência *"salvo fundamento registrado no ato"*, e é o que `justifica_precedencia` é: o
    reconhecimento explícito de quem convoca de que está passando à frente, com o fundamento do ato
    servindo de justificativa e ficando na trilha.

    **Não bastaria exigir fundamento**, que já é obrigatório em toda convocação (o *"no interesse da
    Administração"* do 77/2026): lida assim, a recusa nunca dispararia e a garantia seria letra
    morta. O que a torna real é a pessoa ter de dizer que sabe o que está fazendo.
    """
    if sucede is None and fila.esgotou(contexto["fila"]):
        # **`lista_alcancada_esgotada` não é "não há mais candidatos"**: é "não há mais quem chamar
        # dentro do teto que o Edital publicou". A faixa seguinte é ato da `014`, e esta feature não
        # a pede — é a fronteira que a `016` já fixou.
        #
        # **Vem antes de `fora_da_faixa`, e a ordem importa.** Quem tenta convocar alguém de fora
        # da faixa costuma estar fazendo isso justamente porque a lista esgotou; responder "essa
        # pessoa não está na faixa" o manda investigar a pessoa, quando o que ele precisa saber é
        # que não há mais ninguém e que o caminho é pedir a faixa seguinte.
        raise DomainError(
            nomes.LISTA_ALCANCADA_ESGOTADA,
            "Não há mais quem chamar dentro da faixa que o corte alcançou neste recorte. Ampliar "
            "a faixa é ato do corte.",
            409,
        )
    if not fila.esta_na_faixa(contexto["alcancados"], inscricao):
        raise DomainError(
            nomes.FORA_DA_FAIXA,
            "Esta Inscrição não está na faixa vigente deste recorte, ou não está habilitada: "
            "convocá-la seria selecioná-la, e a seleção é ato do corte.",
            409,
        )
    if sucede is not None:
        # Corrigir uma chamada já praticada não reabre a fila: a pessoa já foi chamada, e o que se
        # corrige é o ato, não a vez dela.
        return
    _recusar_reabilitado_a_frente(contexto, inscricao=inscricao)
    _recusar_reclassificado_antes_do_esgotamento(contexto, inscricao=inscricao)
    anteriores = fila.precedencia(contexto["fila"], inscricao)
    if anteriores and not justifica_precedencia:
        raise DomainError(
            nomes.PRECEDENCIA_NA_ORDEM,
            f"Há {len(anteriores)} Inscrição(ões) antes desta na ordem de chamada, sem convocação "
            "e sem desfecho registrado: convoque-as, ou registre o desfecho de cada uma.",
            409,
        )


def _recusar_reclassificado_antes_do_esgotamento(contexto, *, inscricao):
    """O reclassificado só volta a ser chamável depois do último suplente (`FR-291`).

    **Ele não perdeu habilitação** — a `D-008` proíbe afirmá-lo —, mas abriu mão da vez. Chamá-lo
    antes de quem nunca foi chamado inverteria a consequência da reclassificação: quem não
    compareceu passaria à frente de quem estava esperando, e a reclassificação viraria vantagem.

    **E a recusa não se justifica com fundamento**, ao contrário da precedência comum: a posição
    no fim da fila é o **efeito** do desfecho que alguém registrou, e não uma escolha de ordem.
    Desfazê-la por ato administrativo seria desfazer o desfecho sem sucedê-lo.
    """
    reclassificados = {chave_da_inscricao(i) for i in contexto["reclassificados"]}
    if chave_da_inscricao(inscricao) not in reclassificados:
        return
    ainda_chamaveis = [i for i in contexto["fila"] if chave_da_inscricao(i) not in reclassificados]
    if ainda_chamaveis:
        raise DomainError(
            nomes.RECLASSIFICADO_ANTES_DO_ESGOTAMENTO,
            f"Há {len(ainda_chamaveis)} Inscrição(ões) ainda não chamada(s) nesta lista: quem foi "
            "reclassificado volta a ser chamável depois do último suplente.",
            409,
        )


def _recusar_reabilitado_a_frente(contexto, *, inscricao):
    """Há Inscrição reabilitada por deferimento no topo da fila (`FR-292b`).

    **E esta recusa não se justifica com fundamento**, ao contrário da precedência comum. A
    diferença é a fonte: a precedência comum é uma escolha de quem conduz o certame, e a `FR-267` a
    admite motivada; esta é o cumprimento de uma decisão recursal. Passá-la à frente de novo, agora
    com fundamento administrativo, seria desfazer por ato interno o que a instância recursal
    decidiu — e a pessoa teria de recorrer duas vezes do mesmo fato.
    """
    reabilitados = {chave_da_inscricao(i) for i in contexto["reabilitados"]}
    if not reabilitados or chave_da_inscricao(inscricao) in reabilitados:
        return
    a_frente = [i for i in contexto["fila"] if chave_da_inscricao(i) in reabilitados]
    if a_frente:
        raise DomainError(
            nomes.REABILITADO_A_FRENTE,
            f"Há {len(a_frente)} Inscrição(ões) reabilitada(s) por deferimento de recurso à frente "
            "nesta fila: convoque-a(s) primeiro. A decisão recursal devolveu a vez, e não só a "
            "habilitação.",
            409,
        )


def _concluir(
    ctx,
    convocacao,
    actor,
    correlation_id,
    idempotency_key,
    *,
    precedencia_justificada=False,
    razao_adicional="",
):
    _auditar(
        ctx,
        convocacao,
        actor,
        correlation_id,
        idempotency_key,
        precedencia_justificada=precedencia_justificada,
        razao_adicional=razao_adicional,
    )
    declarado = declarado_da_convocacao(convocacao)
    ctx.concluir_sem_resultado(201, declarado)
    return declarado


def _auditar(
    ctx,
    convocacao,
    actor,
    correlation_id,
    idempotency_key,
    *,
    precedencia_justificada=False,
    razao_adicional="",
):
    auditar(
        actor=actor,
        permissao=ctx.base.permissao,
        operation=CONVOCAR,
        aggregate=convocacao,
        now=ctx.now,
        correlation_id=correlation_id,
        # **A proveniência entra na razão, e não só no agregado** (`FR-294`). Ator, ação e instante
        # o registro genérico já guarda; o recorte, a apuração, a ordem e o corte são desta feature,
        # e sem eles a auditoria não reconstrói por que **esta** pessoa foi chamada.
        reason=(
            f"Convocação {convocacao.especie} da inscrição {convocacao.inscricao_id} no marco "
            f"{convocacao.marco_id}, Perfil {convocacao.perfil_id}, lista "
            f"{convocacao.lista_id or 'ampla concorrência'}, sobre a apuração "
            f"{convocacao.apuracao_id} e a ordem {convocacao.ato_de_ordenacao_id}. "
            f"Fundamento: {convocacao.fundamento}"
            + (
                f" Motivo da sucessão: {convocacao.motivo_da_sucessao}"
                if convocacao.motivo_da_sucessao
                else ""
            )
            # **O estado anterior ao lado do posterior** (Constituição, III; 120, `FR-3851`): a
            # razão já dizia o vencimento novo; sem a convocação corrigida e o vencimento dela, a
            # trilha não reconstruía de quanto a correção mudou o prazo.
            + (
                f" Sucede a convocação {convocacao.convocacao_anterior_id}, de vencimento "
                + (
                    convocacao.convocacao_anterior.vencimento.isoformat()
                    if convocacao.convocacao_anterior.vencimento
                    else "não informado"
                )
                + "."
                if convocacao.convocacao_anterior_id
                else ""
            )
            # **Pular alguém fica escrito** (`FR-267`). A recusa admite a precedência com
            # fundamento; o que impede a exceção de virar rotina invisível é ela constar da trilha
            # com todas as letras, ao lado do fundamento que a autoriza.
            + (
                " Convocada à frente de habilitados sem convocação e sem desfecho, com fundamento "
                "registrado neste ato."
                if precedencia_justificada
                else ""
            )
            + (f" {razao_adicional}" if razao_adicional else "")
        ),
        idempotency_key=idempotency_key,
    )


def declarado_da_convocacao(convocacao):
    return {
        "id": str(convocacao.id),
        "inscricao": str(convocacao.inscricao_id),
        "especie": convocacao.especie,
        "vencimento": convocacao.vencimento.isoformat() if convocacao.vencimento else None,
        "sucede": str(convocacao.convocacao_anterior_id)
        if convocacao.convocacao_anterior_id
        else None,
    }


def convocar_em_sequencia(
    ctx,
    *,
    actor,
    edital,
    perfil_id,
    marco_id,
    lista_id,
    inscricoes,
    fundamento,
    vencimento,
    correlation_id,
    razao_adicional="",
):
    """Pratica N convocações, na ordem, **dentro da transação de quem chama** (050, `FR-860`).

    **As mesmas recusas da chamada individual, pessoa a pessoa** (`FR-864`): ordem vigente,
    apuração ausente ou obsoleta, chamada em aberto, faixa, precedência e vaga. O contexto do
    recorte é lido **uma vez** (`FR-888`), e a cada convocação praticada ele é atualizado em memória
    — a pessoa sai da fila e passa a ter chamada em aberto —, que é exatamente o que uma nova
    leitura diria. Uma recusa de qualquer uma sobe e desfaz o ato inteiro: o gesto é um ato, e não
    grava metade.

    **Sem precedência justificada e sem sucessão.** Os dois são exceções que uma pessoa decide sobre
    outra, e continuam exclusivos da chamada individual (`FR-861`).
    """
    ato = ato_vigente(edital=edital, marco_id=marco_id, lista_id=lista_id)
    if ato is None:
        raise DomainError(
            nomes.ORDEM_NAO_VIGENTE,
            "Este recorte não tem ordem vigente: não há de onde tirar quem é o próximo.",
            409,
        )
    contexto = selectors.contexto_do_recorte(
        edital=edital, perfil_id=perfil_id, marco_id=marco_id, lista_id=lista_id, at=ctx.now
    )
    apuracao = contexto["apuracao"]
    if apuracao is None:
        raise DomainError(
            nomes.APURACAO_AUSENTE,
            "Este recorte não tem apuração de ocupação emitida: não há vaga faltante conhecida "
            "para a qual convocar.",
            409,
        )
    if contexto["causasDeObsolescencia"]:
        raise DomainError(
            nomes.APURACAO_OBSOLETA,
            "A apuração vigente deste recorte já se sabe para trás "
            f"({', '.join(contexto['causasDeObsolescencia'])}): emita a apuração seguinte antes "
            "de convocar.",
            409,
        )
    versao = effective_version(edital_id=edital.id, at=ctx.now)
    praticadas = []
    for inscricao in inscricoes:
        if _em_aberto_da_pessoa(contexto, inscricao) is not None:
            raise DomainError(
                nomes.CONVOCACAO_VIGENTE_EXISTENTE,
                "Uma das pessoas do gesto já tem convocação aguardando desfecho neste recorte.",
                409,
            )
        especie = especie_da_posicao.derivada(
            inscricao,
            ocupando=contexto["ocupando"],
            alcancados=contexto["alcancados"],
            regularizaveis=contexto["regularizaveis"],
        )
        _recusar_por_ordem(contexto, inscricao=inscricao, sucede=None)
        _recusar_por_deficit(
            contexto, especie=especie, inscricao=inscricao, apuracao=apuracao, sucede=None
        )
        convocacao = Convocacao(
            edital=edital,
            perfil_id=perfil_id,
            marco_id=marco_id,
            lista_id=lista_id,
            inscricao_id=inscricao,
            especie=especie,
            vencimento=vencimento,
            fundamento=fundamento,
            apuracao=apuracao,
            ato_de_ordenacao_id=ato.id,
            corte_id=contexto["corte"].id if contexto["corte"] is not None else None,
            versao=versao,
            chamada=_proxima_chamada(contexto, inscricao=inscricao),
            criado_por=str(getattr(actor, "subject", actor)),
            criado_em=ctx.now,
        )
        convocacao.save()
        # **A mesma rotina, com a mesma versão, que a chamada individual usa** (115, FR-3572). O
        # gesto nasceu na `050`, antes de a convocação pedir documento, e a `115` só ligou a lista
        # ao caminho individual: as convocações do gesto saíam sem lista, e o aceite passava sem
        # documento nenhum. A gravação fica dentro do laço, e não depois dele, para que a falha de
        # uma pessoa desfaça o gesto inteiro pela mesma transação que desfaz as recusas.
        from processo_seletivo.convocacao.application.documentos import gravar_lista_da_chamada

        gravar_lista_da_chamada(convocacao, versao=versao)
        _auditar(ctx, convocacao, actor, correlation_id, "", razao_adicional=razao_adicional)
        # **O que uma releitura diria, sem relê-la.** A pessoa sai da fila e passa a ter chamada
        # em aberto; a próxima do gesto é, a partir daqui, a primeira da fila.
        alvo = chave_da_inscricao(inscricao)
        contexto["fila"] = [i for i in contexto["fila"] if chave_da_inscricao(i) != alvo]
        contexto["emAberto"] = {*contexto["emAberto"], inscricao}
        praticadas.append(convocacao)
    return praticadas


def _edital_do_processo(processo, edital_id):
    try:
        return Edital.objects.get(processo=processo, id=identificador(edital_id))
    except Edital.DoesNotExist as erro:
        raise DomainError("edital_nao_encontrado", "Edital não encontrado.", 404) from erro


__all__ = ["convocar"]
