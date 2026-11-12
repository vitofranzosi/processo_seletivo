"""A apuração de ocupação e o movimento de vaga — os dois append-only (016, `D-008`).

**Ato, e não projeção.** A decisão do usuário de 12/09/2026 fechou que a apuração é ato sucedido a
cada mudança, como a ordem da `015` e o corte da `014` já são. Projeção foi recusada pelo que ela
perde: o número de ontem não é recuperável se os atos-fonte mudarem de leitura, e ocupação é
exatamente o número que alguém vai contestar.

**Vigência e obsolescência não são colunas.** Mantê-las exigiria `UPDATE`, operação proibida nestas
tabelas — o provisionamento instala e verifica a proibição. Vigente é a apuração que ninguém
sucedeu no recorte; obsolescência é **calculada**, com as causas nomeadas, em
`application/selectors.py`. Quem acrescentar a coluna não é barrado ao criá-la: é barrado quando
tentar atualizá-la, que é o modo de falha mais tardio possível.
"""

import uuid

from django.db import models
from django.db.models import F, Q

from processo_seletivo.ocupacao.domain import nomes
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models import VersaoConsolidada


class ApuracaoDeOcupacao(models.Model):
    """Quantas vagas um recorte publicou, quantas tem efetivamente, e quantas estão ocupadas.

    **Quatro quantidades são colunas e a quinta não é.** `faltando` é
    `efetivas - ocupadas - nao_preenchidas`, aritmética da mesma linha — guardá-la seria armazenar o
    derivável. `efetivas` e `nao_preenchidas`, ao contrário, **precisam** ser colunas: dependem de
    somar registros de outras tabelas, e `CHECK` não agrega (016, `R-006`; 155, R-002).

    **`publicadas` nunca muda por movimento** (`FR-239a`). O que a reversão move é a quantidade
    efetiva; o publicado é intocável, e sem esta separação reverter faria o sistema afirmar que o
    Edital publicou um número que ele não publicou.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="apuracoes")
    # Identidades publicadas, e não FKs para a elaboração, pela razão que `AtoDeOrdenacao` e
    # `Corte` já registram: Retificação acrescenta e remove itens sem criar ou apagar a linha do
    # rascunho.
    perfil_id = models.UUIDField()
    marco_id = models.UUIDField()
    # `NULL` = ampla concorrência, a mesma grafia da ordem, do corte e do quadro de vagas.
    lista_id = models.UUIDField(null=True, blank=True)
    ato = models.ForeignKey(
        "classificacao.AtoDeOrdenacao", on_delete=models.PROTECT, related_name="apuracoes"
    )
    # Nula onde o recorte não tem corte: marco que não corta continua podendo ter ocupação apurada,
    # e nesse caso a faixa é o universo inteiro do ato.
    corte = models.ForeignKey(
        "classificacao.Corte",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="apuracoes",
    )
    versao = models.ForeignKey(
        VersaoConsolidada, on_delete=models.PROTECT, related_name="apuracoes"
    )
    apuracao_anterior = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="sucessoras"
    )
    motivo_da_sucessao = models.TextField(blank=True, default="")
    publicadas = models.PositiveIntegerField()
    efetivas = models.PositiveIntegerField()
    ocupadas = models.PositiveIntegerField()
    # **As vagas declaradas não preenchidas que esta apuração leu**, já líquidas dos desfazimentos
    # (155, R-002, FR-6326). Saem do "a ocupar" e **não** das efetivas: a vaga existe, e ninguém a
    # preencheu — reduzir as efetivas diria que ela deixou de existir. Padrão zero, que é o que toda
    # apuração anterior à `155` leu: a coluna entra sem reescrever linha, e o gatilho append-only
    # não dispara em `ADD COLUMN`.
    nao_preenchidas = models.PositiveIntegerField(default=0)
    # **Qual** linha do quadro foi lida. É a lição literal do `Corte`, que guarda o `rowId` do alvo
    # derivado: sem ela, retificado o quadro, não há como dizer se **esta** apuração ficou para
    # trás — a quantidade sozinha não identifica a linha (`FR-263`).
    linha_do_quadro_id = models.UUIDField(null=True, blank=True)
    # Quadro, declaração de reversão, recusas e `movimentosLidos` congelados no instante da
    # emissão. Os ids dos movimentos não são decoração: reproduzir é reler **aqueles** ids, e não
    # os movimentos de hoje (`FR-244`).
    universo = models.JSONField(default=dict)
    emitida_por = models.CharField(max_length=255)
    emitida_em = models.DateTimeField()

    class Meta:
        constraints = [
            # **As duas de primeira apuração não são redundantes**: no PostgreSQL dois `NULL` não
            # colidem, e uma só deixaria passar duas primeiras apurações de ampla concorrência no
            # mesmo marco. É a cirurgia de `uq_corte_raiz_por_marco`, e pela mesma razão —
            # verificada contra o banco antes de entrar aqui.
            models.UniqueConstraint(
                fields=["edital", "perfil_id", "marco_id"],
                condition=Q(apuracao_anterior__isnull=True, lista_id__isnull=True),
                name="uq_apuracao_primeira_por_marco",
            ),
            models.UniqueConstraint(
                fields=["edital", "perfil_id", "marco_id", "lista_id"],
                condition=Q(apuracao_anterior__isnull=True, lista_id__isnull=False),
                name="uq_apuracao_primeira_por_marco_e_lista",
            ),
            # **Uma sucessora por apuração.** Sem esta, duas apurações sucedem a mesma anterior e o
            # recorte fica com duas vigentes — e vigência é derivada justamente de "ninguém me
            # sucedeu". É a cópia de `uq_geracao_sucessora_unica`, que existe pela mesma razão.
            models.UniqueConstraint(
                fields=["apuracao_anterior"],
                condition=Q(apuracao_anterior__isnull=False),
                name="uq_apuracao_sucessora_unica",
            ),
            # O limite é contra **efetivas**, e não contra publicadas: recebida a reversão, a linha
            # geral passa de 28 para 35, e as 35 são ocupáveis. Comparar com `publicadas` recusaria
            # o ato justamente no cenário de sucesso da feature.
            #
            # **E as não preenchidas entram na mesma conta** (155, R-002): vaga declarada não
            # preenchida não é ocupável, e uma apuração que dissesse 3 ocupadas e 1 não preenchida
            # de 3 efetivas afirmaria quatro vagas onde há três. O nome fica, porque a garantia é a
            # mesma — ninguém ocupa além do que existe —, só que agora com as duas parcelas.
            models.CheckConstraint(
                condition=Q(ocupadas__lte=F("efetivas") - F("nao_preenchidas")),
                name="ck_apuracao_ocupadas_no_limite",
            ),
            # Sucessão exige motivo, e a primeira apuração não o tem. É a mesma forma que o
            # `AtoDeOrdenacao` usa para `motivo_da_sucessao`.
            models.CheckConstraint(
                condition=Q(apuracao_anterior__isnull=True) | ~Q(motivo_da_sucessao=""),
                name="ck_apuracao_sucessao_com_motivo",
            ),
        ]
        indexes = [
            models.Index(
                fields=["edital", "perfil_id", "marco_id", "lista_id"],
                name="ix_apuracao_recorte",
            )
        ]

    def __str__(self):
        return f"{self.perfil_id}/{self.lista_id or 'ampla'} — {self.ocupadas}/{self.efetivas}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("ApuracaoDeOcupacao é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("ApuracaoDeOcupacao é append-only")

    @property
    def faltando(self):
        """`efetivas - ocupadas - nao_preenchidas`, nunca negativo. Não é coluna, de propósito.

        A vaga declarada não preenchida deixa de contar como "a ocupar" (155, FR-6326): é o que
        impede a tela de pedir a alguém que chame para uma vaga que a comissão já declarou que
        ninguém vai preencher.
        """
        return max(self.efetivas - self.ocupadas - (self.nao_preenchidas or 0), 0)


class MovimentoDeVaga(models.Model):
    """A quantidade que sai de um recorte e entra em outro: a reversão de cota (016, `FR-246`).

    **Um sentido só, e a ausência do segundo é o achado da US4 da `016`.** A concorrência
    concomitante do item 8.9 do 28/2026 parecia ser o sentido oposto deste movimento, e não é: ela
    não transfere quantidade nenhuma. O autodeclarado que ocupa pela ampla apenas **não é
    computado** no preenchimento da reservada, que continua com as vagas que publicou. Aquilo é
    exclusão no cálculo de `ocupadas`, e mora em `apuracao.apurar`.

    **A segunda espécie é o ato contrário** (155, R-005): desfazer a destinação grava outro
    movimento, com a mesma quantidade e origem e destino trocados, citando o que desfaz. Não é o
    sentido oposto da concorrência concomitante — é a correção com rastro, como a da vaga acrescida.

    **Até a `155`, o movimento nascia com a apuração da origem**, na mesma transação que o
    determinava, e com o id gerado **antes** dela — para que ela o incluísse nos próprios
    `movimentosLidos` e já nascesse com a `efetivas` líquida da cessão. Os movimentos gravados assim
    continuam válidos e contam como destinação feita (FR-6316). Daqui em diante a destinação é ato
    próprio (R-001): `apuracao` passa a ser **a apuração lida pelo ato**, e o movimento carrega o
    recorte, o gatilho, o fundamento e a versão do Edital que o autorizaram.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # **Nula só onde a origem não tem apuração**: a lista de sorteio sem relação, que não chega a
    # ter ordem a apurar (155, R-007, D-011). Uma apuração artificial para preencher a coluna foi
    # recusada pelo usuário — ela afirmaria uma ocupação que ninguém apurou. A falta da apuração é
    # compensada pelo recorte próprio, e `ck_movimento_com_recorte` exige um dos dois.
    apuracao = models.ForeignKey(
        ApuracaoDeOcupacao,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="movimentos",
    )
    especie = models.CharField(
        max_length=32,
        choices=[
            (nomes.MOVIMENTO_REVERSAO, "Reversão de cota"),
            (nomes.MOVIMENTO_DESFAZIMENTO, "Desfazimento da reversão"),
        ],
    )
    # **O recorte do próprio movimento** (155, R-001). Nulo nos movimentos anteriores à `155`, que o
    # liam pela apuração; preenchido nos novos. Identidades publicadas, e não FKs para a
    # elaboração, pela razão que a apuração registra. Toda leitura por recorte pergunta pelos dois
    # caminhos — `apuracao__...` **ou** estes —, e uma varredura prende que nenhuma ficou para trás.
    edital = models.ForeignKey(
        Edital,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="movimentos_de_vaga",
    )
    perfil_id = models.UUIDField(null=True, blank=True)
    marco_id = models.UUIDField(null=True, blank=True)
    origem_lista_id = models.UUIDField(null=True, blank=True)
    destino_lista_id = models.UUIDField(null=True, blank=True)
    quantidade = models.PositiveIntegerField()
    causa = models.TextField()
    # O gatilho que o Edital declarou e sob o qual o ato moveu a vaga. Vazio nos anteriores à `155`:
    # eles não o guardavam, e preenchê-los agora seria `UPDATE` numa tabela append-only — além de
    # afirmar, depois do fato, uma leitura que o ato não registrou.
    gatilho = models.CharField(
        max_length=32,
        blank=True,
        default="",
        choices=[
            (nomes.REVERSAO_POR_ESGOTAMENTO, "Por esgotamento da lista reservada"),
            (nomes.REVERSAO_POR_SALDO, "Pelo saldo não preenchido"),
        ],
    )
    # A frase publicada da reversão, ou o motivo do desfazimento (FR-6310). Obrigatório nos novos —
    # `ck_movimento_com_fundamento` — e vazio nos antigos, que tinham só a `causa`.
    fundamento = models.TextField(blank=True, default="")
    # A versão do Edital cuja declaração o ato leu (FR-6310, FR-6342): uma Retificação posterior
    # pode trocar a reversão, e a pergunta "sob que norma esta vaga saiu da reserva" continua tendo
    # resposta.
    versao = models.ForeignKey(
        VersaoConsolidada,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="movimentos_de_vaga",
    )
    desfaz = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="desfazimentos"
    )
    registrado_por = models.CharField(max_length=255)
    registrado_em = models.DateTimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(quantidade__gt=0), name="ck_movimento_quantidade_positiva"
            ),
            # As espécies eram só *choices*, e *choices* o banco não vê. Com duas, uma terceira
            # escrita por engano seria lida pela apuração como movimento — a forma de
            # `ck_acrescimo_especie`.
            models.CheckConstraint(
                condition=Q(especie__in=list(nomes.ESPECIES_DE_MOVIMENTO)),
                name="ck_movimento_especie",
            ),
            # **A apuração ou o recorte, e nunca nenhum dos dois** (155, R-001). Sem uma das duas
            # portas, o movimento não alcançaria recorte nenhum: nenhuma apuração o leria, e a vaga
            # teria saído da reserva sem chegar a lugar algum.
            models.CheckConstraint(
                condition=Q(apuracao__isnull=False)
                | Q(edital__isnull=False, perfil_id__isnull=False, marco_id__isnull=False),
                name="ck_movimento_com_recorte",
            ),
            # O desfazimento cita o movimento que desfaz, e a reversão não cita nenhum. Sem a
            # citação, a trava do saldo somaria desfazimentos de nada (a lição do acréscimo).
            # Escrita como "não desfazimento ⇔ sem citação", e não pela lista das espécies, para
            # que a espécie desconhecida seja recusada só por `ck_movimento_especie`: com as duas
            # disparando, a recusa nomearia a errada.
            models.CheckConstraint(
                condition=(~Q(especie=nomes.MOVIMENTO_DESFAZIMENTO) & Q(desfaz__isnull=True))
                | Q(especie=nomes.MOVIMENTO_DESFAZIMENTO, desfaz__isnull=False),
                name="ck_desfazimento_cita_o_movimento",
            ),
            # **Fundamento nos novos**, reconhecidos pelo recorte próprio. Os antigos não o tinham,
            # e exigir dos dois tornaria inválida, pela migration, linha que já foi lida.
            models.CheckConstraint(
                condition=Q(edital__isnull=True) | ~Q(fundamento=""),
                name="ck_movimento_com_fundamento",
            ),
            # Origem e destino distintos. **`NULL` exige o cuidado de sempre**: em SQL,
            # `NULL = NULL` não é verdadeiro, então a comparação direta deixaria passar
            # `(NULL, NULL)` — a ampla cedendo para a ampla. As duas metades abaixo cobrem isso.
            models.CheckConstraint(
                condition=(
                    Q(origem_lista_id__isnull=True, destino_lista_id__isnull=False)
                    | Q(origem_lista_id__isnull=False, destino_lista_id__isnull=True)
                    | (
                        Q(origem_lista_id__isnull=False, destino_lista_id__isnull=False)
                        & ~Q(origem_lista_id=F("destino_lista_id"))
                    )
                ),
                name="ck_movimento_recortes_distintos",
            ),
        ]
        indexes = [
            models.Index(fields=["destino_lista_id"], name="ix_movimento_destino"),
            # A leitura pelo recorte próprio, que a apuração faz a cada emissão.
            models.Index(fields=["edital", "perfil_id", "marco_id"], name="ix_movimento_recorte"),
        ]

    def __str__(self):
        return f"{self.especie} {self.quantidade}: {self.origem_lista_id} → {self.destino_lista_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("MovimentoDeVaga é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("MovimentoDeVaga é append-only")


