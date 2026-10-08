"""A unidade que pratica o ato, e quem pode responder pelos atos dela (060).

**A Unidade materializa o escopo institucional, e não o substitui** (`D-001`). O código dela é o
valor de `institution_scope` que operadores, Processos, Editais e a trilha já carregam; nada aponta
para esta tabela por chave estrangeira. O escopo continua isolando, autorizando e numerando como
antes — o que a Unidade acrescenta é o que o documento oficial diz da unidade: o nome, as linhas do
cabeçalho e o local do ato, que até a 060 eram constantes do compositor.

**A Autoridade habilitada não é pessoa, cargo nem mandato** (`D-003`). É a resposta a uma pergunta
só: *quem pode ser escolhido para os atos desta unidade nesta data?* O Reitor que responde por um
Edital de campus é uma linha a mais naquele campus, e não uma hierarquia a inferir.

**Nada aqui se exclui.** A Publicação congela o identificador da autoridade, e a trilha aponta para
as duas pelo `id`; apagar uma linha deixaria o ato citando o nada. Retirar de uso é desativar a
Unidade ou encerrar a vigência da autoridade, e o banco recusa a exclusão por gatilho
(`unidades/0002`).
"""

import uuid

from django.db import models
from django.db.models import F, Q


class Unidade(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # O valor de `institution_scope`. Imutável: mudá-lo desligaria a Unidade de tudo o que o escopo
    # já marcou, sem que nada o acusasse — e é por isso que o gatilho o recusa (FR-1108).
    codigo = models.CharField(max_length=100, unique=True)
    sigla = models.CharField(max_length=30)
    nome = models.CharField(max_length=255)
    # As linhas que o nome ocupa no cabeçalho, uma ou duas. Quebrar o nome é decisão editorial de
    # documento oficial, e não refluxo: o compositor as imprime como estão (FR-1106).
    cabecalho = models.JSONField(default=list)
    # O local do ato no fecho do documento publicado — *"Vitória (ES)"* (FR-1113).
    local = models.CharField(max_length=120)
    ativa = models.BooleanField(default=True)
    registrada_em = models.DateTimeField()
    alterada_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["sigla"]
        constraints = [
            models.CheckConstraint(condition=~Q(codigo=""), name="ck_unidade_codigo_preenchido"),
            models.CheckConstraint(condition=~Q(nome=""), name="ck_unidade_nome_preenchido"),
            models.CheckConstraint(condition=~Q(local=""), name="ck_unidade_local_preenchido"),
        ]

    def __str__(self):
        return self.nome


class AutoridadeHabilitada(models.Model):
    # Gerado, nunca digitado nem exibido: é o que a Publicação congela em `signatory_id`, e é por
    # ele que a auditoria responde quem respondeu pelo ato (FR-1117).
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # A unidade **por cujos atos** responde — não a lotação (FR-1118). Nunca muda (FR-1121).
    unidade = models.ForeignKey(Unidade, on_delete=models.PROTECT, related_name="autoridades")
    # Cargo, nome e ato de nomeação no exercício de atribuição pública, e nada além (FR-1116). O
    # nome e o ato são opcionais pela razão da 054: enquanto o Cefor não os fornece, o fecho diz o
    # cargo, e um nome que não é nome seria pior que nenhum.
    cargo = models.CharField(max_length=255)
    nome = models.CharField(max_length=255, blank=True, default="")
    # Delegação de competência, quando houver, é dita aqui, em texto: o sistema a registra e não a
    # interpreta.
    ato_de_nomeacao = models.CharField(max_length=255, blank=True, default="")
    inicio_vigencia = models.DateField()
    # Inclusivo, e nulo quando aberto. Encerrar com fim hoje mantém a autoridade disponível hoje e a
    # retira amanhã (FR-1120).
    fim_vigencia = models.DateField(null=True, blank=True)
    cadastrada_por = models.CharField(max_length=255)
    cadastrada_em = models.DateTimeField()
    encerrada_por = models.CharField(max_length=255, blank=True, default="")
    encerrada_em = models.DateTimeField(null=True, blank=True)
    # O primeiro ato praticado com ela, gravado pela publicação sob a trava da linha. Coluna, e não
    # consulta às publicações, porque `unidades` não depende de quem a usa — e porque é ela que o
    # gatilho lê para tornar o registro imutável depois do primeiro uso (FR-1121, `D-004`).
    usada_em = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["cargo", "nome"]
        constraints = [
            models.CheckConstraint(condition=~Q(cargo=""), name="ck_autoridade_cargo_preenchido"),
            models.CheckConstraint(
                condition=Q(fim_vigencia__isnull=True) | Q(fim_vigencia__gte=F("inicio_vigencia")),
                name="ck_autoridade_fim_depois_do_inicio",
            ),
            # O que "encerrada" significa, dito no banco, no molde de
            # `ck_membro_inativacao_completa`: quem e quando andam juntos, e só existem com um fim
            # declarado.
            models.CheckConstraint(
                condition=Q(encerrada_em__isnull=True, encerrada_por="")
                | Q(encerrada_em__isnull=False, fim_vigencia__isnull=False) & ~Q(encerrada_por=""),
                name="ck_autoridade_encerramento_completo",
            ),
        ]
        indexes = [models.Index(fields=["unidade", "inicio_vigencia"])]

    def __str__(self):
        from processo_seletivo.unidades.domain.rotulos import quem_assinou

        return quem_assinou(self.nome, self.cargo)
