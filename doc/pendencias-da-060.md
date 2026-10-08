# Pendências da 060 — o que ficou fora, e o que a implantação precisa

Registradas ao fechar a [`060`](../specs/060-unidades-e-autoridades/spec.md), em 06/10/2026.

> **Não viram escopo por estarem escritas aqui.** As da primeira parte são decisões de produto que a
> `060` deixou fora de propósito; as da segunda são passos de implantação, fora do código.
> Priorizar é do usuário.

## O que o produto ainda diz do Cefor

A `060` tirou o Cefor do **documento oficial** — cabeçalho, local, autoridade — e deixou de fora o
que o produto diz **de si**. Com uma unidade só, nada disso está errado; com a segunda, passa a
estar.

| Onde | O que diz | Por que ficou fora |
|---|---|---|
| `interface/templates/interface/base.html`, `portal/templates/portal/base.html`, `shared/templates/404.html` | *"Cefor/Ifes"* no título da página e no topo | É a marca do sistema, e trocá-la é decisão de produto: *"Ifes"*, *"Seleções Ifes"*, ou a unidade do operador |
| `identidade/application/mensagem.py`, `inscricoes/application/mensagem.py` | *"Seleções Cefor/Ifes"* no assunto e na assinatura dos e-mails | Idem, e o e-mail do candidato não tem unidade de operador — teria de vir do Edital |
| `interface/templates/interface/lista.html`, `recusa.html`, `minhas_etapas.html`, `interface/erros.py` | *"Peça acesso a quem administra o sistema no Cefor"* | A quem pedir depende de quem administra o sistema em cada unidade, e isso não existe ainda |
| `shared/api/operacional.py`, `shared/api/problems.py` | *"Processo Seletivo e Editais — Cefor/IFES"* e o tipo dos problemas `processo-seletivo.cefor/errors/…` | Contrato da API: mudar o tipo dos problemas muda o que os clientes leem |
| `portal/views.py` (`_selecao`) e `portal/templates/portal/_cartao_da_selecao.html` | a vitrine diz *"Unidade: CEFOR"* — o código do escopo em caixa alta | Com várias unidades, a vitrine deveria dizer a sigla da Publicação, e o filtro por unidade, a sigla e não o código. Ler a Publicação em cada cartão pede cuidado com o orçamento de consultas da vitrine |
| `interface/views.py` (`identificar`), `interface/identidade.py` (`ESCOPO_PADRAO`) | o seletor de identidade só oferece o escopo `cefor` | Limita a **demonstração** a uma unidade, e não o produto: produção não tem seletor, e a identidade institucional ainda não foi integrada. Os testes usam outros escopos sem passar por ele |

## O que a implantação precisa, fora do código

1. **Cadastrar as autoridades do Cefor** (FR-1124). O catálogo em código saiu, e com ele as três
   entradas — Reitora, Pró-Reitor de Ensino e Diretora-Geral do Cefor. Antes da primeira publicação
   real, o Gestor do Cefor as cadastra pela tela *Autoridades da unidade*, só com o cargo enquanto o
   Cefor não fornecer nome e portaria ([quickstart §7](../specs/060-unidades-e-autoridades/quickstart.md)).
   Sem nenhuma autoridade vigente, a publicação fica indisponível — e a tela diz por quê.
2. **Confirmar a base legal com o encarregado de dados do Ifes.** A `060` registra nome, cargo e
   ato de nomeação de quem responde pelo ato, e indica como base o cumprimento de obrigação legal
   (LGPD, art. 7º, II; Lei nº 9.784/1999, art. 22, § 1º) no tratamento pelo poder público
   (art. 23). A indicação é da spec; a confirmação é do encarregado
   ([spec, *Assumptions*](../specs/060-unidades-e-autoridades/spec.md#assumptions)).
3. **Registrar as demais unidades** quando o Ifes as fornecer: uma entrada em
   `backend/processo_seletivo/unidades/unidades.json` por unidade — sigla, nome, as linhas do
   cabeçalho e o local —, revisada em diff, aplicada por `make preparar` ou
   `manage.py sincronizar_unidades`.

## A pergunta que continua com o Cefor

Depois de gerado pelo sistema, **qual artefato é o documento oficial, e onde ele é formalizado e
assinado?** A `060` responde quem responde pelo ato, e não como o ato é assinado. A resposta não
muda o que a `060` construiu: o documento já diz *"Autoridade responsável pelo ato"*, que é verdade
em qualquer resposta.
