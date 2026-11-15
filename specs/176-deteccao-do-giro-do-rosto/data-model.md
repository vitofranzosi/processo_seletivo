# Data Model: A detecção do giro do rosto

**Nenhuma entidade, tabela, campo ou migration.** O que a detecção produz vive só na memória da página
e morre com ela (FR-8000). O `M` da preparação não muda.

## O que existe, e onde

| Coisa | Onde | Vida |
|---|---|---|
| A chave `VERIFICACAO_DETECCAO_DO_GIRO` | `settings` | configuração do ambiente |
| O manifesto do motor (versão, caminho, SHA-256) | `portal/deteccao.py`, constante | código |
| O giro de cada passo (`perfil-esquerdo` → `esquerda`, `perfil-direito` → `direita`) | `portal/deteccao.py`, constante; as chaves conferidas contra `roteiro.CHAVES` | código |
| As leituras `{ms, giro}` e o estado do oval | memória de `deteccao.js` | do palco aberto até sair dele; no máximo as últimas 20 leituras |
| A escolha "Prefiro avançar só tocando" | memória da página | até recarregar; não é guardada (D-003) |

## O que não muda

O corpo do início do envio — `tamanho`, `formato`, `duracao`, `marcas`, `roteiro`, `maioridade` — e as
marcas `{passo, instante}`, uma por passo, na ordem (a FR-7113 da `166`). Não há campo que diga se um
passo avançou pelo giro (FR-8031).
