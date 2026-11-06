# Alternativas, proposta e escopo de spec

Parte do [estudo de orientação da jornada](README.md). Os achados `J-` e `P-` estão na
[matriz de lacunas](matriz-de-lacunas.md); as situações e a derivação de cada uma, no
[contrato de derivação](contrato-de-derivacao.md); a validação, no [roteiro](validacao.md).

**Versão 2, de 06/11/2026, depois da revisão do mesmo dia.** A revisão aprovou o diagnóstico e a direção
funcional, e pediu cinco ajustes. Esta versão os incorpora:

| Pedido da revisão | O que mudou aqui |
|---|---|
| A matriz Perfil × ato pode reproduzir a carga que quer resolver | Dois níveis: as providências dentro de "O que fazer agora", e a matriz recolhida por Perfil, no lugar do cartão "Classificação" (§3) |
| "O que fazer agora" não pode ser sequência rígida | Não há próximo passo único: a derivação devolve um conjunto de providências, e a apresentação as ordena por regra fixa (contrato §1 e §4) |
| Ausência de ato não é pendência | Sete situações, com a derivação de cada uma a partir do que já existe (contrato §2 e §5) |
| A orientação depende do papel | Maquetes do mesmo Edital para quem conduz, quem publica e quem elabora, e do 91 para a presidência; o contrato da `104` é reaproveitado (contrato §3) |
| Não acrescentar 400 px | A v2 tira a trilha depois da publicação e o cartão "Classificação". Para quem conduz o 35, a página cai de 1767 para 1732 px (§3.3) |
| Priorizar; o P0 não depende da visão de jornada | P0 a P3, e o P0 numa spec própria e pequena (§2, §5) |
| D1 a D6 com alternativas e recomendação | §4, mais D7 e D8, que o contrato fez aparecer |

A v1 continua em `maquetes/v1/` e no histórico do repositório.

> **Versão 3 (segunda revisão de 06/11): generalidade.** A revisão condicionou a Spec B à prova de que
> a proposta serve a toda forma de classificação. O [complemento](generalidade-da-jornada.md) mostrou
> que o nível 1 e as sete situações são genéricos, e o nível 2 da v2 não era: as colunas eram as do
> sorteio, e as Etapas de avaliação nem apareciam. O que muda aqui, marcado **[v3]** onde está:
>
> - o nível 2 se compõe pela `jornada()` da `094`;
> - a D5 e a D6 foram revistas;
> - a Spec A ganha a G-01;
> - os critérios da Spec B cobrem uma família por linha da matriz de compatibilidade.

---

## 1. As cinco alternativas

| | O que é | Resolve | Não resolve |
|---|---|---|---|
| **A: preservar, com correções de texto** | Corrigir as mensagens que desorientam ou induzem a erro | J-06, J-07, J-10, J-12 e a parte de risco de J-08 | J-01, J-03, J-04: o quadro continua espalhado |
| **B: orientação contextual nas telas de operação** | "Próximo nesta lista" nas mensagens de sucesso; motivo da espera na célula | J-08 | J-01, J-03 |
| **C: orientação no detalhe do Edital** | As providências, por papel, em "O que fazer agora"; o andamento por Perfil, recolhido | J-01, J-03, J-04, J-07, J-09, J-16 | J-05 |
| **D: C + detalhamento por lista** | C, e a condução do marco com relação, semente e convocação | Tudo de C, e J-05 | — |
| **E: pendências da unidade na Lista** | O "Em aberto" de todos os Editais na entrada | J-11 | É a mais cara e arriscada; só depois de C provar a derivação |

| Critério (●●● é o melhor; para esforço e risco, o menor) | A | B | C | D | E |
|---|---|---|---|---|---|
| Clareza para quem opera de vez em quando | ● | ●● | ●●● | ●●● | ●● |
| Fidelidade ao domínio (sem fase única) | ●●● | ●●● | ●●● | ●●● | ●● |
| Carga cognitiva (perguntas respondidas por tela) | ● | ●● | ●●● | ●●● | ●● |
| Esforço | ●●● | ●● | ●● | ● | ● |
| Reaproveitamento do que já é derivado | ●●● | ●●● | ●●● | ●●● | ●● |
| Risco de divergir das telas de ato | ●●● | ●● | ●● | ●● | ● |
| Evolução incremental | ●●● | ●●● | ●●● | ●● | ● |

