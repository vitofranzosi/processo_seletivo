# Quickstart — verificar a 054

## 1. A suíte

```bash
cd backend && make lint check test-pg DB_NAME=ps_054
```

## 2. O documento do 28/2026, seção a seção

Num banco próprio (`ps_054_demo`), migrado e com os papéis provisionados:

1. Compor um Edital com a estrutura do 28/2026: 7 Perfis (um por polo, 40 vagas cada, com as reservas
   PPI e PcD no quadro), classificação por sorteio, Requerimento de Matrícula na convocação, e as
   seções textuais que o original tem, com o texto transcrito do original — **sem nenhum nome de
   pessoa**. As que o original não tem ficam vazias.
2. Submeter, homologar e publicar pela camada de aplicação, com a autoridade do catálogo.
3. Retificar o texto de uma seção e publicar a Retificação.
4. Extrair os dois documentos (`DocumentoPublicado.bytes`) e lê-los com `pdftotext -layout`, ao lado
   do original (`pdftotext -layout` do PDF em `~/Downloads`).

**Esperado**: as 15 seções numeradas do original com seção correspondente (`SC-361`), na ordem de
[research](research.md) R-001; a tabela de Perfis terminando em `Total … 280` (`SC-369`); a
declaração do Requerimento na Matrícula (`SC-368`); o fecho `Vitória (ES), <data>.` e o cargo, sem
nome (`SC-364`, `SC-365`); no documento da Retificação, a marca *"Versão consolidada…"* e, no
original, nenhuma (`SC-367`).

## 3. O catálogo anterior continua retificável

Numa cópia do banco com um Edital publicado **antes** da 054 (12 seções): aplicar as migrations,
retificar o texto de uma seção e publicar. **Esperado**: a publicação é aceita, e o consolidado tem as
12 seções da publicação original (`SC-366`). É o que o teste de integração da US4 reproduz.

## 4. A etapa Conteúdo

No preview, abrir a etapa Conteúdo de um Edital em elaboração: as seções vazias dizem *"Vazia — não
sai no documento"*, as demais o número; digitar numa vazia faz ela e as seguintes renumerarem sem
gravar (`UX-130`); a Revisão mostra os mesmos números (`SC-363`).

## 5. Antes do deploy

Os Editais homologados e não publicados precisarão ser submetidos de novo:

```bash
cd backend && uv run python manage.py shell -c "from processo_seletivo.editais.models import Edital; print(list(Edital.objects.filter(status='HOMOLOGADO').values_list('number', 'year')))"
```
