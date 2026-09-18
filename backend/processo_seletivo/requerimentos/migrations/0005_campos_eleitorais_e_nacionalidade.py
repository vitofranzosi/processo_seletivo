"""Os três campos eleitorais e o fechamento da lista de nacionalidade (031, `D-007`, `D-008`).

**Duas mudanças, e a segunda é a delicada.**

Os três eleitorais entram vazios, como todo campo novo de um formulário que já existe: ninguém os
declarou ainda, e nenhum Edital os exige para enviar. A `FR-382` da `029` recusa oito informações
*"nenhuma com destino na saída"* — estes não estavam naquela lista; só não tinham consumidor, e o
formato de importação do Registro Acadêmico é a finalidade que faltava.

**A nacionalidade fecha, e o que já foi declarado NÃO é reescrito.**

O campo foi texto livre por dois dias, e nele há *"Brasil"*, *"Brasileira"* e o que mais a pessoa
tiver digitado. A tentação é converter a coluna inteira. **Ela é recusada para o que já foi
enviado**, por duas razões que se somam:

- o gatilho `requerimento_enviado_imutavel` (migration `0002`) recusa `UPDATE` sobre requerimento
  enviado, e desabilitá-lo aqui seria contornar a garantia em vez de respeitá-la;
- a Constituição proíbe reescrever o que já produziu efeito. O requerimento enviado é peça de ato
  administrativo: o indeferimento se funda nele, e trocar a palavra que a pessoa escreveu apagaria
  a declaração dela.

Então **só o rascunho é convertido** — ele muda legitimamente, é isso que ser rascunho significa —,
e o enviado fica exatamente como está. A coluna 16 da exportação continua saindo certa porque quem
**lê** reconhece a grafia histórica (`FR-453`): *"brasil"*, *"brasileira"* e *"brasileiro"* emitem
`BR`, e o que não for reconhecido sai vazio com a pessoa nomeada no relatório de lacunas.

**Nada aqui importa `processo_seletivo`**: os valores vão **copiados**, como a `0002` copiou
`'ENVIADO'`. Migration que importa domínio faz uma alteração futura mudar retroativamente o efeito
de uma migration já executada, e `test_migrations_do_not_import_domain_or_application_code` recusa.
"""

from django.db import migrations, models

# Copiados de `requerimentos.domain.nomes` — ver a docstring.
RASCUNHO = "RASCUNHO"
BRASIL = "BRASIL"
GRAFIAS_HISTORICAS_DE_BRASIL = ("brasil", "brasileira", "brasileiro")


def _sem_acento(texto):
    """Comparação que não depende de acento nem de caixa, sem dependência nova.

    *"Brasil"* e *"BRASIL"* são a mesma declaração; comparar cru deixaria uma das duas de fora.
    """
    import unicodedata

    decomposto = unicodedata.normalize("NFKD", texto)
    return (
        "".join(letra for letra in decomposto if not unicodedata.combining(letra)).strip().lower()
    )


def reconhecer_brasil(apps, schema_editor):
    """Os **rascunhos** que dizem Brasil passam a dizê-lo no vocabulário da lista.

    Um a um, e não por `update()` em massa, porque o filtro é sobre a forma normalizada do texto —
    e normalizar no SQL exigiria extensão que este banco não tem.
    """
    Requerimento = apps.get_model("requerimentos", "RequerimentoDeMatricula")
    for requerimento in Requerimento.objects.filter(status=RASCUNHO).exclude(nacionalidade=""):
        if _sem_acento(requerimento.nacionalidade) in GRAFIAS_HISTORICAS_DE_BRASIL:
            requerimento.nacionalidade = BRASIL
            requerimento.save(update_fields=["nacionalidade"])


def devolver_o_texto_livre(apps, schema_editor):
    """A reversão devolve *"Brasil"* ao rascunho convertido.

    **Existe porque sem ela não há rollback de deploy**, e
    `test_every_migration_declares_a_reverse_path` recusa operação irreversível. Ela não tenta
    restaurar a grafia exata de cada pessoa — *"Brasileira"* volta como *"Brasil"* —, e isso é
    honesto: o que ela desfaz é o fechamento da lista, não a história do campo.
    """
    Requerimento = apps.get_model("requerimentos", "RequerimentoDeMatricula")
    Requerimento.objects.filter(status=RASCUNHO, nacionalidade=BRASIL).update(
        nacionalidade="Brasil"
    )


class Migration(migrations.Migration):
    dependencies = [("requerimentos", "0004_carga_por_geracao")]

    operations = [
        migrations.AddField(
            model_name="requerimentodematricula",
            name="titulo_eleitoral",
            field=models.CharField(blank=True, default="", max_length=12),
        ),
        migrations.AddField(
            model_name="requerimentodematricula",
            name="zona_eleitoral",
            field=models.CharField(blank=True, default="", max_length=3),
        ),
        migrations.AddField(
            model_name="requerimentodematricula",
            name="secao_eleitoral",
            field=models.CharField(blank=True, default="", max_length=4),
        ),
        migrations.AlterField(
            model_name="requerimentodematricula",
            name="nacionalidade",
            field=models.CharField(
                blank=True,
                choices=[("BRASIL", "BRASIL"), ("OUTRO_PAIS", "OUTRO_PAIS")],
                default="",
                max_length=60,
            ),
        ),
        migrations.RunPython(reconhecer_brasil, devolver_o_texto_livre),
    ]
