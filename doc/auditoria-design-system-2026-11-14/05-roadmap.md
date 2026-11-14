# F. Plano de convergência

*Proposta de sequência. Nada aqui foi iniciado: cada frente vira spec própria depois da decisão sobre
a direção visual.*

Esforço relativo: **P** cabe numa sessão, **M** numa spec de alguns dias, **G** pede mais de uma
spec. O alcance é em rotas que rendem tela (135 no total).

## O menor conjunto com o maior avanço

Seis mudanças explicam a maior parte da fragmentação medida, e nenhuma delas é de uma tela só:

| # | Mudança | Resolve | Alcance |
|---|---|---|---|
| 1 | Tokens de escala (fonte, espaço, raio, controle) e os neutros num lugar só | S3, S7, S11 | todas |
| 2 | Parcial de cabeçalho de página | S1 | 89 telas da gestão |
| 3 | Três composições de página: cheia, com trilho, centrada | S2 | todas |
| 4 | `.acao` com altura única, e uma barra de ações | S5 | cerca de 40 telas |
| 5 | Indicador e aviso como componentes | S4, S6 | cerca de 45 telas |
| 6 | Guardiões com lista fechada | impede a volta | todas as futuras |

## P0. Correções críticas

Independem da direção visual. Podem entrar antes de qualquer decisão.

| Item | O que é | Evidência | Esf. | Risco |
|---|---|---|---|---|
| P0.1 | Visão Geral: contraste abaixo de 4,5:1 em 155 trechos | S7, E1 | P | baixo: trocar a paleta local pelos tokens |
| P0.2 | Visão Geral: transbordo a 768 px | S8, E1 | P | baixo: usar a moldura comum de tabela |
| P0.3 | Confirmação de ato irreversível com linha de 176 caracteres em monitor largo | S2, E8 | P | baixo: medida de leitura nos blocos de consequência |
| P0.4 | Aviso que só se distingue pela cor | S6 | P | baixo: marca de espécie no texto ("Atenção", "Impede") onde ainda não há |

**Critério de aceite:** `telas.csv` regenerado mostra zero trecho abaixo do contraste na Visão Geral,
zero transbordo a 768 px e nenhuma linha acima de 100 caracteres nas confirmações; a suíte fecha
verde.

## P1. Padrões estruturais

A fundação. Nenhum item muda sozinho a aparência de uma tela que não o adote.

| Item | O que é | Depende de | Esf. | Risco |
|---|---|---|---|---|
| P1.1 | Tokens: os 14 de `acesso.css` sobem para `tokens.css`; entram as escalas `--t-*`, `--e-*`, `--raio*`, `--controle*` e o `--azul` | decisão 1 | P | baixo: só acrescenta |
| P1.2 | Parcial `_cabecalho_da_pagina.html` e a regra `.cabecalho-da-pagina` | P1.1 | M | baixo |
| P1.3 | Composições `.com-trilho` e `.centrada` em `moldura.css`; `--formulario`, `--trilho`, `--coluna` | P1.1 | M | médio: `test_larguras.py` aprende as medidas novas |
| P1.4 | `.acao` com 32 px e `line-height` fixo; `.botao.discreto`; `.barra-de-acoes` | P1.1 | P | médio: muda 1 a 5 px em cerca de 40 telas; conferir por captura |
| P1.5 | `.indicador` e `.indicadores`; `.aviso` com quatro tons e ícone | P1.1 | M | baixo |
| P1.6 | Cinco guardiões, cada um com a lista do que existe hoje | P1.1 | M | baixo: nascem verdes |
| P1.7 | Instrumento de medida como alvo do `Makefile` | nenhuma | P | nenhum |

**Decisão embutida em P1.1.** Subir os neutros da entrada para oficiais pode ser feito de dois
jeitos: *acrescentar* os tokens e deixar `--texto`, `--borda` e `--fundo` como estão (nenhuma tela
muda), ou *apontar* os antigos para os novos (todas as telas mudam um pouco, de uma vez). A
recomendação é acrescentar no piloto e apontar no começo da P2, com captura de todas as telas antes
e depois.

