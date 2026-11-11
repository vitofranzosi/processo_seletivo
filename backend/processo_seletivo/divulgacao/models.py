"""O ato de divulgar um resultado, a situação individual que ele congela e o seu documento.

As três tabelas são append-only nas três camadas: `save` e `delete` recusam, a trigger recusa
mesmo quem tem privilégio, e o papel de runtime não possui `UPDATE` nem `DELETE` sobre elas
(FR-040, FR-071). **Toda sucessão é linha nova** — não há coluna de vigência a alternar, e vigente
é a publicação que ninguém sucedeu (T-002).

**O individual não mora no conteúdo publicado.** `PublicacaoResultado.conteudo_publico` guarda só
o que foi divulgado; a situação de cada participante considerado vai para `SituacaoDivulgada`. A
separação é de tabela, e não de chave dentro de um mesmo registro: é o que permite à leitura
pública **não ter caminho** para o dado individual, em vez de tê-lo e confiar que ninguém o
percorre (T-010, T-013).

O agregado **não tem máquina de estados** porque não tem ciclo de vida: nasce publicado e é
sucedido por outra linha, ou não é (FR-046).
"""

import uuid

from django.db import models
from django.db.models import Q

from processo_seletivo.classificacao.models import AtoDeOrdenacao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital


class Natureza(models.TextChoices):
    """A ordem entre as duas tem sentido único: preliminar não sucede definitiva (D-007)."""

    PRELIMINAR = "PRELIMINAR", "Resultado preliminar"
    DEFINITIVA = "DEFINITIVA", "Resultado definitivo"


