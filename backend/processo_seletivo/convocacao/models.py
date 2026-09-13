"""O ato que alcança a pessoa, e o que ela respondeu — os quatro append-only (019, `D-011`).

**Ato, e não projeção**, pela mesma razão da apuração da `016`: convocação é o que alguém vai
contestar, e o número de ontem não é recuperável se os atos-fonte mudarem de leitura. Correção é
**sucessão** (`FR-272`), com motivo — nunca `UPDATE`.

**Vigência não é coluna.** Vigente é a convocação que ninguém sucedeu, como a apuração da `016` e o
corte da `014`. Coluna exigiria `UPDATE`, proibido nestas tabelas — e o provisionamento instala a
proibição em duas camadas independentes.

**Nenhum campo diz recebido, lido ou entregue** (`UX-039`). O sistema registra que **enviou**, e o
prazo corre de `enviado_em` (`D-009`). O campo que não existe não impede a prosa de mentir, e por
isso há varredura sobre as telas — mas ele também não pode existir.

**Vaga individual não é entidade** (`D-011`). Não há `Vaga` aqui, e não deve haver: o Edital publica
quantidade e o sistema conhece conjunto de pessoas. Qual vaga numerada cada pessoa ocupa é pergunta
que nenhum Edital lido responde.
"""

import uuid

from django.db import models
from django.db.models import Q

from processo_seletivo.convocacao.domain import nomes
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import VersaoConsolidada