## P2. Convergência das telas

Por arquétipo, e não por tela: cada família é uma spec, e termina tirando itens das listas dos
guardiões. A ordem vai do maior alcance com menor risco para o contrário.

| Ordem | Família | Rotas | O que muda | Esf. | Risco |
|---|---|---:|---|---|---|
| P2.1 | Confirmação de ato | 35 | página centrada, um aviso por tom, barra de ações | M | baixo: poucos templates servem muitas rotas |
| P2.2 | Lista administrativa, registro e histórico | 22 | cabeçalho, barra de filtros, tabela em cartão, moldura única | M | baixo |
| P2.3 | Jornada do candidato e portal público | 20 | página centrada, alturas de controle, envio de arquivo | M | médio: scripts do portal e impressão do comprovante |
| P2.4 | Formulário de configuração | 14 | passos, grade de campos, trilho de apoio, barra de ações fixa | G | médio: os guardiões do assistente leem os templates |
| P2.5 | Central de trabalho e página de entidade | 15 | cabeçalho, indicadores, trilho; Lista de Processos em tabela | M | médio: orçamento de consulta da lista |
| P2.6 | Operação com etapas, avaliação e conferência | 17 | indicadores, gesto em destaque, contexto no trilho | G | alto: texto e ordem fixados em spec; uma spec por tela |

O Centro de Controle e a Página do Processo entram na P2.5 só com a troca de tokens: são as
referências, e a composição delas fica.

As 12 rotas restantes: o acesso (8) é referência e só recebe os tokens; os dois relatórios seguem
a P2.2; o guia incorporado está na P3.5.

## P3. Refinamento

| Item | O que é | Esf. |
|---|---|---|
| P3.1 | Um conjunto de ícones; saída gradual dos glifos de texto | M |
| P3.2 | Fonte embarcada, se a decisão 3 for por ela | P |
| P3.3 | Estados vazios com a ação seguinte | P |
| P3.4 | Transição de cor e de borda nos controles | P |
| P3.5 | Guia incorporado (Documentação do Sistema) com os tokens | M |
| P3.6 | Folha de impressão revista contra a nova escala | P |

## O piloto

**Recomendação: P0, P1.1 a P1.5, e três telas.** O piloto prova que os padrões se propagam, e não
que uma tela ficou bonita.

| Tela do piloto | Por quê |
|---|---|
| **Confirmação de ato do Edital** (`confirmar.html`) | um template serve submeter, homologar, devolver, publicar, encerrar e cancelar: uma mudança, seis rotas. Prova a página centrada, o aviso e a barra de ações |
| **Ocupação de vagas** | operação simples, com indicadores e prosa: prova o trilho e o indicador sem tocar em ato |
| **Lista de Processos Seletivos**, sem a coluna nova | é a porta de entrada: prova o cabeçalho de página, a tabela em cartão e o trilho, e todo perfil vê |

Ficam de fora do piloto, de propósito: a Convocação (risco de domínio), o assistente (muitos
guardiões) e o portal (scripts próprios). Entram na P2, cada um com a sua spec.

### Critérios de aceite do piloto

Medidos pelo instrumento, antes e depois, no mesmo banco de cenários:

1. **Nada fora do piloto muda.** No `telas.csv`, só as linhas das telas do piloto têm diferença. As
   capturas das demais são conferidas por amostra de 20.
2. **Nas telas do piloto:** nenhuma cor literal, nenhum `font-size` fora da escala, um botão cheio
   por tela, nenhuma linha acima de 80 caracteres, nenhum transbordo de 375 a 1920 px, zero trecho
   abaixo do contraste.
3. **Largura:** metade direita ocupada acima de 45% a 1440 px na Lista e na Ocupação; margens iguais
   na confirmação, em qualquer largura.