class PublicacaoResultado(models.Model):
    """O ato institucional de divulgação de um `AtoDeOrdenacao` (FR-001)."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(
        Edital, on_delete=models.PROTECT, related_name="publicacoes_de_resultado"
    )
    # `PROTECT` porque a origem não pode desaparecer sob a publicação que a cita.
    ato = models.ForeignKey(
        AtoDeOrdenacao, on_delete=models.PROTECT, related_name="publicacoes_de_resultado"
    )
    # Identidades publicadas, e não FKs para a elaboração — a mesma razão da 015: Retificação pode
    # acrescentar e remover itens sem criar ou apagar a linha correspondente no rascunho.
    perfil_id = models.UUIDField()
    marco_id = models.UUIDField()
    # A dimensão da lista de concorrência (021, D-015, FR-068). `NULL` = ampla concorrência, que é
    # o que toda publicação feita antes desta feature é.
    #
    # **A D-006 parou no ato, e a dimensão não parava ali.** Três atos raiz num marco exigem três
    # publicações; sem esta coluna a segunda lista batia em `uq_publicacao_raiz_por_marco` e o
    # certame com cotas sorteava sem conseguir divulgar.
    lista_id = models.UUIDField(null=True, blank=True)
    natureza = models.CharField(max_length=20, choices=Natureza.choices)
    publicacao_anterior = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="sucessoras",
    )
    # Os bytes canônicos **do que foi divulgado**, e nada além (T-003). Congelar a projeção é o
    # que impede uma correção futura de reescrever em silêncio o que já foi publicado.
    conteudo_publico = models.BinaryField()
    conteudo_publico_hash = models.CharField(max_length=64, db_index=True)
    publicado_por = models.CharField(max_length=255)
    publicado_em = models.DateTimeField()
    signatario_id = models.UUIDField()
    # Nome, cargo e ato de nomeação são persistidos: encerrar a autoridade ou cadastrar outra no
    # lugar não altera ato já praticado. O ato de nomeação chegou com a 060 (FR-1128); antes, só a
    # Publicação de Edital o guardava.
    signatario_nome = models.CharField(max_length=255)
    signatario_cargo = models.CharField(max_length=255)
    signatario_ato_de_nomeacao = models.CharField(max_length=255, blank=True, default="")
    # A unidade que praticou o ato, como estava no dia — as mesmas colunas de `Publicacao` (060,
    # FR-1128). O documento as lê do `conteudo_publico`; estas existem para consulta.
    unidade_codigo = models.CharField(max_length=100, blank=True, default="")
    unidade_sigla = models.CharField(max_length=30, blank=True, default="")
    unidade_nome = models.CharField(max_length=255, blank=True, default="")
    unidade_cabecalho = models.JSONField(default=list)
    unidade_local = models.CharField(max_length=120, blank=True, default="")
    # A declaração expressa de que o prazo recursal se encerrou, exigida **somente** quando a
    # natureza é definitiva e o marco não tem janela computável (FR-085, FR-086). Onde há janela, o
    # sistema verifica: pedir a declaração ali seria pedir à pessoa que respondesse pelo que a
    # máquina sabe — e reintroduziria, com mais passos, a afirmação sem lastro que o E2E17-005
    # registrou.
    #
    # Gravada no nascimento, e por isso persistida na publicação: quem a fez, quando e com que
    # fundamento. Sem os três, "declarou-se encerrado" seria afirmação sem autor.
    prazo_encerrado_declarado_em = models.DateTimeField(null=True, blank=True)
    prazo_encerrado_declarado_por = models.CharField(max_length=255, blank=True, default="")
    prazo_encerrado_fundamento = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            # **Duas parciais, pela cirurgia idêntica à do `AtoDeOrdenacao`.** A primeira mantém o
            # nome e a garantia de hoje para a publicação sem lista — e toda publicação existente
            # tem `lista_id NULL`, portanto continua sob exatamente a constraint que já a governava.
            models.UniqueConstraint(
                fields=["edital", "perfil_id", "marco_id"],
                condition=Q(publicacao_anterior__isnull=True, lista_id__isnull=True),
                name="uq_publicacao_raiz_por_marco",
            ),
            models.UniqueConstraint(
                fields=["edital", "perfil_id", "marco_id", "lista_id"],
                condition=Q(publicacao_anterior__isnull=True, lista_id__isnull=False),
                name="uq_publicacao_raiz_por_marco_e_lista",
            ),
            models.UniqueConstraint(
                fields=["publicacao_anterior"],
                condition=Q(publicacao_anterior__isnull=False),
                name="uq_publicacao_sucessora_unica",
            ),
            # A resposta a "o mesmo ato pode ser publicado duas vezes?": pode, **uma vez por
            # natureza** (D-007, FR-039). Não muda com a dimensão da lista, e não precisa mudar:
            # três listas são três atos distintos, e a duplicidade que esta constraint recusa
            # continua sendo a mesma (021, D-015).
            #
            # Um preliminar que ninguém contestou vira definitivo sem
            # que exista ato novo a emitir; a mesma natureza duas vezes é duplicidade, e o banco a
            # recusa — o que dá ao cenário das duas abas uma garantia de banco, e não só de
            # idempotência.
            models.UniqueConstraint(
                fields=["ato", "natureza"],
                name="uq_publicacao_por_ato_natureza",
            ),
            # Os três campos da declaração andam juntos ou não existem. Uma declaração com autor e
            # sem fundamento seria afirmação sem razão escrita, e uma com fundamento e sem autor
            # seria razão sem quem responda por ela — as duas metades de um ato que só vale
            # inteiro (FR-085).
            models.CheckConstraint(
                condition=(
                    Q(
                        prazo_encerrado_declarado_em__isnull=True,
                        prazo_encerrado_declarado_por="",
                        prazo_encerrado_fundamento="",
                    )
                    | Q(prazo_encerrado_declarado_em__isnull=False)
                    & ~Q(prazo_encerrado_declarado_por="")
                    & ~Q(prazo_encerrado_fundamento="")
                ),
                name="ck_declaracao_completa",
            ),
        ]
        indexes = [models.Index(fields=["edital", "perfil_id", "marco_id"])]

    def __str__(self):
        return f"{self.get_natureza_display()} — {self.publicado_em}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("PublicacaoResultado é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("PublicacaoResultado é append-only")


class SituacaoDivulgada(models.Model):
    """A situação de **uma** pessoa naquela divulgação — inclusive quem não recebeu posição.

    Não é segunda fonte de verdade (FR-058): nasce na mesma transação, do mesmo ato imutável que
    produziu a lista pública, e aponta para a publicação que a originou. O que a FR-058 proíbe é
    uma fonte **viva**, que mudasse com o ato enquanto a publicação permanece histórica.
    """

    class Situacao(models.TextChoices):
        CLASSIFICADA = "CLASSIFICADA", "Classificada"
        SEM_POSICAO = "SEM_POSICAO", "Sem posição"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # `CASCADE` descreve a pertinência — a projeção é parte da publicação e não tem vida sem ela.
    # Na prática nada é apagado: a publicação é append-only, e a exclusão não existe como operação.
    publicacao = models.ForeignKey(
        PublicacaoResultado, on_delete=models.CASCADE, related_name="situacoes"
    )
    # `PROTECT` pelo oposto: a Inscrição não pode desaparecer sob a divulgação que a nomeia.
    inscricao = models.ForeignKey(
        Inscricao, on_delete=models.PROTECT, related_name="situacoes_divulgadas"
    )
    situacao = models.CharField(max_length=20, choices=Situacao.choices)
    posicao = models.PositiveIntegerField(null=True, blank=True)
    compartilhada = models.BooleanField(default=False)
    # Já na apresentação institucional (`185,00`): texto, e não decimal — reformatar na leitura
    # seria decidir de novo o que o ato já decidiu.
    pontuacao = models.CharField(max_length=32, blank=True, default="")
    motivo = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["publicacao", "inscricao"],
                name="uq_situacao_por_publicacao_inscricao",
            )
        ]
        # Por este índice o acompanhamento encontra a linha da pessoa, sem varrer publicação.
        indexes = [models.Index(fields=["inscricao"])]

    def __str__(self):
        return f"{self.inscricao_id}: {self.situacao}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("SituacaoDivulgada é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("SituacaoDivulgada é append-only")


class DocumentoDoResultado(models.Model):
    """Os bytes do documento oficial, no molde de `DocumentoPublicado`.

    Tabela própria, e não coluna anulável na publicação: até a US4 as publicações nascem sem
    documento, e a ausência de linha representa isso sem deixar coluna a limpar depois (T-007).
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    publicacao = models.OneToOneField(
        PublicacaoResultado, on_delete=models.PROTECT, related_name="documento"
    )
    bytes = models.BinaryField()
    content_type = models.CharField(max_length=100, default="application/pdf")
    # Integridade, **não** unicidade: dois documentos idênticos são legítimos.
    documento_hash = models.CharField(max_length=64, db_index=True)

    def __str__(self):
        return f"Documento de {self.publicacao_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("DocumentoDoResultado é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("DocumentoDoResultado é append-only")