class AtestadoDeFatoExterno(models.Model):
    """O que aconteceu fora do sistema, e quem atestou que aconteceu (019, `D-004`).

    **O sistema não detém o artefato e não infere o fato.** Ele registra que uma pessoa competente
    concluiu alguma coisa — que o convocado não acessou o ambiente, não apareceu na primeira semana,
    não entregou presencialmente. O documento que prova isso vive onde sempre viveu; o que entra
    aqui é a conclusão e a autoria dela.

    **Sem atestante não há atestado**, e por isso `atestado_por` é obrigatório: o cancelamento por
    inércia decide a vaga de alguém, e "o prazo venceu" não é uma pessoa responsável.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    inscricao = models.ForeignKey(Inscricao, on_delete=models.PROTECT, related_name="atestados")
    especie = models.CharField(
        max_length=40,
        choices=[
            (nomes.ATESTADO_NAO_ACESSO_AO_AMBIENTE, "Não acessou o ambiente"),
            (nomes.ATESTADO_AUSENCIA_NA_PRIMEIRA_SEMANA, "Ausente na primeira semana"),
            (nomes.ATESTADO_NAO_ENTREGA_PRESENCIAL, "Não entregou presencialmente"),
        ],
    )
    conclusao = models.TextField()
    # **Copiada do conteúdo publicado**, e não referenciada por identidade: o atestado precisa dizer
    # contra qual prazo a conclusão foi tirada, e uma Retificação posterior não pode reescrever o
    # que a pessoa competente leu quando concluiu.
    referencia_do_prazo = models.TextField()
    atestado_por = models.CharField(max_length=255)
    atestado_em = models.DateTimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(especie__in=list(nomes.ESPECIES_DE_ATESTADO)),
                name="ck_atestado_especie",
            ),
            models.CheckConstraint(condition=~Q(conclusao=""), name="ck_atestado_com_conclusao"),
            models.CheckConstraint(condition=~Q(atestado_por=""), name="ck_atestado_com_atestante"),
        ]
        indexes = [models.Index(fields=["inscricao"], name="ix_atestado_inscricao")]

    def __str__(self):
        return f"{self.especie} — {self.inscricao_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("AtestadoDeFatoExterno é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("AtestadoDeFatoExterno é append-only")


class Convocacao(models.Model):
    """O ato que chama uma pessoa para a vaga que a `016` apurou como faltante (019, `FR-264`).

    **Três espécies, e a terceira não se chama `REGULARIZACAO`.** Convoca-se **para regularizar**, e
    o que a pessoa faz em seguida é a regularização: o mesmo termo para o ato e para o desfecho
    confunde tela e código.

    **A proveniência é obrigatória e é de três atos** (`FR-294`): a apuração que disse que faltava
    vaga, a ordem que disse quem é o próximo, e o corte que disse até onde a faixa alcança. Sem os
    três, o número que motivou a chamada não é reconstruível — e é o número que alguém contesta.

    **A apuração é FK, e a ordem e o corte são UUID.** A diferença não é descuido: a apuração é lida
    desta feature para dentro, e `PROTECT` sobre ela é o que impede apagar o ato que fundamentou a
    chamada; ordem e corte já são citados por identidade pela própria `016`, e repetir a FK aqui
    acrescentaria duas arestas ao grafo sem acrescentar garantia nenhuma.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="convocacoes")
    # Identidades publicadas, e não FKs para a elaboração — a razão que a `015`, a `016` e o `Corte`
    # já registram: Retificação acrescenta e remove itens sem criar ou apagar a linha do rascunho.
    perfil_id = models.UUIDField()
    marco_id = models.UUIDField()
    # `NULL` = ampla concorrência, a grafia do resto do sistema.
    lista_id = models.UUIDField(null=True, blank=True)
    inscricao = models.ForeignKey(Inscricao, on_delete=models.PROTECT, related_name="convocacoes")
    especie = models.CharField(
        max_length=24,
        choices=[
            (nomes.VAGA_INICIAL, "Para vaga inicial"),
            (nomes.SUPLENCIA, "Para vaga que vagou"),
            (nomes.PARA_REGULARIZAR, "Para regularizar o indeferimento"),
        ],
    )
    # **Informado por quem convoca** (`FR-269`), e nulo onde o Edital não publicou prazo. O sistema
    # não calcula dias úteis e não mantém calendário de feriados (`R-004`): sem calendário, calcular
    # "2 dias úteis" seria inventar feriado — e errar por um dia num prazo que decide vaga.
    vencimento = models.DateTimeField(null=True, blank=True)
    fundamento = models.TextField()
    apuracao = models.ForeignKey(
        "ocupacao.ApuracaoDeOcupacao", on_delete=models.PROTECT, related_name="convocacoes"
    )
    ato_de_ordenacao_id = models.UUIDField()
    # Nulo quando o marco não corta: ali não há faixa, e a `016` já apura ocupação sem corte.
    corte_id = models.UUIDField(null=True, blank=True)
    versao = models.ForeignKey(
        VersaoConsolidada, on_delete=models.PROTECT, related_name="convocacoes"
    )
    convocacao_anterior = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="sucessoras"
    )
    motivo_da_sucessao = models.TextField(blank=True, default="")
    # **A quantas chamadas desta pessoa neste recorte esta é.** Cresce a cada chamada **nova**; a
    # sucessora copia a da raiz que corrige, porque corrigir não é chamar de novo.
    #
    # **Existe porque a mesma pessoa é legitimamente chamada mais de uma vez** (`FR-283`): quem foi
    # reclassificado volta ao fim da fila e é chamado outra vez quando a vez dele chega. A primeira
    # versão tinha unicidade de raiz por pessoa e recorte, e ela transformava esse retorno em beco —
    # a segunda chamada só cabia como sucessora, e sucessão é correção: pularia as guardas de ordem.
    #
    # **O número é o que torna a regra exprimível no banco.** "Uma chamada em aberto por pessoa" não
    # é índice parcial possível — depende de haver ou não desfecho, que mora em outra tabela —, e a
    # aplicação a impõe. O que o banco garante é que duas chamadas da mesma pessoa no mesmo recorte
    # são chamadas **distintas**, e não uma duplicata.
    chamada = models.PositiveIntegerField(default=1)
    criado_por = models.CharField(max_length=255)
    criado_em = models.DateTimeField()

    class Meta:
        constraints = [
            # **Uma raiz por pessoa, recorte e número de chamada**, e as duas metades não são
            # redundantes: no PostgreSQL dois `NULL` não colidem, e uma só deixaria passar duas
            # raízes de ampla concorrência com o mesmo número no mesmo marco. É a cirurgia de
            # `uq_apuracao_primeira_por_marco`, e pela mesma razão.
            #
            # **O número entra na chave porque a mesma pessoa é chamada mais de uma vez.** Sem ele,
            # o reclassificado que volta à fila não teria como ser chamado de novo — e a única saída
            # seria declará-la sucessora, que é correção e pula as guardas de ordem.
            models.UniqueConstraint(
                fields=["edital", "perfil_id", "marco_id", "inscricao", "chamada"],
                condition=Q(convocacao_anterior__isnull=True, lista_id__isnull=True),
                name="uq_convocacao_raiz_por_recorte",
            ),
            models.UniqueConstraint(
                fields=["edital", "perfil_id", "marco_id", "lista_id", "inscricao", "chamada"],
                condition=Q(convocacao_anterior__isnull=True, lista_id__isnull=False),
                name="uq_convocacao_raiz_por_recorte_e_lista",
            ),
            # **A terceira metade: uma sucessora por convocação.** Sem ela, duas convocações
            # sucedem a mesma anterior e a pessoa fica com duas vigentes no recorte — e vigente é
            # derivada justamente de "ninguém me sucedeu".
            models.UniqueConstraint(
                fields=["convocacao_anterior"],
                condition=Q(convocacao_anterior__isnull=False),
                name="uq_convocacao_sucessora_unica",
            ),
            models.CheckConstraint(
                condition=Q(especie__in=list(nomes.ESPECIES_DE_CONVOCACAO)),
                name="ck_convocacao_especie",
            ),
            # Sucessão exige motivo, e a raiz não o tem. A mesma forma que o `AtoDeOrdenacao` e a
            # `ApuracaoDeOcupacao` usam — e a metade que falta na maioria das tentativas é a
            # segunda: raiz **com** motivo seria sucessão que não sucede nada.
            models.CheckConstraint(
                condition=(
                    Q(convocacao_anterior__isnull=True, motivo_da_sucessao="")
                    | Q(convocacao_anterior__isnull=False) & ~Q(motivo_da_sucessao="")
                ),
                name="ck_convocacao_sucessao",
            ),
            # O *"no interesse da Administração"* do 77/2026 entra aqui, e é o que faz a chamada ser
            # ato motivado em vez de linha numa planilha.
            models.CheckConstraint(
                condition=~Q(fundamento=""), name="ck_convocacao_com_fundamento"
            ),
        ]
        indexes = [
            models.Index(
                fields=["edital", "perfil_id", "marco_id", "lista_id"],
                name="ix_convocacao_recorte",
            ),
            models.Index(fields=["inscricao"], name="ix_convocacao_inscricao"),
        ]

    def __str__(self):
        return f"{self.especie} — {self.inscricao_id} em {self.marco_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("Convocacao é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("Convocacao é append-only")