class EfeitoDeOcupacao(models.Model):
    """A porta por onde a `019` mexe na contagem: uma inscrição sai do conjunto de ocupantes, ou
    entra nele (019, `R-003`).

    **Mora aqui, e não em `convocacao`, por causa do grafo de migrations.** Uma FK de `ocupacao`
    para a feature nova inverteria a dependência exatamente onde ela é irreversível: a `016`
    passaria a não poder migrar sem a `019`. O ato de origem entra como **UUID opaco mais rótulo** —
    é o mesmo recurso que `perfil_id` e `marco_id` já usam nesta app, pela mesma razão.

    **A `016` não sabe o que é convocação.** Ela sabe que uma inscrição foi excluída ou incluída,
    com fundamento e proveniência. Quem dá sentido ao fundamento é quem o escreveu — e é por isso
    que `rotulo_da_origem` existe: sem ele a trilha diria "efeito de origem
    `3f2a…`", que não é linguagem humana nenhuma (`FR-296`).

    **Nenhuma unicidade por inscrição e recorte, e a ausência é deliberada.** Duas exclusões da
    mesma pessoa em ciclos diferentes são fatos distintos, e os dois aconteceram. O que a apuração
    faz com eles é **conjunto**, não soma — e é isso que evita o `−2` que a `R-001` nomeia.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="efeitos_de_ocupacao")
    perfil_id = models.UUIDField()
    marco_id = models.UUIDField()
    # `NULL` = ampla concorrência, a mesma grafia do resto do sistema.
    lista_id = models.UUIDField(null=True, blank=True)
    # **Identidade, e não FK**: é por esta coluna que `ocupacao` deixa de depender de `inscricoes`
    # para registrar efeito. A FK existe do outro lado, em `convocacao.Convocacao`, onde o ato que
    # alcança a pessoa é praticado.
    inscricao_id = models.UUIDField()
    especie = models.CharField(
        max_length=16,
        choices=[
            (nomes.EFEITO_EXCLUSAO, "Exclusão do conjunto de ocupantes"),
            (nomes.EFEITO_INCLUSAO, "Inclusão no conjunto de ocupantes"),
        ],
    )
    fundamento = models.TextField()
    # O desfecho que o produziu, **opaco**. Não é FK, e a ausência é a decisão (`R-003`).
    ato_de_origem_id = models.UUIDField()
    rotulo_da_origem = models.CharField(max_length=120)
    registrado_por = models.CharField(max_length=255)
    registrado_em = models.DateTimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(especie__in=list(nomes.ESPECIES_DE_EFEITO)),
                name="ck_efeito_especie",
            ),
            # Fundamento é obrigatório, e vazio não é fundamento. A mesma forma que
            # `ck_apuracao_sucessao_com_motivo` usa: o `CHECK` é o que impede a string vazia de
            # entrar por um caminho que não passe pela aplicação.
            models.CheckConstraint(condition=~Q(fundamento=""), name="ck_efeito_com_fundamento"),
            models.CheckConstraint(
                condition=~Q(rotulo_da_origem=""), name="ck_efeito_com_rotulo_da_origem"
            ),
        ]
        indexes = [
            # A leitura que a apuração faz: todos os efeitos do recorte, na ordem em que foram
            # registrados. Sem ele, cada emissão varreria a tabela inteira.
            models.Index(
                fields=["edital", "perfil_id", "marco_id", "lista_id"],
                name="ix_efeito_recorte",
            )
        ]

    def __str__(self):
        return f"{self.especie} {self.inscricao_id} — {self.rotulo_da_origem}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("EfeitoDeOcupacao é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("EfeitoDeOcupacao é append-only")


class AcrescimoDeVagas(models.Model):
    """A vaga que entra num recorte depois da publicação, e o ato contrário que a devolve (097).

    **É fato operacional, e não norma** (`D-001`). O Edital continua dizendo as vagas que publicou;
    este registro diz que um fato de fora o completou — no TMD, a matrícula que não se efetivou no
    Edital regular libera a vaga aqui. Retificar as vagas a cada chamada usaria ato normativo
    público, com versão e documento, para registrar um fato de outro certame (`DP-05`).

    **Não é `MovimentoDeVaga`** (`T-001`). O movimento nasce com a apuração que o causa, move vaga
    entre dois recortes e não tem texto; este precede a apuração que o lê — pode nem produzi-la, se
    outra causa a deixou obsoleta —, não tem recorte de origem e carrega origem e fundamento.
    Afrouxar as três constraints do movimento para caber nele apagaria o que elas protegem.

    **Uma tabela para as duas espécies.** Acréscimo e desfazimento são lidos pela mesma conta,
    congelados na mesma lista e mostrados na mesma linha do tempo. A quantidade é sempre positiva,
    e o sinal vem da espécie: um `-1` digitado seria desfazimento sem motivo nem citação.

    **O que o banco não garante, a aplicação garante sob a trava do Processo**: que o desfazimento
    não passe do que resta do acréscimo, e que não tire a vaga de quem já foi chamado (`FR-2462`).
    `CHECK` não agrega.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="acrescimos_de_vagas")
    perfil_id = models.UUIDField()
    marco_id = models.UUIDField()
    # **O recorte exato em que foi registrado** (`T-002`). A ampla tem duas grafias — o recorte nulo
    # e a Modalidade declarada como ampla —, e gravar "na linha geral" faria a vaga valer nas duas.
    lista_id = models.UUIDField(null=True, blank=True)
    especie = models.CharField(
        max_length=16,
        choices=[(nomes.ACRESCIMO, "Acréscimo"), (nomes.DESFAZIMENTO, "Desfazimento")],
    )
    quantidade = models.PositiveIntegerField()
    origem = models.TextField(blank=True)
    # O porquê do acréscimo, ou o motivo do desfazimento. Um campo para os dois, porque os dois
    # respondem a mesma pergunta — por que este número mudou —, e a trilha os lê no mesmo lugar.
    fundamento = models.TextField()
    referencia = models.CharField(max_length=255, blank=True)
    desfaz = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="desfazimentos"
    )
    # **A versão que declarou o cadastro de reserva que autorizou o ato** (`FR-2463`). Uma
    # Retificação posterior pode mudar a reserva; a pergunta "com que norma isto foi aceito"
    # continua tendo resposta.
    versao = models.ForeignKey(
        VersaoConsolidada, on_delete=models.PROTECT, related_name="acrescimos_de_vagas"
    )
    registrado_por = models.CharField(max_length=255)
    registrado_em = models.DateTimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(quantidade__gt=0), name="ck_acrescimo_quantidade_positiva"
            ),
            models.CheckConstraint(
                condition=Q(especie__in=list(nomes.ESPECIES_DE_ACRESCIMO)),
                name="ck_acrescimo_especie",
            ),
            models.CheckConstraint(
                condition=Q(especie=nomes.DESFAZIMENTO) | (~Q(origem="") & Q(desfaz__isnull=True)),
                name="ck_acrescimo_com_origem",
            ),
            models.CheckConstraint(
                condition=Q(especie=nomes.ACRESCIMO) | (Q(desfaz__isnull=False) & Q(origem="")),
                name="ck_desfazimento_cita_o_acrescimo",
            ),
            models.CheckConstraint(condition=~Q(fundamento=""), name="ck_acrescimo_com_fundamento"),
        ]
        indexes = [
            models.Index(
                fields=["edital", "perfil_id", "marco_id", "lista_id"], name="ix_acrescimo_recorte"
            ),
        ]

    def __str__(self):
        return f"{self.especie} {self.quantidade} no marco {self.marco_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("AcrescimoDeVagas é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("AcrescimoDeVagas é append-only")