# ---------------------------------------------------------------------------
# A publicação das inscrições (148)
# ---------------------------------------------------------------------------


class NaturezaDasInscricoes(models.TextChoices):
    """As três naturezas, na ordem em que um certame as pratica — e a ordem tem sentido único.

    **"Homologação" é sempre das inscrições** (148, UX-461). A palavra já nomeia, no código e na
    tela, o ato sobre a revisão do Edital (`publicacoes.Homologacao`); aqui ela vive dentro de um
    agregado cujo nome diz de quê, e o rótulo a qualifica sempre.
    """

    RECEBIDAS = "RECEBIDAS", "Relação de inscrições recebidas"
    PRELIMINAR = "PRELIMINAR", "Resultado preliminar da análise das inscrições"
    HOMOLOGACAO = "HOMOLOGACAO", "Homologação das inscrições"


ORDEM_DAS_NATUREZAS = {
    NaturezaDasInscricoes.RECEBIDAS: 0,
    NaturezaDasInscricoes.PRELIMINAR: 1,
    NaturezaDasInscricoes.HOMOLOGACAO: 2,
}


class PublicacaoDasInscricoes(models.Model):
    """O ato público sobre as inscrições de um Edital — recebidas, preliminar ou homologação (148).

    **Não decide nada sobre inscrição nenhuma.** A decisão de deferir ou indeferir é o
    `ResultadoEtapa` da Etapa decisória que o Edital já declara, com motivo, sucessão e recurso;
    este ato a **publica**, de uma vez e para todos, e guarda o que publicou (D-001). Por isso não
    há estado novo na `Inscricao`: ele seria uma segunda resposta à mesma pergunta, e esbarraria no
    gatilho da inscrição enviada.

    **Uma cadeia por Edital, e não por Perfil.** A análise é por inscrição, e a comissão publica a
    relação do Edital inteiro, agrupada por Perfil. Corrigir é suceder — mesma natureza exige
    motivo —, e o anterior continua legível no mesmo endereço (D-006).

    **O documento mora na própria linha.** Ao contrário da divulgação de resultado, cuja publicação
    nasceu antes do documento, este ato nasce com ele: não há estado "sem documento" a representar,
    e uma tabela a mais seria um vínculo a manter sem nada a ganhar.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(
        Edital, on_delete=models.PROTECT, related_name="publicacoes_das_inscricoes"
    )
    natureza = models.CharField(max_length=20, choices=NaturezaDasInscricoes.choices)
    # A identidade **publicada** da Etapa decisória, e não chave estrangeira — pela mesma razão que
    # `ResultadoEtapa.etapa_id`: existe Etapa vigente sem linha em elaboração.
    etapa_id = models.UUIDField(null=True, blank=True)
    versao = models.ForeignKey(
        "publicacoes.VersaoConsolidada",
        on_delete=models.PROTECT,
        related_name="publicacoes_das_inscricoes",
    )
    publicacao_anterior = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="sucessoras",
    )
    motivo_da_sucessao = models.TextField(blank=True, default="")
    # O período de recurso do preliminar, **congelado** (D-002, FR-5413). `None` em
    # `admite_recurso` fora do preliminar; `False` quando quem publicou declarou que o Edital não
    # prevê recurso contra a análise; `True` com o Evento do Cronograma e o seu término.
    admite_recurso = models.BooleanField(null=True, blank=True)
    recurso_evento_id = models.UUIDField(null=True, blank=True)
    recurso_ate = models.DateTimeField(null=True, blank=True)
    quantidade = models.PositiveIntegerField()
    conteudo_publico = models.BinaryField()
    conteudo_publico_hash = models.CharField(max_length=64, db_index=True)
    documento = models.BinaryField()
    documento_hash = models.CharField(max_length=64)
    publicado_por = models.CharField(max_length=255)
    publicado_em = models.DateTimeField()
    signatario_id = models.UUIDField()
    signatario_nome = models.CharField(max_length=255)
    signatario_cargo = models.CharField(max_length=255)
    signatario_ato_de_nomeacao = models.CharField(max_length=255, blank=True, default="")
    unidade_codigo = models.CharField(max_length=100, blank=True, default="")
    unidade_sigla = models.CharField(max_length=30, blank=True, default="")
    unidade_nome = models.CharField(max_length=255, blank=True, default="")
    unidade_cabecalho = models.JSONField(default=list)
    unidade_local = models.CharField(max_length=120, blank=True, default="")

    class Meta:
        constraints = [
            # Uma raiz por Edital: a segunda "primeira publicação" de duas abas morre aqui, e não
            # numa cadeia bifurcada que ninguém saberia ler (FR-5406).
            models.UniqueConstraint(
                fields=["edital"],
                condition=Q(publicacao_anterior__isnull=True),
                name="uq_publicacao_das_inscricoes_raiz",
            ),
            models.UniqueConstraint(
                fields=["publicacao_anterior"],
                condition=Q(publicacao_anterior__isnull=False),
                name="uq_publicacao_das_inscricoes_sucessor",
            ),
            # O preliminar sempre tem a Etapa que ele publica; a relação de recebidas nunca tem.
            models.CheckConstraint(
                condition=~Q(natureza="PRELIMINAR") | Q(etapa_id__isnull=False),
                name="ck_preliminar_tem_etapa",
            ),
            models.CheckConstraint(
                condition=~Q(natureza="RECEBIDAS") | Q(etapa_id__isnull=True),
                name="ck_recebidas_sem_etapa",
            ),
            # O prazo é do preliminar, e só existe quando ele admite recurso.
            models.CheckConstraint(
                condition=Q(recurso_ate__isnull=True)
                | (Q(natureza="PRELIMINAR") & Q(admite_recurso=True)),
                name="ck_prazo_so_no_preliminar_que_admite",
            ),
            models.CheckConstraint(
                condition=Q(admite_recurso__isnull=True) | Q(natureza="PRELIMINAR"),
                name="ck_admite_recurso_so_no_preliminar",
            ),
            models.CheckConstraint(
                condition=Q(quantidade__gte=1), name="ck_publicacao_das_inscricoes_nao_vazia"
            ),
        ]
        indexes = [models.Index(fields=["edital", "publicado_em"])]

    def __str__(self):
        return f"{self.get_natureza_display()} — {self.publicado_em}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("PublicacaoDasInscricoes é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("PublicacaoDasInscricoes é append-only")


class InscricaoNaPublicacao(models.Model):
    """A situação de **uma** inscrição naquele ato — a projeção individual, nunca pública (148).

    Guarda o `ResultadoEtapa` de onde a situação veio, e é isso que torna a divergência derivável:
    o resultado sucedido depois da publicação deixa de ser o vigente, e a comparação o encontra sem
    que coluna alguma precise ser mantida (D-006, FR-5427).
    """

    class Situacao(models.TextChoices):
        RECEBIDA = "RECEBIDA", "Recebida"
        DEFERIDA = "DEFERIDA", "Deferida"
        INDEFERIDA = "INDEFERIDA", "Indeferida"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    publicacao = models.ForeignKey(
        PublicacaoDasInscricoes, on_delete=models.PROTECT, related_name="itens"
    )
    inscricao = models.ForeignKey(
        Inscricao, on_delete=models.PROTECT, related_name="publicacoes_das_inscricoes"
    )
    situacao = models.CharField(max_length=20, choices=Situacao.choices)
    resultado = models.ForeignKey(
        "resultados.ResultadoEtapa",
        null=True,
        blank=True,
        on_delete=models.PROTECT,
        related_name="publicacoes_das_inscricoes",
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["publicacao", "inscricao"], name="uq_inscricao_por_publicacao"
            ),
            # A indeferida sempre vem de um resultado: indeferir sem decisão seria o ato decidindo.
            models.CheckConstraint(
                condition=~Q(situacao="INDEFERIDA") | Q(resultado__isnull=False),
                name="ck_indeferida_tem_resultado",
            ),
        ]
        indexes = [models.Index(fields=["inscricao"])]

    def __str__(self):
        return f"{self.inscricao_id}: {self.situacao}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("InscricaoNaPublicacao é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("InscricaoNaPublicacao é append-only")
