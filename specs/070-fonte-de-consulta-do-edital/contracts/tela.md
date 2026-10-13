# Contrato — a tela de validação interna

Uma tela nova na gestão, e um link de entrada numa tela existente. Nada no portal.

## Rota

| Método | Caminho | Nome | View |
|---|---|---|---|
| `GET` | `gestao/editais/<uuid:edital_id>/duvidas/` | `interface:duvidas` | `interface/duvidas.py`, `respostas_do_assistente` |

Os parâmetros vão na query; todos são opcionais.

| Parâmetro | Forma | Efeito |
|---|---|---|
| `pergunta` | `P-01` … `P-12` | Sem ele, só o catálogo e os pontos para revisão |
| `perfil` | código do Perfil | Para as perguntas com Perfil |
| `modalidade` | código da modalidade, ou `nenhuma` | Só na `P-05` |
| `em` | `AAAA-MM-DDTHH:MM`, na zona institucional | Instante de referência (`R-020`) |
| `versao` | UUID da versão da resposta anterior | Aviso de mudança (`FR-1415`) |

## Portas e negativas

| Situação | Resposta | Inventário da `033` |
|---|---|---|
| Sem identidade na sessão | redireciona para identificar, como a página do Edital | — |
| Edital fora do escopo do ator, ou inexistente | `404`, pelo `not_found` do domínio, como nas telas dos avisos | nenhuma: não há `Http404` (implementação de 12/10) |
| Edital sem publicação, ou instante anterior à primeira vigência | `200`, com "Só Edital publicado tem respostas" ou "Não havia versão vigente em {instante}" | — |
| Pergunta fora do catálogo, ou não aplicável ao Edital | `200`, com o catálogo e a mensagem "Esta pergunta não se aplica a este Edital" | — |
| Perfil ou modalidade inexistentes na versão vigente | `200`, com a pergunta reapresentada e o motivo | — |
| `em` inválido | `200`, consultado no presente, com a mensagem de instante não entendido | — |

Nenhum `403` novo: não há capacidade nova (`D-010`).

## Ordem da tela

1. **Título:** "Respostas do assistente de dúvidas — validação interna". Logo abaixo: "Nada desta
   tela é exibido a candidatos." (`UX-205`)
2. **Identificação do Edital**: número/ano e título. Depois, o instante de referência, com o campo
   para mudá-lo.
3. **Pontos para revisão antes da abertura pública** (`UX-203`): lista, ou "Nenhum ponto para
   revisão."
4. **Perguntas:** formulário `GET`, com um rádio por pergunta aplicável, os seletores de Perfil e de
   modalidade (nativos) e o botão "Ver a resposta".
5. **Resposta**, numa região com `aria-live="polite"` e foco movido para o título dela (`UX-204`):
   1. o aviso de mudança de versão, se houver (`UX-201`);
   2. a versão: "Versão vigente desde {data e hora} · publicada em {data e hora} · retificada em
      {datas e horas} · identificador {12 hex}". Com a hora, porque atos do mesmo dia ficavam
      indistinguíveis ("retificada em 12/10/2026 e em 12/10/2026");
   3. o tipo, em palavras (`UX-202`);
   4. os avisos;
   5. a explicação, rotulada "Explicação — produzida pelo sistema a partir das fontes abaixo; não é
      texto do Edital" (`FR-1436`);
   6. as fontes, uma `<section class="referencia">` por cartão:
      - o rótulo da natureza, em palavras (`UX-200`);
      - a localização;
      - o conteúdo — textos longos dentro de `<details>` aberto por padrão até um limite de linhas e
        recolhível, **sem truncar** (`UX-204`);
      - a origem: "Publicação original de {data}" ou "Retificação publicada em {data}, vigente desde
        {data}", com o link "Abrir o documento deste ato";
      - os links para a página pública, quando houver.

## Vocabulário

| Use | Não use | Por quê |
|---|---|---|
| "assistente de dúvidas" | "assistente" sozinho | `R-002` |
| "Texto do Edital", "Dado da versão vigente", "Explicação" | "citação", "trecho do PDF" | `FR-1434` |
| "documento deste ato" | "Edital completo", "documento vigente" | `D-004` |
| "O Edital não informa" | "não cabe", "não há", "não é permitido" | `FR-1422` |
| o título da seção | "item 11", "seção 10" | `FR-1431` |

## Entrada

Na página do Edital (`interface/templates/interface/detalhe.html`), no bloco dos documentos
publicados, um link: "Ver as respostas do assistente de dúvidas (validação interna)". Ele aparece só
quando o Edital tem ao menos uma publicação.

## Acessibilidade e largura

- Controles nativos, com `label` ligado. Os grupos de rádio ficam em `fieldset` com `legend`.
- O `fieldset` das perguntas tem `flex-wrap`. Sem ele, o grupo cresce até o conteúdo mínimo e alarga
  a página a 375 px (achado da `057`).
- Toda classe nova tem regra em `interface/templates/interface/base.html`
  (`test_acessibilidade.py`).
- Nenhuma regra CSS com `}}` na mesma linha (`test_estaticos.py`).