class VagaNaoPreenchida(models.Model):
    """A vaga que ninguém vai preencher, declarada por ato, e o ato contrário (155, R-002, D-003).

    **Não é acréscimo negativo.** Reduzir as efetivas, como um desfazimento de acréscimo, diria que
    a vaga deixou de existir; ela existe e não foi preenchida, e é isso que o relatório e a página
    pública precisam poder dizer (FR-6326). A apuração lê a soma em `nao_preenchidas`, que sai do
    "a ocupar" e deixa as efetivas como estão.

    **Não é `MovimentoDeVaga`**: nada sai de um recorte para outro. E não é coluna da apuração
    sozinha: a declaração precede a apuração que a lê, tem fundamento e autor, e se desfaz — a
    forma de `AcrescimoDeVagas`, com uma tabela para as duas espécies e a quantidade sempre
    positiva, o sinal vindo da espécie.

    **O recorte é o exato, e a linha geral é `lista_id` nulo** (D-014): a declaração vale para a
    ampla sem ninguém que ainda possa ocupá-la, inclusive a que recebeu vaga destinada (FR-6324).

    **O que o banco não garante, a aplicação garante sob a trava do Processo**: que a declaração não
    passe do saldo do recorte, e que o desfazimento não passe do que resta dela. `CHECK` não agrega.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(
        Edital, on_delete=models.PROTECT, related_name="vagas_nao_preenchidas"
    )
    perfil_id = models.UUIDField()
    marco_id = models.UUIDField()
    lista_id = models.UUIDField(null=True, blank=True)
    # A apuração que o ato leu. **Nula só no sorteio sem relação** (R-007), onde a origem não tem
    # apuração — pela razão que o movimento registra.
    apuracao = models.ForeignKey(
        ApuracaoDeOcupacao,
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="declaracoes_de_nao_preenchida",
    )
    especie = models.CharField(
        max_length=16,
        choices=[
            (nomes.NAO_PREENCHIDA_DECLARACAO, "Declaração de vaga não preenchida"),
            (nomes.NAO_PREENCHIDA_DESFAZIMENTO, "Desfazimento da declaração"),
        ],
    )
    desfaz = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="desfazimentos"
    )
    quantidade = models.PositiveIntegerField()
    # O porquê da declaração, ou o motivo do desfazimento. **Escrito e obrigatório** (FR-6323):
    # declarar que uma vaga não será preenchida sem dizer por quê é o "por padrão" que a spec veda.
    fundamento = models.TextField()
    # A versão do Edital lida pelo ato (FR-6325): é ela que diz se havia reversão declarada.
    versao = models.ForeignKey(
        VersaoConsolidada, on_delete=models.PROTECT, related_name="vagas_nao_preenchidas"
    )
    registrado_por = models.CharField(max_length=255)
    registrado_em = models.DateTimeField()

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=Q(quantidade__gt=0), name="ck_nao_preenchida_quantidade_positiva"
            ),
            models.CheckConstraint(
                condition=Q(especie__in=list(nomes.ESPECIES_DE_NAO_PREENCHIDA)),
                name="ck_nao_preenchida_especie",
            ),
            # Na forma da do movimento, pela mesma razão: a espécie desconhecida é recusada só pela
            # constraint da espécie.
            models.CheckConstraint(
                condition=(~Q(especie=nomes.NAO_PREENCHIDA_DESFAZIMENTO) & Q(desfaz__isnull=True))
                | Q(especie=nomes.NAO_PREENCHIDA_DESFAZIMENTO, desfaz__isnull=False),
                name="ck_nao_preenchida_desfazimento_cita",
            ),
            models.CheckConstraint(
                condition=~Q(fundamento=""), name="ck_nao_preenchida_com_fundamento"
            ),
        ]
        indexes = [
            # A leitura que a apuração faz a cada emissão, como a do acréscimo.
            models.Index(
                fields=["edital", "perfil_id", "marco_id", "lista_id"],
                name="ix_nao_preenchida_recorte",
            ),
        ]

    def __str__(self):
        return f"{self.especie} {self.quantidade} no marco {self.marco_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("VagaNaoPreenchida é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("VagaNaoPreenchida é append-only")
