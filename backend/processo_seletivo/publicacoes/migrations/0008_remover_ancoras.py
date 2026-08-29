"""Remove a âncora de identidade da `003`.

`expected_anchors` respondia "o item neste índice ainda é a mesma entidade?". Com o
endereçamento por chave, o próprio `target_path` nomeia a entidade e não sobra índice para
deslocar: a coluna perdeu a pergunta que respondia (FR-015).

É migração de esquema e nada mais. O sistema não está em produção e não há ato a preservar, de
modo que não há caminho a converter nem condição a comprovar antes de remover (FR-016).

`RemoveField` é reversível por si: o Django recria a coluna a partir do estado que a `0005`
guarda, vazia. É o máximo que uma reversão honesta oferece — as âncoras não existem em lugar
nenhum depois daqui.
"""

from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [("publicacoes", "0007_imutabilidade_do_historico")]

    operations = [
        migrations.RemoveField(model_name="alteracaonormativa", name="expected_anchors"),
    ]
