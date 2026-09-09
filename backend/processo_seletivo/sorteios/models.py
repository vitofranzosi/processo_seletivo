"""O compromisso do universo, o material da fonte e a proveniência do ato.

As quatro tabelas são append-only nas três camadas, como o acervo normativo inteiro: `save` e
`delete` recusam, a trigger recusa mesmo quem tem privilégio, e o papel de runtime não possui
`UPDATE` nem `DELETE` sobre elas (FR-007).

**Publicar é congelar**, e não há estado "publicada, não congelada": uma relação publicada e ainda
editável seria exatamente a janela que esta feature existe para fechar — universo conhecido,
compromisso ausente.

**O método não está aqui.** Ele é conteúdo canônico versionado do Edital, objeto do marco de
classificação, e alterá-lo é Retificação. Uma tabela de método seria um registro operacional que se
diz normativo: sem versão consolidada, sem autoridade signatária, fora do snapshot e fora do
alcance da gramática de endereçamento (D-013, FR-014). O que mora aqui é a **citação** dele:
`RelacaoDeHabilitados.metodo_hash`, gravado no instante do congelamento.
"""

import uuid

from django.db import models
from django.db.models import Q

from processo_seletivo.classificacao.models import AtoDeOrdenacao
from processo_seletivo.inscricoes.models import Inscricao
from processo_seletivo.processos.models import Edital
from processo_seletivo.publicacoes.models_retificacao import VersaoConsolidada


class RelacaoDeHabilitados(models.Model):
    """O universo comprometido de um recorte. Publicada, é imutável; corrigida, é sucedida."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="relacoes_de_sorteio")
    # Identidades publicadas, e não FKs para a elaboração — a mesma razão da `015`: a Retificação
    # pode acrescentar e remover itens sem criar ou apagar a linha correspondente no rascunho.
    perfil_id = models.UUIDField()
    # O marco é o terceiro eixo do recorte, e é ele que declara o método. Sem esta coluna o método
    # não seria localizável, e "o método vigente" acabaria resolvido no instante do sorteio — isto
    # é, depois da semente (D-014).
    marco_id = models.UUIDField()
    lista_id = models.UUIDField(null=True, blank=True)
    versao = models.ForeignKey(
        VersaoConsolidada, on_delete=models.PROTECT, related_name="relacoes_de_sorteio"
    )
    # O compromisso do método, gravado antes de existir semente. Com ele, a relação publicada
    # **prova** sob qual método aquele universo se comprometeu; sem ele, a escolha do método seria
    # feita depois de conhecido o efeito dela (FR-067).
    metodo_hash = models.CharField(max_length=64)
    criterio_de_projecao = models.TextField()
    # Redundância deliberada: o manifesto a publica, e ela é conferível contra as linhas.
    quantidade = models.PositiveIntegerField()
    # `canonical_sha256` da **projeção pública** da relação — número, nome e protocolo. Nada que o
    # portal não mostre entra nele, para que quem lê possa recalculá-lo em vez de aceitá-lo
    # (FR-006, R-015).
    resumo = models.CharField(max_length=64, db_index=True)
    publicada_em = models.DateTimeField()
    publicada_por = models.CharField(max_length=255)
    relacao_anterior = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="sucessoras"
    )
    motivo_da_sucessao = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            # **Uma raiz por recorte**, e a constraint parte em duas pela mesma cirurgia do
            # `AtoDeOrdenacao`: a primeira vale onde não há lista, a segunda onde há. A sucessão
            # ordena uma cadeia; ela não impede que nasçam duas — e duas cadeias vivas no mesmo
            # recorte seriam duas escolhas possíveis depois de conhecida a semente (FR-070, D-014).
            models.UniqueConstraint(
                fields=["edital", "perfil_id", "marco_id"],
                condition=Q(relacao_anterior__isnull=True, lista_id__isnull=True),
                name="uq_relacao_raiz_por_marco",
            ),
            models.UniqueConstraint(
                fields=["edital", "perfil_id", "marco_id", "lista_id"],
                condition=Q(relacao_anterior__isnull=True, lista_id__isnull=False),
                name="uq_relacao_raiz_por_marco_e_lista",
            ),
            models.UniqueConstraint(
                fields=["relacao_anterior"],
                condition=Q(relacao_anterior__isnull=False),
                name="uq_relacao_sucessora_unica",
            ),
            models.CheckConstraint(
                condition=Q(relacao_anterior__isnull=True) | ~Q(motivo_da_sucessao=""),
                name="ck_relacao_sucessao_com_motivo",
            ),
            # Relação vazia não é universo a comprometer (FR-009).
            models.CheckConstraint(condition=Q(quantidade__gte=1), name="ck_relacao_nao_vazia"),
        ]
        indexes = [models.Index(fields=["edital", "perfil_id", "marco_id", "lista_id"])]

    def __str__(self):
        return f"Relação de habilitados {self.id} — {self.quantidade} participantes"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("RelacaoDeHabilitados é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("RelacaoDeHabilitados é append-only")


class ParticipanteHabilitado(models.Model):
    """A inscrição que figura na relação, com o seu número público."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    relacao = models.ForeignKey(
        RelacaoDeHabilitados, on_delete=models.CASCADE, related_name="participantes"
    )
    # `PROTECT`: a inscrição não desaparece sob a relação que a cita.
    inscricao = models.ForeignKey(
        Inscricao, on_delete=models.PROTECT, related_name="participacoes_em_sorteio"
    )
    # Atribuído na projeção, por protocolo crescente. É o identificador que a chave do sorteio
    # endereça, e o único que a audiência precisa (D-004, R-011).
    numero_publico = models.PositiveIntegerField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["relacao", "inscricao"], name="uq_participante_por_relacao"
            ),
            models.UniqueConstraint(
                fields=["relacao", "numero_publico"], name="uq_numero_por_relacao"
            ),
        ]
        indexes = [models.Index(fields=["relacao", "numero_publico"])]

    def __str__(self):
        return f"Participante {self.numero_publico} da relação {self.relacao_id}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("ParticipanteHabilitado é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("ParticipanteHabilitado é append-only")


