# Verificação: O Cronograma — visibilidade no PDF, ordenação e prévia (144)

## Incremento A — visibilidade no PDF (10/11/2026)

Branch `claude/144-a-visibilidade-no-pdf`, sobre a `main` em `b202a7c0` (com a spec, #454).

### Suíte contra PostgreSQL

Uma rodada completa, 4 workers, `worksteal`, **sem** os grupos `navegador` e `assistente`:
**17 923 passando, 22 pulados e 3 falhas**, em 868s.

- Os 22 pulados são os previstos sem os dois grupos: 9 arquivos de jornada no navegador, 10 pares do
  vocabulário, a contagem do tokenizer, o E2E da Caixa e a recusa por vendor.
- As 3 falhas tinham uma causa só: três testes acrescentam Evento por Retificação pela API com o
  objeto escrito à mão, e a forma publicada passou a exigir `shownInPdf`, como já exigia `location`
  e `isRegistrationPeriod` — "o Evento acrescentado por Retificação é declarado inteiro". Os três
  literais ganharam a chave (`agenda/test_fonte.py`, `editais/test_reaproveitamento.py`,
  `publicacoes/test_retificacoes.py`). Nenhuma recusa foi afrouxada.
- Depois da correção, **não** se repetiu a suíte inteira: rodaram os quatro arquivos que acrescentam
  Evento por Retificação (112 passando) e os arquivos novos com os guardiões de estáticos,
  acessibilidade, JavaScript, citações e README (1 189 passando). O CI roda a suíte completa.
- `ruff check`, `ruff format --check`, `manage.py check` e `makemigrations --check`: verdes.

### No navegador (preview `cronograma-144`, banco `ps_demo_144`, Edital 76/2027)

- Os três olhos saem do servidor com `hidden` e o `cronograma.js` os revela.
- O clique no olho da "Prova objetiva" muda o campo para `false`, `aria-pressed` para `true`, o
  `title` para "Oculto do PDF — exibir", mostra a marca e atenua o cartão; o `change` chega ao
  formulário, e o rascunho local o registra (`Prova objetiva: false`). O foco fica no botão.
- "Acrescentar Evento" traz a linha nova exibida, com o olho revelado pela mutação da lista.
- Gravado e recarregado: a "Prova objetiva" volta oculta. A prévia do PDF não traz a descrição dela.
- Nenhuma violação de CSP no console.

### O que não foi verificado

- Os casos de navegador (foco depois de ordenar, jornada inteira) são do incremento C (T026, T029),
  e pedem o grupo `navegador`.
- A 375 px o cartão não foi medido: o incremento A só acrescenta um botão ao grupo de ações, que já
  quebrava linha; a medição entra com a prévia (UX-393).

### Revisão de código (10/11/2026)

Sete achados; seis corrigidos antes do PR — a frase da Revisão que dizia "Nada cadastrado em
Cronograma" com todos os Eventos ocultos, `numero_no_documento` comparando `None == None`, três
rótulos para o mesmo campo (agora "Sai na tabela do Cronograma do PDF" na tela da Retificação e na
página pública), o bloco do Cronograma montado direto, o estado passado ao include das ações da linha
por parâmetro, e o teste do Evento acrescentado por Retificação. Depois deles, os testes de
`interface`, `unit/publicacoes`, `integration/publicacoes`, `integration/editais`, `contract`, os de
JavaScript, citações e README: 7 195 passando, 1 pulado.

**Registrado, não corrigido:** na etapa Conteúdo, a seção Cronograma com todos os Eventos ocultos
aparece como "(vazia — não sai no documento)". O rótulo é reescrito pelo `conteudo.js` a partir do
estado `nao-sai`, e distinguir "vazia" de "toda oculta" pede um estado novo no script — fora do
incremento A. A Revisão, que é onde quem homologa decide, já diz a causa certa.