**Recomendação**: A já, como P0; depois B e C juntas, em dois incrementos; D e E por último, se a
validação pedir. A direção é a mesma da v1; o que mudou é a ordem e a hierarquia.

---

## 2. Prioridades

| Prioridade | Intervenção | Achados | Por quê |
|---|---|---|---|
| **P0** | Corrigir o que induz a erro ou diz o contrário do domínio: a sucessão em destaque logo depois do ato; *Falta* em lista sem inscrito e as duas orientações opostas da convocação; o erro cru da Caixa com `**`; "aguardando resposta" para convocação sem comunicação; o aviso de congelamento fora do lugar | J-08 (a parte de risco), J-06, J-12, J-07, J-10 | Segurança operacional e precisão. **Não depende** da visão de jornada nem do contrato inteiro |
| **P1** | "O que fazer agora" contextual depois da publicação: as providências por papel (nível 1); "Próximo nesta lista" nas mensagens de sucesso; coerência com a faixa da `104` | J-01, J-08 (a parte de orientação), J-09, J-16 | Maior ganho de orientação; depende do contrato de derivação |
| **P2** | O andamento por Perfil e lista, recolhido (nível 2), no lugar do cartão "Classificação" | J-03, J-04, J-13 | Compreensão do Edital com muitas listas; depende do P1 validado |
| **P3** | A condução do marco estendida; a contagem na Lista | J-05, J-11 | Depende da avaliação do P1 e do P2 |

---

## 3. A proposta, em dois níveis

### 3.1 O nível 1: providências, dentro de "O que fazer agora"

O cartão que já existe, no mesmo lugar, passa a começar pelas providências em aberto do Edital. É a
pergunta que ele promete responder.

- **Uma contagem e de quem são**: "2 providências em aberto · 1 é sua". Sem percentual e sem fase.
- **As da pessoa primeiro, destacadas**, com o verbo da tela do ato como link; depois as de outros
  papéis, com o papel no lugar do link; depois as que aguardam fato externo ou estão impedidas, com a
  razão. A ordem é a regra fixa do contrato §4.
- **Até cinco itens**, e "mais N" (o `MOSTRADOS` da `104`).
- **As ações de hoje continuam** (Inscrições, Relatório, Formalização, Encerrar, Cancelar), mas nenhuma
  vem cheia: a ação principal passa a ser a providência da pessoa, quando há uma.
