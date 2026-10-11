"""Extrai, de um banco com os editais publicados, os PDFs e o conteúdo canônico de cada Publicação.

**Não foi reexecutado na rodada 2**, que não publica nada. Na rodada 1, o banco `ps_libras_corpus` foi
criado do zero (`createdb` + `migrate` com o superusuário + `sincronizar_unidades`) e povoado com:

- `doc/auditoria-edital-pdf-2026-10-08/cenarios/cenario_a2.py` (91/2026 e a sua Retificação);
- `doc/auditoria-edital-pdf-2026-10-08/cenarios/cenario_b_corrigido.py` (92/2026 e a sua Retificação);
- `manage.py seed_demo` (01/2026 e as suas duas Retificações, entre outros).

Os roteiros da auditoria têm caminhos absolutos de outra sessão: copiá-los, trocar o caminho do
scratchpad em `sys.path`, `exec` e `ORIGEM`, e o `SAIDA` fixo de `comum.py`.

**Não se reproduz byte a byte**: o conteúdo inclui identificadores aleatórios de Processo e de Edital, e o
`seed_demo` usa datas relativas ao instante da execução. A fonte de verdade são os arquivos em
`editais/<edital>/fonte/`, cujos hashes estão nos manifestos.

Uso:  cd backend && DB_NAME=<banco> ... uv run python manage.py shell < ../docs/libras/ferramentas/exportar_corpus.py
Grava em `docs/libras/ferramentas/saida/` (fora de controle de versão por convenção desta pasta).
"""

import json
from pathlib import Path

from django.conf import settings
from processo_seletivo.publicacoes.models import DocumentoPublicado, Publicacao
from processo_seletivo.publicacoes.models_retificacao import Retificacao

SAIDA = Path(settings.BASE_DIR).parent / "docs" / "libras" / "ferramentas" / "saida"
SAIDA.mkdir(parents=True, exist_ok=True)

for p in Publicacao.objects.select_related("edital").order_by("edital__number", "publication_order"):
    e = p.edital
    rotulo = f"E{e.number}-{e.year}-pub{p.publication_order}"
    (SAIDA / f"{rotulo}-canonico.json").write_bytes(bytes(p.canonical_content))
    documento = DocumentoPublicado.objects.filter(publicacao=p).first()
    if documento:
        (SAIDA / f"{rotulo}.pdf").write_bytes(bytes(documento.bytes))
    retificacao = Retificacao.objects.filter(publication=p).first()
    if retificacao:
        alteracoes = [dict(path=a.target_path, op=a.operation, novo=a.new_value) for a in retificacao.alteracoes.all()]
        (SAIDA / f"{rotulo}-alteracoes.json").write_text(
            json.dumps(
                dict(
                    justificativa=retificacao.justification,
                    vigencia=str(retificacao.effective_at),
                    alteracoes=alteracoes,
                ),
                ensure_ascii=False,
                indent=1,
                default=str,
            ),
            encoding="utf-8",
        )
    print(rotulo, p.content_hash[:16], "retificação" if retificacao else "original")
