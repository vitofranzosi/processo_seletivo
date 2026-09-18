"""O registro de que um arquivo de importação foi gerado — e **nada além dele** (031, `FR-447`).

**Uma tabela, e ela não guarda o arquivo.** O binário não é persistido (`FR-456`): ele é montado,
entregue na resposta e descartado. Guardá-lo criaria um acervo do artefato mais concentrado de dado
pessoal deste sistema, com política de retenção, expurgo e backup próprios — e não guardá-lo
**dispensa** essa política em vez de adiá-la. Precisar do arquivo de novo é gerá-lo de novo, e a
`FR-446` garante que sai idêntico.

**O registro não contém dado de candidato.** Ele diz quem gerou, quando, de qual Edital, para qual
população, quantas linhas e sob quais regras. Os requerimentos entram por **identificador**, e não
por conteúdo: auditar quem exportou não pode exigir uma segunda cópia do que foi exportado, que é
como o log vira o vazamento (§18).

**Append-only, e por duas camadas.** A tabela entra em `seguranca/papeis.py::TABELAS_APPEND_ONLY` —
o runtime fica sem `UPDATE` e sem `DELETE` — e a migration instala o gatilho que recusa a mutação
mesmo de quem tenha privilégio. Nenhuma das duas depende de a aplicação se comportar.
"""

import uuid

from django.db import models

from processo_seletivo.matriculas.domain import nomes
from processo_seletivo.processos.models import Edital


class GeracaoDeArquivo(models.Model):
    """Um ato de geração: quem, quando, de que população, e sob quais regras.

    **Não tem ciclo de vida.** A geração acontece ou é recusada — não há estado a transitar, e por
    isso não há `status` nem `revision` aqui. Inventá-los para caber no molde dos outros agregados
    seria manter estado que ninguém escreve.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # `PROTECT`: o Edital não desaparece sob o registro que o cita.
    edital = models.ForeignKey(
        Edital, on_delete=models.PROTECT, related_name="geracoes_de_matricula"
    )
    # **Qual conjunto, dito explicitamente** (`FR-433`). A referência é o marco de classificação ou
    # a publicação do resultado, conforme a espécie; o rótulo guarda como a tela a nomeou, para que
    # quem leia o registro meses depois não precise resolver um UUID para entender o que foi gerado.
    populacao_especie = models.CharField(
        max_length=20, choices=[(valor, valor) for valor in nomes.ESPECIES_DE_POPULACAO]
    )
    populacao_referencia = models.UUIDField()
    populacao_rotulo = models.CharField(max_length=255)
    quantidade_de_linhas = models.PositiveIntegerField()
    # **De qual versão do resultado saiu** (`FR-447`). Para a população de um resultado divulgado é
    # o resumo do conteúdo publicado — a versão daquele resultado, literalmente. Para a de
    # convocação é o resumo dos atos de ordenação que as chamadas citam, que é o que responde à
    # mesma pergunta: sob qual ordem aquelas pessoas foram chamadas.
    versao_do_resultado = models.CharField(max_length=64)
    # **Sob quais regras de conversão** (`FR-454`). Alterada à mão por quem mudar qualquer
    # serializador, no molde de `SCHEMA_VERSION` — ver a razão em `domain/colunas.py`.
    versao_dos_mapeamentos = models.PositiveIntegerField()
    # **Qual era o requerimento vigente de cada pessoa**, por identificador (§9, *Edge Cases*). Um
    # requerimento sucedido entre duas gerações faz a segunda trazer o vigente, e é esta lista que
    # permite responder *"qual era na primeira"* sem guardar uma segunda cópia da declaração.
    requerimentos = models.JSONField(default=list)
    gerado_por = models.CharField(max_length=255)
    gerado_em = models.DateTimeField()

    class Meta:
        verbose_name = "geração de arquivo de matrícula"
        verbose_name_plural = "gerações de arquivo de matrícula"
        indexes = [models.Index(fields=["edital", "-gerado_em"])]

    def __str__(self):
        return f"Geração de {self.quantidade_de_linhas} linha(s) — {self.edital_id}"