- **O aviso de conteúdo imutável cai para uma linha** no pé do cartão.
- **Sem providência em aberto**, o cartão diz isso, e diz o porquê ("Nada em aberto: a convocação
  terminou e o resultado definitivo foi publicado").

### 3.2 O nível 2: "Andamento da seleção", no lugar do cartão "Classificação"

**[v3]** As colunas não são fixas. A sequência de cada Perfil vem de `classificacao/domain/jornada.jornada()`:
as Etapas, na ordem do Edital, e os marcos depois das Etapas que enumeram. A Etapa ocupa todas as
listas do Perfil; o marco por sorteio abre a ordem em relação, semente e sorteio; o marco por
pontuação tem a ordem depois das Etapas. Detalhes e maquetes `G1` a `G3` no
[complemento](generalidade-da-jornada.md) §4. O resto desta seção vale como estava:

- A linha das inscrições (aberta até / encerrada em, enviadas, rascunhos que não contam).
- **Uma linha por Perfil, recolhida**, com um resumo em palavras ("3 listas · sorteadas, cortadas e
  apuradas · resultado preliminar · convocação: 1 pendente"; ou "Não se aplica: nenhuma inscrição nas
  3 listas").
- **Aberta, a matriz daquele Perfil**: uma linha por lista e uma coluna por ato, com as situações do
  contrato §2, palavra e sinal, e a célula como link para quem abre a tela.
- Os destinos que o cartão "Classificação" oferecia (o sorteio, a condução, o corte, a ocupação, a
  convocação, a divulgação) ficam nas células e no nome do Perfil.

### 3.3 As maquetes v2 e o que custam

Mesmo método da v1: a tela real, com só o trecho proposto trocado e marcado. Medidas a 1280 px, de
`maquetes/medidas-v2.json`.

| Maquete | Papel | Hoje | Proposta | Onde termina o nível 1 |
|---|---|---|---|---|
| `N1-35-quem-conduz` | Gestor | 1767 px (`capturas/04`) | **1732** | 458 px |
| `N1b-…-com-o-perfil-aberto` | Gestor, Cefor aberto | 1767 | 1957 | 458 |
| `N2-35-quem-publica` | Publicador | 1615 (`17`) | **1590** | 458 |
| `N3-35-quem-elabora` | Elaborador | 1175 | **1124** | 458 |
| `N4-57-quem-conduz-…` | Gestor, Design aberto | 1657 (`04b`) | 1804 aberto; ≈1580 recolhido (estimado pela diferença do 35) | 449 |
| `N5-91-presidencia-da-comissao` | Presidência | 1710 | **1403** | 366 |

Em todos os casos, a pergunta "o que é meu" é respondida antes de 460 px: na primeira tela de um
notebook, sem rolar. Recolhido, o nível 2 não deixa nenhuma página mais alta do que hoje. Aberto, ele
acrescenta ~225 px por Perfil de 3 listas, e só para quem pediu.

As maquetes da transição e da condução (`M4`, `M3`, `M3b`) são as da v1. A `M4` é P0 na parte da
sucessão recolhida e P1 na parte do "Próximo nesta lista".

### 3.4 Acessibilidade e linguagem

- O nível 1 é lista (`ul`), com o papel como texto e o ato como link com verbo; "Sua" não é só cor.
- O nível 2 usa `details`/`summary` nativos, que o teclado e o leitor de tela já operam; a matriz é
  tabela com `caption` e `th scope`, na moldura `rolavel-no-estreito` da `058`.
- As situações têm palavra e sinal (✓ ● ◷ —); a cor nunca é a única pista (WCAG 1.4.1).
- O vocabulário é o das telas de ato; "semente" e "relação" ganham definição no "Termos desta tela".

---

## 4. As decisões, com recomendação

Cada uma tem as opções, a recomendação e o fundamento. Todas são do usuário.

### D1. A trilha de situação depois da publicação

| Opção | Efeito |
|---|---|
| a. Manter como está | "Publicado → Encerrado" continua sugerindo que falta pouco (J-02) |
| b. Legendar como "situação do documento" | Corrige a leitura e mantém os ~90 px |
| **c. Recolher depois de publicado** | O selo "Publicado", ao lado do título, já diz a situação; a trilha volta a ser o que é útil: a orientação da pré-publicação |

**Recomendo c.** A trilha só orienta enquanto há passos de documento a dar. Depois da publicação ela
informa uma coisa que o selo já diz, e ocupa o lugar que as providências precisam. *Encerrado* e
*Cancelado* continuam visíveis pelo selo.

### D2. O que entra nas providências

| Opção | Efeito |
|---|---|
| **a. Só o que tem caminho no GPS** | Toda providência é acionável por alguém no sistema |
| b. Também o que acontece fora (a matrícula) | Uma lista que nunca se esvazia |

**Recomendo a**, e uma nota fixa no nível 2 quando toda convocação de um Perfil tiver desfecho: "A
matrícula acontece fora do GPS". Uma providência sem caminho ensina a ignorar a lista. O relatório da
`099` já declara esse limite, e a nota repete a frase dele.

### D3. Quem vê cada nível

| Opção | Efeito |
|---|---|
| a. Os dois níveis só para quem hoje vê o cartão "Classificação" | Quem elabora, homologa ou julga não sabe a quem cabe o que falta |
| b. Os dois níveis para todo papel que abre o Edital | Muda quem vê o quê no nível 2; para quem elabora, +270 px |
| **c. O nível 1 para todos; o nível 2 para quem hoje vê o cartão** | Cada um sabe o que é seu e quem faz o resto; a visibilidade do detalhe não muda |

**Recomendo c.** Dizer "quem publica resultado precisa publicar o definitivo" a quem elabora é
orientação, e não acesso: não mostra candidato, nota nem convocado. Já a matriz por lista expõe
contagens de convocação que hoje só quem conduz, publica ou audita alcança. Mudá-la é decisão de
acesso, e "negar por padrão" pede que ela não venha de carona numa feature de orientação. Na maquete
`N3`, quem elabora vê o nível 1 e não vê o nível 2: a página fica 51 px mais curta do que hoje.

### D4. A Lista

| Opção | Efeito |
|---|---|
| **a. Não muda agora** | A D-002 da `104` vale; quem conduz continua entrando Edital por Edital |
| b. A contagem de providências por linha, em lote | Fecha J-11; custa consultas por linha |

**Recomendo a, até o P2.** A contagem na Lista depende da derivação estar provada no detalhe, e
custaria por linha o que o detalhe custa uma vez. Volta como P3, com orçamento de consulta medido.

### D5. Os nomes

| Opção | Efeito |
|---|---|
| **a. O nível 1 continua "O que fazer agora"; o nível 2 é "Andamento por Perfil"** | Nenhum nome novo onde a pessoa já procura |
| b. "Andamento da seleção" como bloco próprio (a v1) | Um título a mais competindo com "O que fazer agora" |
| c. "Onde estamos" | Sugere uma posição única, que o Edital não tem |

**Recomendo a**, com o nível 2 chamado **"Andamento da seleção"** **[v3]**, como a revisão preferiu:
"da seleção" é transversal, e "por Perfil" descrevia a forma, e não o assunto. O cartão já promete
responder "o que fazer agora"; o defeito é não cumprir. Trocar o nome dele seria tratar o sintoma.

### D6. O Edital por avaliação (Etapas)

| Opção | Efeito |
|---|---|
| **a. Nível 1 no P1, pela `104`; matriz das Etapas no P2** | A presidência vê a avaliação no Edital desde o primeiro incremento (`N5`) |
| b. Tudo no P1 | O P1 cresce com distribuição, avaliação e consolidação |
| **c. [v3] Todas as famílias em cada incremento; os incrementos separam os níveis** | B1: nível 1 para sorteio e Etapas; B2: nível 2 composto para todos |

~~Recomendo a.~~ **[v3] Recomendação revista: nenhuma das duas.** A opção a deixava, no P1, só a
avaliação da própria pessoa (é o que a `104` lê). A distribuição sem avaliador e a consolidação
pendente ficavam de fora, e são justamente as providências da presidência e as que faltaram no 35.
E adiar a matriz das Etapas obrigaria a refazer um nível 2 desenhado para o sorteio.

**Recomendo c: a derivação das Etapas entra junto da do sorteio, e os incrementos escalonam níveis, e
não famílias.** A B1 entrega o nível 1 para todas as famílias; a B2, o nível 2 para todas, composto
pela `jornada()`. Fundamento no [complemento](generalidade-da-jornada.md) §6.

### D9 [v3]. A Etapa que nenhum ato do GPS consome

Opções e fundamento no [complemento](generalidade-da-jornada.md) §10. **Recomendo mostrar sem cobrar**:
"Atenção" no nível 1, coluna "sem efeito no GPS" no nível 2. A decisão de fundo, se a Etapa deve ter
efeito, é de configuração do Edital (G-07).

### D7. "Depois" no lugar de "Falta" na condução do marco

O `data-model.md` da `049` decidiu que o resultado sem ordem conta como *Falta* ("falta a ordem"). O
contrato o lê como *Depois* (contrato §6, D2).

| Opção | Efeito |
|---|---|
| a. Manter *Falta* | A condução e o andamento divergem na palavra |
| **b. *Depois*, sem mudar a contagem** | "Publicação 0 de 3" continua; a palavra deixa de mandar agir onde não é a vez |

**Recomendo b**, no P3, junto da condução estendida. O motivo da `049` (não tirar o recorte da conta)
continua atendido: só a palavra muda.

### D8. O resultado preliminar é "feito" ou "pendente"?

| Opção | Efeito |
|---|---|
| **a. Seguir a pendência que já existe** (`DEFINITIVO_NAO_PUBLICADO`, da `099`/`113`) | Preliminar sem definitivo é providência de quem publica, como o relatório e o Encerrar já dizem |
| b. Decidir pelo marco (pede definitiva se declara recurso) | Regra nova |

**Recomendo a.** Não cria regra: usa a que o relatório e a confirmação de encerrar já aplicam. No 35,
a definitiva do Cefor foi aferida em 06/11 e é publicável agora, e por isso aparece como providência
*Pendente* de quem publica (`N2`).

---

## 5. Escopo das specs

Duas specs, e não uma "da jornada completa".

### 5.1 Spec A: correções de orientação (P0)

**Problema**: cinco mensagens ou estados induzem a erro ou contradizem o domínio.

**Inclui**:

- **A1** Lista sem inscrito num marco de sorteio: *Não se aplica*, sem gesto, na condução e na
  convocação. A convocação deixa de oferecer a faixa seguinte sem corte (J-06).
- **A2** Logo depois de um ato, o formulário de sucessão do mesmo ato vem recolhido e com nome
  próprio ("Suceder este corte (exige motivo)"). Vale para o corte, a ordem, a apuração e a relação do
  sorteio (J-08).
- **A3** A falha de acesso à fonte da semente sem marcação nem erro técnico, dizendo que nada foi
  gravado e que se pode tentar de novo (J-12).
- **A4** "Aguardando resposta" só para prazo em curso; prazo não iniciado é "sem comunicação enviada",
  no relatório e no Encerrar (J-07).
- **A5** O aviso de congelamento inviável junto do formulário de sucessão, e não como primeira frase
  dos recortes, quando todas as relações estão congeladas (J-10; a regra da `102` não muda).

- **A6 [v3]** A ordem por pontuação emitida sem nenhum resultado nas Etapas enumeradas (G-01). A tela
  lista quem está sem posição e por quê, mas oferece "Emitir ordem", irreversível. Nada recusa, e a
  confirmação mostra só as contagens, sem o motivo. **É decisão de regra, e não de orientação**: recusar, ou dizer na conferência quantas
  inscrições estão sem resultado e em quais Etapas. A Spec A registra a decisão e implementa a
  escolhida.

**Exclui**: tudo de orientação nova; o contrato de derivação (só A1 e A4 o seguem).

**Aceitação**: no banco de demonstração, o Polo Vitória do 35 não mostra *Falta* nem gesto; depois de
emitir o corte no 26, o único botão cheio da tela não é de sucessão; o Encerrar do 35 não diz
"aguardando resposta" da convocação de C10.

### 5.2 Spec B: orientação do andamento do Edital (P1 e P2)

**Problema**: depois da publicação, o detalhe do Edital não diz o que está em aberto, de quem é, nem o
que a pessoa pode fazer agora; as transições não dizem o próximo passo (J-01, J-03, J-04, J-08, J-09).

**Objetivo de produto**: o operador compreende o andamento e identifica a providência apropriada **sem
abrir sucessivamente telas operacionais** para descobrir o que falta.

**B1 (P1), requisitos candidatos**:

- **R1** A derivação segue o `contrato-de-derivacao.md`: sete situações, providência com natureza,
  responsável, expectativa e razão; nenhum estado persistido; nenhuma função escolhe um próximo passo
  único.
- **R2** Ausência de ato nunca é exibida como pendência: toda célula sem ato vigente é *Depois*,
  *Aguarda*, *Impedido*, *Não se aplica* ou *Pendente*, pela derivação do contrato §5.
- **R3** "O que fazer agora" do Edital publicado ou encerrado começa pelas providências em aberto, na
  ordem fixa do contrato §4, até cinco e "mais N".
- **R4** A providência da pessoa é link para a tela do ato; a de outro papel nomeia o papel; a que
  aguarda ou está impedida diz a razão com a frase da tela do ato.
- **R5** "O que fazer agora" nunca diz "Nenhum ato disponível" se há providência da pessoa (estende a
  FR-2819 da `104`).
- **R6** A mensagem de sucesso de corte, ordem, relação, semente, apuração, convocação, comunicação e
  conferência diz o próximo passo daquela lista e o que falta em outras listas do mesmo marco, pela
  mesma derivação.
- **R7** A trilha de situação não aparece depois da publicação (D1); o aviso de conteúdo imutável
  ocupa uma linha.
- **R8** Custo fixo por Edital, medido como os da `104`.

**B2 (P2)**:

- **R9** O cartão "Classificação" dá lugar ao "Andamento da seleção": a linha das inscrições e uma
  linha por Perfil, recolhida, com resumo em palavras; aberta, a matriz da §3.2, **composta pela
  `jornada()` da `094`, sem colunas fixas** [v3].
- **R9a [v3]** A matriz rola dentro da própria moldura em qualquer largura; a página nunca rola de
  lado.
- **R9b [v3]** Uma pendência só é descoberta pelo nível 1. A matriz não é o único lugar de nenhuma
  providência.
- **R10** O nível 2 é visível a quem hoje vê o cartão "Classificação" (D3).
- **R11** Recolhido, o nível 2 não deixa a página mais alta do que o cartão que substitui.

**Aceitação (candidata)**:

- **CA1** Nos seis Editais do banco (35, 57, 26, 51, 91, 72) e para cada papel, toda providência
  *Pendente* da pessoa leva a uma tela que oferece o ato habilitado, e toda *Aguarda* ou *Impedido*
  leva a uma tela que o recusa com a mesma razão (contrato §7).
- **CA2** No 35, quem conduz lê "2 providências em aberto · 1 é sua", com a comunicação de C10 primeiro;
  quem publica lê o definitivo como sua; o Polo Vitória não aparece como providência.
- **CA3** No 57, as duas providências de quem conduz são de Perfis diferentes, em situações diferentes.
- **CA4** Depois de emitir o corte da ampla no 26, a mensagem leva à apuração daquela lista e cita a
  lista PPP sem relação.
- **CA5** A 1280 px, o nível 1 termina antes de 500 px do topo em todas as maquetes de §3.3.
- **CA6** Sem migration e sem tabela nova.
- **CA7** Os critérios do `validacao.md` atendidos com as maquetes **antes** do plano da B1.
- **CA8 [v3]** Uma família por linha da matriz de compatibilidade do complemento (§8): S1 (35), S2
  (72), P1 (91), P2 (51) e CR (91) com o banco de demonstração; S3 (habilitação antes do sorteio) e P3
  (vários marcos no Perfil) com cenários compostos para a spec. Um critério que só o sorteio satisfaz
  não aprova a B.
- **CA9 [v3]** No 91, a presidência lê duas providências (avaliar a Prova de Títulos e distribuir a
  de Desempenho Didático), a Entrevista como "Atenção", e a ordem como *Depois* das Etapas, e não como
  *Falta*. No 35, quem conduz lê as duas Etapas declaradas como "Atenção", sem que elas sejam cobradas
  (D9).

**Exclui**: a condução do marco estendida e a Lista (P3); barra de fases; percentual; notificação;
mudança de regra, de permissão, de vigência ou de quem vê o quê no nível 2; a Agenda; a matrícula.

**Casos excepcionais que a spec precisa cobrir**: Retificação que torna ato obsoleto; extração não
publicada e Caixa fora do ar; extração anterior ao congelamento; lista esgotada e faixa seguinte;
desistência e não atendimento; documento pendente; Edital encerrado com convocação aberta; segregação
de funções.

**Riscos**: divergência entre a derivação e a tela do ato (mitigação: um módulo, `interface/andamento.py`,
que chama as funções do contrato, e o CA1 como teste); custo do detalhe (medir antes do plano); a lista
de providências virar painel (mitigação: cinco itens, sem gráfico, sem percentual).

**Validação**: o [roteiro](validacao.md), com as maquetes, antes do plano da B1.
