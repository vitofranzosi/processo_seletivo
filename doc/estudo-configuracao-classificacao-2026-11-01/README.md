# Investigação da configuração de classificação

## Rodada 2 — comece por aqui

A rodada 1 foi avaliada como insuficiente: não reproduziu o sintoma, os protótipos não configuravam
nada e o "mapa" era uma tabela. A rodada 2 refez o percurso **do zero, pela interface**, e mudou o
diagnóstico e a recomendação.

| Leia | O quê |
|---|---|
| [sintese.md](sintese.md) | Uma página: o problema medido, a aposta, os três passos, a confiança |
| [diario-de-construcao.md](diario-de-construcao.md) | O percurso passo a passo, com 10 achados e as referências de código ([registro bruto](diario-registro-bruto.txt), [capturas](capturas/diario/)) |
| [prototipos/v2/](prototipos/v2/index.html) | Trilho editável e texto do edital editável, sobre o mesmo modelo; cenários de estudo no rodapé |
| [decisoes-para-o-usuario.md](decisoes-para-o-usuario.md) | D-1 a D-7: o que muda o que o GPS grava ou publica, e por isso não se decide aqui |
| [verificacao-rodada2.json](verificacao-rodada2.json) | Sem erro de JavaScript; teclado; largura em 390 px; [16 capturas](capturas/rodada2/) por [script](scripts/capturar_rodada2.py) |

Servir a pasta: `python3 -m http.server 8769 --bind 127.0.0.1 --directory doc/estudo-configuracao-classificacao-2026-11-01`
e abrir <http://127.0.0.1:8769/prototipos/v2/index.html>. Os arquivos também abrem direto do disco.

O que segue é a rodada 1, mantida como registro. Dela continuam valendo a reconstrução do domínio
([diagnostico.md](diagnostico.md), [dependencias.md](dependencias.md)), o inventário de
validações ([validacoes.md](validacoes.md)) e a vista temporal do sorteio. **A recomendação dela
(mapa + painel de consequências) foi substituída.**

## Rodada 1

Estudo de 01/11/2026 sobre o commit `4d9e97a9597937f8812fed7c9a00f2197815e0d9`. Propostas para avaliação; sem implementação definitiva, spec nova ou alteração das regras do GPS.

**Abra a [apresentação visual](index.html)**. Ela leva a duas experiências navegáveis:

- [Mapa de relações](prototipos/mapa.html): selecione etapas e marcos, retire a marca classificatória, resolva pendências e examine consequências.
- [Caderno de compromissos](prototipos/caderno.html): construa decisões do edital, confronte o alcance entre perfis e confira compromissos antes de confirmar.

Os arquivos funcionam localmente, sem dependências externas. Alternativa por HTTP:

```bash
python3 -m http.server 8768 --bind 127.0.0.1 --directory doc/estudo-configuracao-classificacao-2026-11-01
```

Abra <http://127.0.0.1:8768/index.html>.

A hipótese inicial foi **parcialmente confirmada**: existem relações importantes separadas entre as telas, mas a prévia atual já simula durante a edição, aceita valores não salvos, mostra jornada e explica desempates. O estudo recomenda aproximar **etapa → marco → corte → etapa governada**, reaproveitando essa prévia; as condições temporais do sorteio merecem outra representação.

| Entrega | Artefato |
|---|---|
| 1. Diagnóstico técnico e cognitivo | [diagnostico.md](diagnostico.md), [jornadas.md](jornadas.md), [evidencias.md](evidencias.md) |
| 2. Mapa de dependências | [dependencias.md](dependencias.md) e mapa navegável |
| 3. Cinco alternativas | [alternativas.md](alternativas.md) |
| 4. Duas propostas materializadas | [mapa](prototipos/mapa.html), [caderno](prototipos/caderno.html), [capturas](capturas/prototipos/) |
| 5. Comparação e recomendação | [avaliacao.md](avaliacao.md) |
| 6. Evolução incremental | [evolucao.md](evolucao.md), [validações e interpretação](validacoes.md) |
| Método e execução técnica | [verificacao.md](verificacao.md), logs e scripts |

Na apresentação, siga o roteiro de comparação. Os seletores de estados no rodapé dos protótipos são controles da pesquisa, não uma proposta para o produto. Há exemplos normais, incompletos, inválidos, circulares e prontos **por hipótese**. Os navegadores não executam os serviços do GPS: apenas exibem transições e respostas preparadas.

Houve inspeção do código e dos testes, navegação real em Chromium e walkthrough cognitivo do pesquisador. **Não houve teste com operadores nem medição empírica de aprendizagem.** Os resultados de testes automatizados verificam o comportamento técnico, não a superioridade de UX.