class DesfechoDaConvocacao(models.Model):
    """O que a pessoa respondeu, ou o que a Administração concluiu (019, `FR-273`).

    **Um vigente por convocação**, e por constraint. Dois desfechos **paralelos** para a mesma
    chamada seriam duas respostas contraditórias sobre a mesma vaga, e o sistema não teria como
    dizer qual vale. Já o desfecho que **sucede** outro é um fato posterior, e a cadeia diz em que
    ordem os fatos aconteceram — é o que torna o cancelamento por inércia registrável sobre quem
    havia aceitado.

    **Sete espécies, e os dois últimos de exclusão são distintos de propósito** (`D-011`). *Não
    atendimento à convocação* e *cancelamento de matrícula por inércia* têm atores, prazos e
    fundamentos diferentes: o segundo depende de atestado de fato externo, o primeiro do vencimento
    informado. Colapsá-los num só apagaria norma.

    **Duas constraints dizem por forma o que o código também diz.** Inércia sem atestado e
    regularização sem Resultado sucessor não entram — nem por um caminho que não passe pela
    aplicação. É a mesma disciplina que faz `ck_resultado_origem` exigir fonte jurídica em todo
    sucessor.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    convocacao = models.ForeignKey(Convocacao, on_delete=models.PROTECT, related_name="desfechos")
    especie = models.CharField(
        max_length=24,
        choices=[
            (nomes.ACEITE, "Aceite"),
            (nomes.REGULARIZACAO, "Regularização"),
            (nomes.INDEFERIMENTO, "Indeferimento"),
            (nomes.DESISTENCIA_EXPRESSA, "Desistência expressa"),
            (nomes.NAO_ATENDIMENTO, "Não atendimento à convocação"),
            (nomes.INERCIA, "Cancelamento de matrícula por inércia"),
            (nomes.RECLASSIFICACAO, "Reclassificação"),
        ],
    )
    fundamento = models.TextField()
    atestado = models.ForeignKey(
        AtestadoDeFatoExterno,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="desfechos",
    )
    resultado_sucessor = models.ForeignKey(
        "resultados.ResultadoEtapa",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="desfechos_de_convocacao",
    )
    # O que foi escrito na porta da `016`. **Obrigatório**, e não anulável: as sete espécies têm
    # efeito — duas incluem e cinco excluem —, e um desfecho sem efeito deixaria a contagem
    # divergente sem nada que a explicasse. Numa tabela append-only essa linha não teria conserto:
    # `UPDATE` é proibido, e sucedê-la não desfaz a divergência que ela já produziu.
    efeito = models.ForeignKey(
        "ocupacao.EfeitoDeOcupacao", on_delete=models.PROTECT, related_name="desfechos"
    )
    # **A sucessão do desfecho, e a razão dela é a `US5`.** O cancelamento de matrícula por inércia
    # *"alcança quem já ocupava e desapareceu"* (§6 da spec) — e quem já ocupava costuma ter
    # aceitado a chamada. Sem sucessão, o aceite fecharia a convocação e a inércia posterior não
    # teria onde ser gravada: a `US5` ficaria estruturalmente impossível no caso que ela nomeia.
    #
    # **Não é correção, e é por isso que o campo se chama sucessão.** O aceite era verdadeiro quando
    # registrado; o que mudou foi o mundo depois dele. É a mesma forma que o `ResultadoEtapa` usa
    # para a superação por recurso — um fato jurídico novo sobre o mesmo objeto, com a linha
    # anterior intacta e legível.
    #
    # **A `FR-273` continua valendo**: há no máximo um desfecho **vigente** por convocação, como há
    # uma apuração vigente por recorte e uma ordem vigente por marco.
    desfecho_anterior = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="sucessores"
    )
    motivo_da_sucessao = models.TextField(blank=True, default="")
    registrado_por = models.CharField(max_length=255)
    registrado_em = models.DateTimeField()

    class Meta:
        constraints = [
            # **Um desfecho raiz por convocação** (`FR-273`), e os sucessores fora do índice: o que
            # a regra proíbe é duas respostas paralelas para a mesma chamada, e não o fato novo que
            # sucede o que foi respondido.
            models.UniqueConstraint(
                fields=["convocacao"],
                condition=Q(desfecho_anterior__isnull=True),
                name="uq_desfecho_por_convocacao",
            ),
            # Um sucessor por desfecho — a mesma cirurgia de `uq_apuracao_sucessora_unica`, e pela
            # mesma razão: sem ela, dois sucessores do mesmo desfecho dariam dois vigentes.
            models.UniqueConstraint(
                fields=["desfecho_anterior"],
                condition=Q(desfecho_anterior__isnull=False),
                name="uq_desfecho_sucessor_unico",
            ),
            models.CheckConstraint(
                condition=(
                    Q(desfecho_anterior__isnull=True, motivo_da_sucessao="")
                    | Q(desfecho_anterior__isnull=False) & ~Q(motivo_da_sucessao="")
                ),
                name="ck_desfecho_sucessao",
            ),
            models.CheckConstraint(
                condition=Q(especie__in=list(nomes.ESPECIES_DE_DESFECHO)),
                name="ck_desfecho_especie",
            ),
            # A `FR-277` dita por forma, e não só por código: fato externo sem atestante não entra.
            models.CheckConstraint(
                condition=~Q(especie=nomes.INERCIA) | Q(atestado__isnull=False),
                name="ck_desfecho_inercia_exige_atestado",
            ),
            # A `D-008` dita por forma: a regularização sucede o Resultado pelo mecanismo da `018`,
            # e sem o sucessor ela seria uma inclusão na contagem sem habilitação que a sustente.
            models.CheckConstraint(
                condition=~Q(especie=nomes.REGULARIZACAO) | Q(resultado_sucessor__isnull=False),
                name="ck_desfecho_regularizacao_exige_sucessor",
            ),
            models.CheckConstraint(condition=~Q(fundamento=""), name="ck_desfecho_com_fundamento"),
        ]

    def __str__(self):
        return f"{self.especie} — convocação {self.convocacao_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("DesfechoDaConvocacao é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("DesfechoDaConvocacao é append-only")


class ComunicacaoEmitida(models.Model):
    """Que o sistema **enviou** — não que chegou (019, `D-009`, `FR-288a`).

    **`enviado_em` é nulo enquanto o envio não teve sucesso**, e é essa nulidade que sustenta o
    estado *"convocado, prazo não iniciado"* (`R-009`). Sem ele, falha de infraestrutura fica
    indistinguível de silêncio da pessoa — e o desfecho que decorre disso é perda de vaga.

    **Nenhum campo diz recebido, lido ou entregue.** Não é omissão: é a `UX-039`, e o campo que não
    existe é a metade da garantia. A outra metade é a varredura sobre as telas, porque prosa mente
    sem precisar de coluna.

    **A falha não apaga o ato.** A convocação continua praticada; o que se registra aqui é que a
    emissão não completou, com o detalhe técnico — e sem dado pessoal, que viajaria para o log.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    convocacao = models.ForeignKey(
        Convocacao, on_delete=models.PROTECT, related_name="comunicacoes"
    )
    # Lida do conteúdo publicado, e nunca escolhida aqui: as duas grafias moram em
    # `publicacoes/domain/vocabulario_da_regra.py`, onde o publicado as define.
    forma = models.CharField(max_length=32)
    # Vazio quando a forma é publicação: ali não há destinatário individual, e inventar um faria a
    # trilha afirmar um endereçamento que não houve.
    destinatario = models.CharField(max_length=255, blank=True, default="")
    # **Onde a convocação foi publicada**, quando a forma é publicação. Vazio na mensagem
    # individual, onde quem recebe é uma pessoa e não o público.
    #
    # **Existe porque o sistema não publica no site do certame** (`R-007` não lhe deu essa
    # capacidade), e sem a referência a emissão por publicação seria um registro de que algo
    # aconteceu em lugar nenhum: o prazo do 69/2026 começaria a correr sem que a convocação tivesse
    # aparecido. É a mesma forma do `referencia_do_prazo` do atestado — quem pratica o ato declara
    # onde ele aconteceu, e o registro guarda a declaração.
    referencia_da_publicacao = models.TextField(blank=True, default="")
    enviado_em = models.DateTimeField(null=True, blank=True)
    resultado = models.CharField(
        max_length=16, choices=[("ENVIADA", "Enviada"), ("FALHA", "Falha")]
    )
    detalhe_tecnico = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(resultado__in=["ENVIADA", "FALHA"]), name="ck_comunicacao_resultado"
            ),
            # **Enviada exige instante, e falha não o tem.** É a forma que impede o estado que a
            # `R-009` existe para distinguir de virar mentira: uma comunicação marcada `ENVIADA`
            # sem instante faria o prazo correr a partir de nada.
            models.CheckConstraint(
                condition=(
                    Q(resultado="ENVIADA", enviado_em__isnull=False)
                    | Q(resultado="FALHA", enviado_em__isnull=True)
                ),
                name="ck_comunicacao_enviada_tem_instante",
            ),
            # **Publicação sem referência não publica nada**, e o prazo do 69/2026 corre do envio:
            # gravar `ENVIADA` ali iniciaria o prazo de uma convocação que ninguém viu. A `FALHA`
            # fica de fora porque ela registra justamente que a emissão não completou.
            models.CheckConstraint(
                condition=(
                    ~Q(forma="PUBLICATION") | Q(resultado="FALHA") | ~Q(referencia_da_publicacao="")
                ),
                name="ck_comunicacao_publicacao_com_referencia",
            ),
        ]
        indexes = [models.Index(fields=["convocacao"], name="ix_comunicacao_convocacao")]

    def __str__(self):
        return f"{self.forma} {self.resultado} — convocação {self.convocacao_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("ComunicacaoEmitida é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("ComunicacaoEmitida é append-only")
