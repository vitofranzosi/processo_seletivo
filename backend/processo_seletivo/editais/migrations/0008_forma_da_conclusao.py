"""A Etapa passa a declarar a forma da conclusão, e os rótulos da forma decisória (012, D-008).

`forma` nasce **não anulável e com default**, e o `AddField` escreve o default nas linhas que já
existem. Não é conveniência: sem ele, toda Etapa hoje em elaboração sairia no snapshot com
`forma: null` e o Edital inteiro ficaria impublicável — o que seria consequência de produto, e não
detalhe de implantação (012, FR-119, FR-120).

Os dois rótulos nascem vazios, e vazio aqui significa "não se aplica": só a forma decisória os
publica, e um default institucional aplicaria ao Edital um rótulo que ele não escreveu (P-007).
"""

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("editais", "0007_etapa_declara_avaliacoes_e_maxima"),
    ]

    operations = [
        migrations.AddField(
            model_name="etapaavaliacao",
            name="forma",
            field=models.CharField(
                choices=[("PONTUADA", "Pontuada"), ("DECISORIA", "Decisoria")],
                default="PONTUADA",
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name="etapaavaliacao",
            name="rotulo_desfavoravel",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="etapaavaliacao",
            name="rotulo_favoravel",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
    ]
