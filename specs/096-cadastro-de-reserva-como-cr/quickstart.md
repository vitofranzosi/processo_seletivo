# Quickstart: validar o CR no documento e no portal

**Feature**: [spec.md](spec.md) · **Contrato**: [contracts/celula-de-vagas-e-nota.md](contracts/celula-de-vagas-e-nota.md)

## Pré-requisitos

- PostgreSQL local de pé (no macOS com Homebrew, `LC_ALL` exportado).
- Dependências de desenvolvimento: `cd backend && uv sync --extra dev`.
- Um `DB_NAME` próprio para esta worktree, por exemplo `ps_096`.

## 1. A suíte das áreas tocadas

```bash
cd backend && uv run pytest -q tests/unit/editais tests/unit/publicacoes tests/integration/portal/test_detalhe_selecao.py tests/contract/test_documento_publicado.py
```

O que se espera:

- os testes novos do predicado, da célula e da nota passam;
- os guardiões de bytes passam contra `specs/096-…/demonstracao/` no cenário B, e contra os PDFs da
  `069` no cenário A, que não muda (`SC-901`);
- `test_documento_da_auditoria_depois_da_096.py` passa, e é ele que prova que a única diferença no
  B é `0` → `CR` mais as notas (`SC-900`);
- a fixture de contrato continua byte a byte.

## 2. O cenário B pelo fluxo real

Num banco de validação novo, com os dados fictícios da auditoria:

```bash
cd backend && make preparar DB_NAME=ps_096_b
```

Depois, rode `doc/auditoria-edital-pdf-2026-10-08/cenarios/cenario_b_corrigido.py` como a `067`
rodou, contra esse banco, e publique. Extraia o texto do PDF publicado com `pdftotext -layout` e
confira:

- dezesseis linhas de tutor presencial com `CR` na coluna de vagas, e nenhuma com `0`;
- os dois Perfis de tutor a distância com o número;
- a linha de total com a soma dos dois;
- uma nota `CR: cadastro de reserva.` por tabela com `CR`, logo abaixo dela;
- a numeração das "Tabela N" igual à da `069`.

Para ver as páginas, renderize com CoreGraphics, e não com `pdftoppm`, que perde o negrito do
Edital.

## 3. O portal

Com o runserver da worktree e o banco do passo 2, abra `/selecoes/<id do Edital>/` e confira, num
Perfil de tutor presencial:

- `Cadastro reserva` em destaque, com `até 15 classificados, para convocação futura` (o 15 é o limite
  fictício do roteiro do cenário B, e não dado de Edital real);
- nenhum `0 vaga` e nenhum `CR` no bloco;
- num Perfil de tutor a distância, o número em destaque, como antes.

## 4. A gestão continua com o número

Na composição do mesmo Edital (etapa Perfis) e na Revisão, as vagas imediatas dos tutores presenciais
continuam `0`. A prévia do documento, aberta da Revisão, diz `CR`.

## 5. Fechamento

```bash
cd backend && make lint check test-pg DB_NAME=ps_096
```