class OcorrenciaDaFonte(models.Model):
    """O material observado. Não é o ato, e observar não decide nada."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    fonte = models.CharField(max_length=255)
    referencia = models.CharField(max_length=255)
    # Como veio da fonte, sem interpretação. **A semente normalizada não mora aqui**: normalizar é
    # regra do método, esta linha é única por `(fonte, referência)`, e guardar a derivada aqui
    # congelaria a regra do primeiro método que observasse a ocorrência e a imporia, calada, a todo
    # método posterior que a citasse (D-016, FR-019).
    material_bruto = models.TextField()
    # **O instante mais cedo em que o evento externo pode ter acontecido**, conforme a fonte o
    # publica — e não quando nós o lemos (021, FR-016). A distinção é a garantia: comparar o
    # instante da **leitura** com o do congelamento permitiria fechar a relação já sabendo o
    # resultado da extração e registrá-lo no sistema depois.
    #
    # **O nome diz o que o dado é.** Ele se chamava `ocorrida_em`, e o adaptador da Loteria Federal
    # carimbava `20:00` sobre uma data sem horário: o campo afirmava um instante que a fonte nunca
    # publicou, e um congelamento no mesmo dia passava ou falhava por causa dele. Agora guarda o
    # limite inferior verdadeiro — o início do dia publicado —, e a comparação exige que o
    # congelamento seja anterior a ele.
    #
    # Nulo só quando a fonte não publica data alguma, e nesse caso a ocorrência não semeia sorteio
    # nenhum: o comando recusa em vez de aceitar uma garantia que não pode provar.
    ocorrida_nao_antes_de = models.DateTimeField(null=True, blank=True)
    observada_em = models.DateTimeField()
    observada_por = models.CharField(max_length=255)
    indisponivel = models.BooleanField(default=False)
    evidencia = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            # Observar duas vezes devolve a mesma linha, e é o que torna a observação idempotente.
            models.UniqueConstraint(fields=["fonte", "referencia"], name="uq_ocorrencia_por_fonte"),
            # Indisponibilidade sem evidência seria afirmação sem lastro sobre a única hipótese que
            # aciona a substituição (FR-015, R-006).
            models.CheckConstraint(
                condition=Q(indisponivel=False) | ~Q(evidencia=""),
                name="ck_indisponibilidade_com_evidencia",
            ),
        ]

    def __str__(self):
        return f"Ocorrência {self.fonte}/{self.referencia}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("OcorrenciaDaFonte é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("OcorrenciaDaFonte é append-only")


class Sorteio(models.Model):
    """A proveniência do ato: o que amarra relação e ocorrência à ordem produzida."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    edital = models.ForeignKey(Edital, on_delete=models.PROTECT, related_name="sorteios")
    perfil_id = models.UUIDField()
    marco_id = models.UUIDField()
    lista_id = models.UUIDField(null=True, blank=True)
    # A relação carrega recorte, versão e método. O sorteio **não recebe método**: ele consome o
    # que a relação comprometeu (FR-067).
    relacao = models.ForeignKey(
        RelacaoDeHabilitados, on_delete=models.PROTECT, related_name="sorteios"
    )
    ocorrencia = models.ForeignKey(
        OcorrenciaDaFonte, on_delete=models.PROTECT, related_name="sorteios"
    )
    # Copiado de `relacao.metodo_hash` e conferido contra ele na constituição: é a proveniência
    # congelada que permite reproduzir sem consultar conteúdo vigente (FR-039).
    metodo_hash = models.CharField(max_length=64)
    # A semente derivada, que é onde método e ocorrência se encontram (D-016).
    semente_normalizada = models.CharField(max_length=255)
    ato = models.OneToOneField(AtoDeOrdenacao, on_delete=models.PROTECT, related_name="sorteio")
    manifesto_hash = models.CharField(max_length=64)
    executado_em = models.DateTimeField()
    executado_por = models.CharField(max_length=255)
    sorteio_anterior = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.PROTECT, related_name="sucessores"
    )
    motivo_da_anulacao = models.TextField(blank=True, default="")

    class Meta:
        constraints = [
            # **A tupla da D-009 e da FR-031.** `perfil_id` e `lista_id` ficam fora porque a relação
            # já os carrega; o método também, e a razão mudou: desde a D-014 ele não é escolha do
            # sorteio, e sim citação da relação — mantê-lo aqui sugeriria uma liberdade que o modelo
            # deixou de ter.
            models.UniqueConstraint(
                fields=["relacao", "ocorrencia"],
                condition=Q(sorteio_anterior__isnull=True),
                name="uq_sorteio_raiz",
            ),
            models.UniqueConstraint(
                fields=["sorteio_anterior"],
                condition=Q(sorteio_anterior__isnull=False),
                name="uq_sorteio_sucessor_unico",
            ),
            models.CheckConstraint(
                condition=Q(sorteio_anterior__isnull=True) | ~Q(motivo_da_anulacao=""),
                name="ck_sorteio_sucessao_com_motivo",
            ),
        ]
        indexes = [models.Index(fields=["edital", "perfil_id", "marco_id", "lista_id"])]

    def __str__(self):
        return f"Sorteio {self.id} — {self.executado_em}"

    def save(self, *args, **kwargs):
        if not self._state.adding:
            raise TypeError("Sorteio é append-only")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise TypeError("Sorteio é append-only")