4. **Função intacta:** a lista de destinos de link e de formulário de cada tela, por papel, é
   idêntica antes e depois (lida pelo cliente de teste, como na `057`). Nenhum texto de ato muda.
5. **Guardiões:** as listas de exceção dos cinco novos não crescem, e a suíte contra PostgreSQL e o
   `lint` fecham verdes.
6. **Leitura humana:** duas pessoas da equipe de seleção abrem as três telas, antigas e novas, e
   dizem onde está a ação principal em cada uma. É conferência, e não teste formal.

## Riscos que valem para todas as frentes

| Risco | De onde vem | Como tratar |
|---|---|---|
| Guardião que lê a folha como texto | 34 arquivos de teste leem CSS; renomear classe ou mover regra reprova | manter os nomes; mudar valor, e não seletor; rodar o diretório `tests/interface` a cada passo |
| Classe citada sem regra | `test_nenhuma_classe_citada_deixa_de_existir_na_folha` | toda classe nova nasce com regra, no mesmo commit |
| Texto fixado em spec | cada frase de tela de operação tem FR | o design move e recolhe; não reescreve. Corte de texto é spec |
| Script que depende de classe | `rascunho.js`, `remocao.js`, `visualizador.js`, `envio.js` selecionam por classe | conferir os seletores antes de mexer no template; os testes de `tests/javascript` cobrem |
| Teto de caracteres da Distribuição | a página tem limite provado por teste | parcial novo não pode engordar o HTML repetido por linha |
| Orçamento de consulta | a lista e o Centro têm teto de consultas | componente novo não lê banco |
| Política de conteúdo | sem `style=` e sem `<style>` | largura e altura dinâmicas continuam por classe (`altura-N`) |
| Impressão | o comprovante e o resultado têm folha de impressão | conferir a impressão em toda família do portal |
| Várias sessões na mesma folha | frentes paralelas tocando `componentes.css` | uma família por vez, em série |

## Decisões que ficam com o usuário

1. **Direção visual.** A dos protótipos vale? Em resumo: os neutros da tela de entrada, raio de 10 e
   6 px, sombra discreta no cartão, texto de interface em 14 px, contexto no trilho.
2. **Piloto.** As três telas propostas, ou outras?
3. **Fonte.** A pilha do sistema, declarada como a fonte do produto, ou Open Sans embarcada?
4. **Neutros.** Acrescentar agora e apontar os antigos na P2, ou trocar de uma vez?
5. **Tabela em 14 px.** Hoje a célula tem 15 px. A proposta ganha densidade e perde 1 px de corpo; a
   alternativa é manter 15 px e aceitar um sétimo tamanho.
6. **"Fase e próximo passo" na Lista de Processos.** É informação nova na listagem.
7. **Texto explicativo.** Aceita-se mover os parágrafos permanentes das telas de operação para o
   trilho ou para um recolhido? Cada caso depois vira item de spec.

## Como medir o avanço

O critério do pedido, navegar por dez telas e sentir o mesmo produto, vira número com o que já está
medido:

| Indicador | Hoje | Alvo ao fim da P2 |
|---|---:|---:|
| Aberturas de página distintas (gestão) | 71 em 89 | uma por arquétipo, cerca de 11 |
| Tamanhos de fonte com mais de 1% do texto | 11 | 6 |
| Regras de caixa nas folhas | 63 | menos de 10 |
| Regras de faixa de aviso | 28 | 4 tons, 2 tamanhos |
| Alturas do `.acao` | 4 | 1 |
| Cores literais fora dos tokens | 41 | 0 |
| Condições de `@media` | 19 | 4 |
| Metade direita ocupada, mediana a 1440 px | 27% | acima de 45% nas telas com trilho |
| Telas que reprovam em contraste | 1 | 0 |
| Classes de uma tela só | 576 de 1.214 | em queda a cada família |
