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

from processo_seletivo.avaliacoes.application.trilha import auditar
from processo_seletivo.classificacao.application.selectors import ato_vigente
from processo_seletivo.comissoes.application import comando_de_comissao
from processo_seletivo.comissoes.application.comissao import identificador
from processo_seletivo.convocacao.application import selectors
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
    especie,
    fundamento,
    idempotency_key,
    correlation_id,
    lista_id=None,
    vencimento=None,
    motivo="",
    justifica_precedencia=False,
):
    """Pratica a convocação e devolve o que ela declarou. Recusa antes de gravar qualquer coisa."""
    payload = {
        "edital": str(edital_id),
        "perfil": str(perfil_id),
        "marco": str(marco_id),
        "lista": str(lista_id) if lista_id else "",
        "inscricao": str(inscricao_id),
        "especie": (especie or "").strip(),
    }
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
        especie = _especie(especie)
        texto_do_fundamento = (fundamento or "").strip()
        if not texto_do_fundamento:
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

        anterior = _vigente_da_pessoa(contexto, inscricao)
        texto_do_motivo = (motivo or "").strip()
        if anterior is not None and not texto_do_motivo:
            raise DomainError(
                nomes.CONVOCACAO_VIGENTE_EXISTENTE,
                "Esta Inscrição já tem convocação vigente neste recorte. Para corrigi-la, declare "
                "o motivo da sucessão.",
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

        versao = effective_version(edital_id=edital.id, at=ctx.now)
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
            criado_por=str(getattr(actor, "subject", actor)),
            criado_em=ctx.now,
        )
        convocacao.save()
        return _concluir(
            ctx,
            convocacao,
            actor,
            correlation_id,
            idempotency_key,
            precedencia_justificada=bool(justifica_precedencia)
            and bool(fila.precedencia(contexto["fila"], inscricao)),
        )


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


def _vigente_da_pessoa(contexto, inscricao):
    """A convocação vigente desta pessoa no recorte, ou `None`.

    **Vigente é a que ninguém sucedeu**, e não a mais recente: sucessão cria linha nova, e a
    anterior continua legível — é o que permite reconstruir o que foi corrigido, e por quê.
    """
    alvo = chave_da_inscricao(inscricao)
    for convocacao in selectors.vigentes(contexto["convocacoes"]):
        if chave_da_inscricao(convocacao.inscricao_id) == alvo:
            return convocacao
    return None


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
    ctx, convocacao, actor, correlation_id, idempotency_key, *, precedencia_justificada=False
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
            # **Pular alguém fica escrito** (`FR-267`). A recusa admite a precedência com
            # fundamento; o que impede a exceção de virar rotina invisível é ela constar da trilha
            # com todas as letras, ao lado do fundamento que a autoriza.
            + (
                " Convocada à frente de habilitados sem convocação e sem desfecho, com fundamento "
                "registrado neste ato."
                if precedencia_justificada
                else ""
            )
        ),
        idempotency_key=idempotency_key,
    )
    declarado = {
        "id": str(convocacao.id),
        "inscricao": str(convocacao.inscricao_id),
        "especie": convocacao.especie,
        "vencimento": convocacao.vencimento.isoformat() if convocacao.vencimento else None,
        "sucede": str(convocacao.convocacao_anterior_id)
        if convocacao.convocacao_anterior_id
        else None,
    }
    ctx.concluir_sem_resultado(201, declarado)
    return declarado


def _edital_do_processo(processo, edital_id):
    try:
        return Edital.objects.get(processo=processo, id=identificador(edital_id))
    except Edital.DoesNotExist as erro:
        raise DomainError("edital_nao_encontrado", "Edital não encontrado.", 404) from erro


__all__ = ["convocar"]
