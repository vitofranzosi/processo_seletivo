# Achado — a regra de substituição publicada nunca avança contra a Caixa real

**Encontrado em**: 03/11/2026, na investigação da extração da Loteria Federal
([estudo](estudo-extracao-da-loteria-federal-2026-11-03.md), seção 8). A análise é da `main` em
`83cd5863`.

> **Não é escopo da `116`, e não vira escopo por estar escrito aqui.** O que se registra é o defeito,
> a evidência, o que ele custa e o que uma spec corretiva teria de decidir. Priorizar é do usuário.

## O que acontece

Todo Edital com sorteio publica uma regra de substituição: *"se a ocorrência declarada faltar, vale a
seguinte da mesma fonte"* (`OCORRENCIA_SEGUINTE_DA_MESMA_FONTE`, a FR-015 da `021`). Ela só avança
quando a ocorrência é registrada como **indisponível**. Contra a Caixa real, ela nunca é.

1. A Caixa responde **HTTP 500** a todo concurso que ainda não foi realizado. Medido em 03/11/2026:
   6115, 6118, 6200, 9999, 99999, 0 e −1. O corpo é `"Ocorreu um erro inesperado."`, com um 404 (ou
   412) interno embrulhado em `exceptionMessage`.
2. O adaptador usa `urllib.request.urlopen`, que levanta `HTTPError` para o 500. `HTTPError` é
   subclasse de `URLError`, e `loteria_federal.py:52` captura `URLError` como **falha de acesso**.
3. Falha de acesso não grava nada (`ocorrencia.py:71`). É o lado seguro, e foi decidido assim de
   propósito: um soluço de rede não pode queimar a extração declarada.
4. O desfecho `indisponivel` só nasce de uma resposta 200 **sem os bilhetes**. A Caixa não devolve
   isso para concurso que não houve. Ela devolve 500.

**Consequência:** para um concurso que não acontece, cancelado ou com número errado, a observação
responde "não foi possível falar com a Caixa" para sempre. A cadeia de substituição nunca recebe a
indisponibilidade que a faz avançar. A guarda `occurrence_not_due_yet` (`ocorrencia.py:94`) também
nunca dispara com a fonte real.

## Evidência reproduzível

Sem rede, com a resposta gravada do 6115
(`doc/estudo-extracao-da-loteria-federal-2026-11-03/respostas/federal_6115.json`). O script está no
estudo, seção 1.3, item 4:

```
4. concurso ainda não realizado (HTTP 500): indisponivel= False falha_de_acesso= True
```

O teste que prende a distinção, `tests/integration/sorteios/test_falha_de_acesso_a_fonte.py:118`,
exercita a indisponibilidade com `{"dataApuracao": "06/09/2026", "listaDezenas": []}` e status 200.
É uma forma de resposta que a Caixa não produziu em nenhuma das 24 chamadas de 03/11.

**Cenário:**

1. Edital publicado com o concurso 6150, que na verdade será realizado meses depois.
2. Relação congelada.
3. No dia declarado, "Observar a ocorrência" recusa com `source_unreachable`: *"Não foi possível
   falar com Loteria Federal agora"*.
4. A recusa se repete em todas as tentativas, e a regra publicada não indica a seguinte, porque nada
   foi registrado.
5. A única saída é Retificação mais relação nova. A regra publicada existia para tornar isso
   desnecessário.

## Por que importa

- **Risco administrativo.** O Edital publica uma garantia — *"sem escolha humana no dia"* — que o
  sistema não consegue cumprir com a fonte que ele mesmo usa. No dia do problema, a escolha volta
  para a mesa, que é o que a FR-015 da `021` proíbe.
- **Diagnóstico errado.** A mensagem manda tentar de novo, por rede, quando a causa é a ausência da
  extração. Quem opera ao vivo investiga o lado errado.
- **Atenuante.** A `116` reduz a chance do número errado chegar ao sorteio, porque confere o número na
  publicação e no congelamento. Ela não cobre o concurso que a Caixa cancela ou adia depois do
  congelamento.

## O que uma spec corretiva teria de decidir

Nenhuma destas se decide lendo código. Todas têm efeito append-only, porque a indisponibilidade
consome a cadeia para sempre.

1. **Que evidência basta para "a fonte não publicou".** O 500 sozinho não basta: é a mesma resposta
   de um erro do serviço. Candidatos:
   - o 500 **depois** do instante declarado, combinado com o endpoint principal informando um último
     concurso **maior** que a referência. Isso significaria que a Caixa passou adiante sem ela;
   - ou um prazo de carência publicado no próprio método.
2. **Quem confirma.** Automático, como a FR-015 pede, ou um ato da presidência com motivo, como
   exceção registrada.
3. **A mensagem.** Separar "a Caixa não respondeu" de "a Caixa respondeu que o concurso não existe
   (ainda)", mesmo antes de decidir o item 1.
4. **O teste de contrato.** Trocar a forma inventada (200 sem bilhetes) pela forma real (500 com 404
   interno), e decidir o que ela significa.

**Recomendação:** spec própria, depois da `116`, antes de depender operacionalmente da
substituição automática. Não atribuir significado normativo ao HTTP 500 sem a evidência do item 1.
