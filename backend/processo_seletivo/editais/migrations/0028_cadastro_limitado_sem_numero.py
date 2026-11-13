from django.db import migrations, models
from django.db.models import Q


class Migration(migrations.Migration):
    """O cadastro limitado deixa de exigir número digitado (162, FR-6931, T-003).

    O número do cadastro de reserva limitado passa a vir do corte do marco que convoca, e a gravação
    não aceita mais o digitado. A `0001` exigia `reserve_limit` não nulo em `LIMITED`; agora o
    limitado admite os dois: nulo, que é todo Perfil gravado depois da `162`, e o número que o
    rascunho salvo antes guarda — e que a Revisão mostra ao lado do derivado (FR-6940). As outras
    duas metades continuam: "não há" e "ilimitado" não admitem número.

    **Só afrouxa**, e por isso nenhuma linha existente viola a condição nova. Não toca tabela
    append-only: `PerfilVaga` é elaboração, e o `M` do provisionamento continua o mesmo.
    """

    dependencies = [
        ("editais", "0027_criterios_de_avaliacao"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="perfilvaga",
            name="ck_perfil_reserve_limit_compatible",
        ),
        migrations.AddConstraint(
            model_name="perfilvaga",
            constraint=models.CheckConstraint(
                condition=(
                    Q(reserve_type="NONE", reserve_limit__isnull=True)
                    | Q(reserve_type="LIMITED")
                    | Q(reserve_type="UNLIMITED", reserve_limit__isnull=True)
                ),
                name="ck_perfil_reserve_limit_compatible",
            ),
        ),
    ]
