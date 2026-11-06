# Complemento: a orientação serve a toda forma de classificação?

Parte do [estudo de orientação da jornada](README.md). Na segunda revisão de 06/11/2026, este
complemento passou a ser **requisito de aprovação da Spec B**. Ele precisa comprovar que a proposta é
transversal ao GPS, e não uma "jornada do sorteio" com adaptações. Nada foi implementado.

Referências relativas a `backend/processo_seletivo/`, na base `250efe97`. O fluxo das Etapas, ato a
ato e com `arquivo:linha`, está no [mapa das Etapas](mapa-das-etapas.md). As capturas novas são as
`30` a `36`, e as maquetes novas são as `G1` a `G3` (roteiro `maquetes_v3.py`).

**Resposta curta.**

- **As sete situações e o nível 1 já são genéricos.** Servem às duas famílias de ordem.
- **O nível 2 da v2 não era genérico.** As colunas eram as do sorteio, e as Etapas de avaliação nem
  apareciam.
- **A correção não pede motor novo.** A ordem dos passos de cada Perfil já é derivada da configuração
  por `classificacao/domain/jornada.jornada()`, da `094`. O nível 2 passa a ser essa sequência,
  preenchida com as situações.
- **Uma regra que a v2 não tinha é obrigatória.** Uma Etapa só é providência quando algum ato do GPS
  depende dela. As que nada consome aparecem, mas não são cobradas (D9).
- **A Spec B precisa de cinco ajustes de escopo antes de ser aprovada** (§10).

---

## 1. O que o GPS implementa (pergunta 1)

O GPS não tem "métodos de classificação" como enumeração. Tem peças combináveis, e as famílias são as
combinações que a configuração permite.

### 1.1 As peças

| Peça | O que é | Onde |
|---|---|---|
| **Etapa** (`stages`) | Avaliação da comissão, por inscrição, que vale para o Edital inteiro (não por lista). Tem duas formas. `PONTUADA`: nota, mínimo, máximo, peso, eliminatória e/ou classificatória. `DECISORIA`: favorável/desfavorável, com o rótulo do Edital, e só se consolida se for eliminatória. O fluxo é alocar → distribuir → avaliar → consolidar. **Não há ato de publicar o resultado de uma Etapa**: ele chega ao candidato pelo marco que a enumera | `avaliacoes/domain/formas.py:21-29`; `resultados/domain/regra.py:57-143`; mapa das Etapas §0 e §1 |
| **Marco classificatório** | Produz a **ordem** de cada lista do Perfil. A origem é `COMPUTADO` (pontuação: soma ou média ponderada das Etapas que enumera) ou `SORTEIO` (relação, semente, sorteio) | `classificacao/models.py:18-22`; `editais/domain/marcos.py:114-158, 251` |
| **As quatro ligações entre Etapa e marco** | **enumerada**: dá nota, ou porta, à ordem, e torna o resultado visível e recorrível depois da publicação do marco; **governada pelo corte**: só a faixa participa, e o "habilitada" dela decide ocupação e convocação; **habilitação do sorteio** (`qualifyingStageId`): filtra a relação; **progressão**: quem foi eliminado numa Etapa sai das seguintes, sem passar por marco | `editais/domain/validation.py:2024-2067`; `resultados/application/prontidao.py:263-473` |
| **Depois da ordem** | Corte, apuração, divulgação e convocação, **iguais** nas duas origens | `016`, `017`, `019` |

**Não existem** ordem por protocolo, ordem de chegada, classificação manual, ato de divergência entre
avaliadores (com mais de uma avaliação prevista, a Etapa inteira fica bloqueada:
`regra_de_combinacao_ausente`), homologação de resultado nem convocação para comparecer a uma Etapa
([registro de 09/10](../registro-convocacao-para-etapas-2026-10-09.md)). O desempate é por nota de uma
Etapa ou por valor de fato; o empate residual compartilha a posição. O cadastro de reserva não é
método: é Perfil com zero vaga imediata (096, 097).

### 1.2 As famílias que existem de fato

Para classificar, usei a configuração publicada e a função oficial de cada pergunta (roteiro
`configuracao2.py`, no scratchpad da sessão).

| Família | Configuração | Edital |
|---|---|---|
| **S1** Sorteio, com Etapas que nada consome | Marco por sorteio que não enumera Etapa; Etapas decisórias declaradas sem ligação com marco | 35, 57 |
| **S2** Sorteio que enumera Etapa | O marco por sorteio enumera uma Etapa. Ela **não entra na ordem**, mas torna o resultado dela visível e recorrível (`faixa.py:93-97`; mapa §3.2 d) | 69, 71, 72 (uma decisória **não eliminatória** chamada "Sorteio", que nem consolida); 26 (Análise de títulos) |
| **S3** Sorteio com habilitação prévia | `qualifyingStageId`: a relação só congela quem tem resultado favorável na Etapa | nenhum no banco; fixtures em `tests/interface/test_metodo_do_marco.py` |
| **P1** Pontuação simples | Marco por pontuação que enumera Etapas pontuadas; corte sem Etapa governada | 91 (e uma decisória depois do marco, que nada consome) |
| **P2** Pontuação com Etapa governada | O corte alimenta uma Etapa (Análise documental decisória, ou Entrevista pontuada), que decide ocupação e convocação | 51, 01; `tests/fixtures/corte.py:29-75` |
| **P3** Vários marcos no Perfil | Marco 1 → corte → Etapa governada → marco 2 | nenhum no banco nem nas fixtures achadas; a `jornada()` o prevê |
| **CR** Cadastro de reserva | Qualquer das anteriores, com zero vaga imediata | 91, 72, Técnico de Laboratório do 51 |

O marco é do Perfil, e a forma é do marco. Por isso, **Perfis de famílias diferentes no mesmo Edital**
são possíveis. No banco, o 51 tem um Perfil P2 e um CR sem Etapa governada.

---

## 2. As sete situações são suficientes? (pergunta 2)

**Para os estados, sim; para os atos, não.** As situações descrevem a relação entre um ato esperado e o
que aconteceu, e não dependem da família. Os atos e a **expectativa** de cada um dependem dela.

| Situação | No sorteio | Na Etapa | Na ordem por pontuação |
|---|---|---|---|
| Feito | relação congelada; sorteio vigente | todas as inscrições participantes consolidadas | ordem vigente |
| Pendente | congelar; observar; sortear | distribuir (inscrição sem avaliador); avaliar (avaliação pendente); consolidar (pronta para consolidar) | emitir, com as Etapas enumeradas consolidadas |
| Aguarda | a extração; o fim das inscrições | o fim das inscrições (`inscricoes_em_curso` recusa distribuir); o Evento da Etapa no cronograma, quando há | — |
| Impedido | extração anterior ao congelamento | `regra_de_combinacao_ausente` (mais de uma avaliação prevista); `regra_insuficiente` (decisória não eliminatória, pontuada eliminatória sem mínima); corte obsoleto que governa a Etapa | `resultado_sem_norma` |
| Depois | sortear antes da semente | Etapa governada antes do corte; inscrição aguardando a Etapa anterior | **ordem antes das Etapas enumeradas consolidadas** |
| Não se aplica | lista sem inscrito | inscrição fora da faixa; eliminada em Etapa anterior | Perfil sem inscrito (a ordem vazia é "ninguém concorreu", D-003 da `049`) |
| Obsoleto | relação sucedida | resultado sucedido por reavaliação | ordem emitida antes de resultados que chegaram depois (`universo.py:82-123`) |

**A Etapa anda inscrição a inscrição**: "8 de 12 avaliadas" é *Pendente* com contagem, e não um estado
novo. A partição já existe (`prontidao.panorama_da_etapa`): eliminada antes, aguardando a anterior,
fora do corte, consolidada, pronta, não consolidável, reavaliação determinada (mapa §1.5).

**O que falta é a expectativa, e não um estado.** A Etapa que nenhum ato consome não é *Pendente*
nem *Não se aplica*. Ela é declarada, e nada do GPS depende dela. O contrato precisa dizer de onde vem
a expectativa:

| Ligação da Etapa | Expectativa | Por quê |
|---|---|---|
| Enumerada por marco de **pontuação** | Esperada | sem ela a ordem não sai |
| **Governada** pelo corte | Esperada | ocupação e convocação contam o "habilitada" dela |
| **Habilitação** do sorteio | Esperada, **antes** da relação | a relação lê o resultado dela |
| Só **progressão**, antes de uma Etapa esperada | Esperada | filtra quem segue |
| Enumerada por marco de **sorteio** | Esperada só se for consolidável | dá visibilidade e recurso; a decisória não eliminatória ("Sorteio" do 69, 71 e 72) nem consolida |
| **Nenhuma** das anteriores | **Declarada, sem efeito no GPS** | nada a jusante a lê, e o resultado não chega ao candidato (35, 57; a Entrevista do 91) |

---

## 3. "O que fazer agora" sem depender do sorteio (pergunta 3)

O nível 1 lista **providências**, com a mesma estrutura em qualquer família (contrato §3). Muda a fonte.
Nos três Editais exercitados:

| Edital (família), papel | Providências | Atenção (D9) | Maquete |
|---|---|---|---|
| 91 (P1, CR), presidência | Avaliar as 12 da Prova de Títulos (o avaliador alocado é a própria presidência, conferido no banco); distribuir as 12 da Prova de Desempenho Didático. A classificação fica *Depois* das duas | Entrevista: 12 sem avaliador; nada depende dela | `G1` |
| 35 (S1), quem conduz | Emitir a comunicação de C10; e, de quem publica, o definitivo | Análise da documentação e verificação da autodeclaração: 11 sem avaliador cada; nada depende delas | `G2` |
| 51 (P2, CR), quem conduz | Emitir a comunicação da convocação (prazo não iniciado); emitir a ordem da lista PPP. Técnico de Laboratório: *Não se aplica* | — | `G3` |

**As fontes existem, e nenhuma é do sorteio.**

| O que | Fonte | Lacuna hoje |
|---|---|---|
| Avaliar (do avaliador) | `trabalho._das_avaliacoes` (104), a carga de Minhas Etapas | — |
| Distribuir, avaliar, consolidar (da Etapa) | `panorama.contagens` e `resumo_da_etapa`, de custo constante (mapa §4) | **a `104` não tem objeto para a presidência** ("distribuir", "consolidar N prontas"); a Supervisão não tem sinal de "falta consolidar" |
| Por Perfil | — | o panorama é por Etapa sobre o Edital; dá para anotar o Perfil na mesma consulta [I] |
| Recurso e reavaliação | `pendencias_do_edital`, `reavaliacoes_pendentes` | — |

**Correção registrada.** A v2 mostrava "2 providências" no 35. A primeira montagem da v3 mostrava 4,
cobrando as duas Etapas sem avaliador. O mapa das Etapas mostrou que nada as consome: no 35 elas não
entram em marco nem filtram a relação. As 2 da v2 estavam certas como providências. O erro da v2 era
**não mostrar as Etapas em lugar nenhum**: a v3 as põe no nível 1 como "Atenção" e no nível 2 como
coluna.

---

## 4. O "Andamento da seleção" composto pela configuração (pergunta 4)

**Colunas fixas, não.** No 91, as colunas da v2 (Relação, Semente, Sorteio…) dariam três colunas
vazias e nenhuma para as Etapas.

**A composição:**

1. **A sequência do Perfil vem de `jornada()`** (`classificacao/domain/jornada.py:33`). Ela é pura, já
   trata o que não é linear e já marca `porta` e `etapa_alimentada`:
   - cada Etapa, na `order` dela;
   - cada marco depois da última Etapa que enumera, ou no começo, se não enumera nenhuma;
   - a Etapa governada depois do corte que a alimenta;
   - a Etapa sem ligação, onde o Edital a pôs.

   Hoje só a prévia da classificação usa essa função. Falta-lhe o estado de execução, e é isso que o
   contrato acrescenta.
2. **Cada ponto vira coluna.**
   - A Etapa ocupa todas as listas do Perfil.
   - O marco por sorteio abre a ordem em relação, semente (comum às listas) e sorteio.
   - O marco por pontuação tem a ordem.
   - Corte, apuração, resultado e convocação são por lista.
3. **Grupos de colunas dizem de onde cada uma vem**: "Etapas · valem para o Perfil", "Marco · por
   pontuação, por lista", "Etapa governada pela faixa", "Etapas que nenhum ato consome" (`G1` a `G3`).
4. **Perfis de famílias diferentes** são linhas recolhidas diferentes, cada uma com a sua sequência. O
   resumo em palavras começa pela forma ("por pontuação", "por sorteio").
5. **O não aplicável** não é coluna vazia:
   - o Perfil sem inscrito é uma linha só (o 3º Perfil do 91, o Técnico de Laboratório do 51, o Polo
     Vitória do 35);
   - a lista sem vaga no quadro é *Não se aplica* na célula;
   - a Etapa sem efeito tem célula própria, "sem efeito no GPS", sem cobrar.
6. **Etapa opcional não existe** na configuração. O que existe é Etapa sem ligação, tratada pela D9.

**O custo visual apareceu na maquete.** Com 8 ou 9 colunas, a matriz não cabe a 1280 px. Na primeira
montagem, ela empurrou a página para 1370 px. A v3 a põe numa moldura que rola por dentro em qualquer
largura (não só a 375 px, como a `058` previu). No 35, isso deixa as Etapas no fim da linha, fora da
vista (`G2`). Daí a regra: **quem descobre o que fazer é o nível 1, e nunca a matriz.**

---

## 5. Dependências de várias Etapas, critérios e homologação (pergunta 5)

| Dependência | Existe? | Como a proposta a comunica |
|---|---|---|
| Ordem que combina várias Etapas | Sim (`combinacao.py`: soma ou média ponderada, normalização, arredondamento) | A ordem fica *Depois* "da Prova de Títulos e do Desempenho Didático" (`G1`). A tela da ordem já lista o motivo de cada um sem posição ("Sem pontuação nas Etapas enumeradas: …", captura `32`) |
| Etapa eliminatória | Sim (nota abaixo da mínima; decisória desfavorável) | É resultado, e não providência. Aparece como *Não se aplica* nas Etapas seguintes daquela pessoa |
| Progressão entre Etapas | Sim (eliminada antes sai; só segue quem foi habilitado na anterior) | A coluna da Etapa seguinte conta só os participantes; "aguardando a anterior" é *Depois* |
| Desempate por Etapa não enumerada | Sim (114) | Entra na sequência como Etapa esperada. **A verificar** se `jornada()` a inclui |
| Etapa governada | Sim | Coluna depois do corte, "só a faixa" (`G3`). Bloqueada se o corte estiver obsoleto |
| Habilitação antes do sorteio | Sim | Relação *Depois* da Etapa de habilitação. **Sem cenário no banco** |
| Recurso e reavaliação | Sim (018, 036): contra o resultado do marco ou da Etapa enumerada | Pelas pendências que já existem |
| Homologação | Só do Edital e da Retificação | Nada a comunicar além do que existe |
| Convocação para comparecer a Etapa | **Não existe** | A Etapa mostra a data do Evento, quando há; não promete convocação que o sistema não faz |

---

## 6. A D6 é coerente? (pergunta 6)

**Não, como estava.** A D6 da v2 punha a avaliação no nível 1 já no P1, pela `104`, e adiava a matriz
das Etapas para o P2. Isso deixava três buracos:

- **o nível 1 do P1 cobriria só a avaliação do avaliador**, porque é o que a `104` lê. Distribuir e
  consolidar, que são da presidência, ficariam de fora;
- **o nível 2 do P2, desenhado para o sorteio,** teria de ser refeito para as Etapas, que é a
  "adaptação posterior" que a revisão quer evitar;
- **num Edital por pontuação, entre o P1 e o P2,** a avaliação apareceria no nível 1 e não teria
  coluna nenhuma no nível 2.

**Recomendação revista (D6 c):** a derivação das Etapas entra no mesmo incremento que a do sorteio. Os
incrementos escalonam os **níveis**, e não as famílias.

---

## 7. Reaproveita ou reinterpreta? (pergunta 7)

**Reaproveita.** Há duas exceções, que são regra, e não orientação:

| O que a proposta lê | Já existe em | Novo? |
|---|---|---|
| A sequência do Perfil | `jornada()` (094) | Não |
| A forma do marco | `marcos.marco_ordena_por_sorteio`, `metodo_que_governa` | Não |
| As ligações da Etapa | `validation._quem_exige_o_resultado` (`:2024-2067`), `faixa.etapa_governada`, `qualifyingStageId` | Não. A expectativa da §2 é a leitura delas |
| O estado da Etapa | `prontidao.panorama_da_etapa`, `resumo_da_etapa`, a carga de Minhas Etapas | Não. A quebra por Perfil é anotação na mesma consulta [I] |
| O estado do sorteio | `previa.recortes_do_marco`, `sorteios_do_edital` | Não |
| Ordem, corte, apuração, resultado | `indicador_do_marco`, `resumo_dos_marcos` | Não |
| A convocação | `prazo.estado`, `leitura_do_recorte` | Não |
| As pendências do Edital | `pendencias_do_edital`, `fatos_do_edital`, `supervisao.sinais` | Não |
| **"A ordem por pontuação espera as Etapas"** | Nada recusa: `calcular_ordem` e `emitir_ordem` gravam a ordem vazia (mapa §2) | **Regra**. Ver G-01 |
| **"Esta Etapa nada consome"** | A validação já sabe, para advertir na publicação (`validation.py:2085-2135`) | **Decisão** de como mostrar: D9 |

---

## 8. Matriz de compatibilidade

Uma linha por família implementada. "Cobertura" é a da **proposta v2**, antes deste complemento.

| Família | Atos e dependências | Como determina a situação | Como determina as providências | Como apresenta o andamento | Excepcionais | Cobertura v2 | Ajuste |
|---|---|---|---|---|---|---|---|
| **S1** (35, 57) | inscrições → relação → semente → sorteio → corte → apuração → resultado → convocação; Etapas sem ligação, em paralelo | contrato §5 | condução, sorteio, convocação | colunas fixas do sorteio | extração cedo ou indisponível; relação condenada; lista vazia; desistência | **Parcial**: as Etapas não apareciam em lugar nenhum | Etapas no nível 2 e como Atenção (D9) (`G2`) |
| **S2** (69, 71, 72, 26) | idem S1; a Etapa enumerada dá visibilidade e recurso, e não ordem | idem, mais a expectativa da Etapa | idem | idem | decisória não eliminatória enumerada: não consolida | **Parcial** | não cobrar a Etapa que não consolida; registrar a configuração (G-05) |
| **S3** (fixture) | Etapa de habilitação → relação → … | relação *Depois* da habilitação | distribuir e consolidar a habilitação | — | habilitação revista depois do congelamento | **Ausente** | a relação lê `habilitadas_na_etapa`; coluna da Etapa antes do marco. **Cenário composto para a spec** |
| **P1** (91) | inscrições → Etapas (distribuir, avaliar, consolidar) → ordem → corte → apuração → resultado → convocação | Etapa pelo panorama; ordem *Depois* | avaliador (104); presidência (panorama) | **sem coluna para as Etapas** | Etapa bloqueada pela regra; eliminação; reavaliação; Perfil vazio | **Parcial no nível 1, ausente no nível 2** | composição pela `jornada()`; objeto da presidência; G-01 (`G1`) |
| **P2** (51, 01) | … → ordem → corte (faixa) → Etapa governada → apuração → convocação (pelo "habilitada" dela) | idem P1, mais a governada *Depois* do corte | idem | idem | corte obsoleto bloqueia a governada; faixa seguinte reabre | **Parcial** | coluna "Etapa governada pela faixa" (`G3`) |
| **P3** (nenhum) | Etapas → marco 1 → corte → governada → marco 2 | idem, por marco | idem | um grupo de colunas por marco | retorno da faixa seguinte | **Ausente** | a `jornada()` ordena; **validar com cenário composto à mão antes do plano** |
| **CR** (91, 72, 51) | qualquer das anteriores, sem vaga imediata | apuração *Não se aplica* sem quadro | ocupação (097) | idem | vaga acrescida e desfeita | **Parcial** | razão na célula (`G1`) |

---

## 9. Achados novos

| ID | Achado | Evidência | Natureza | Destino |
|---|---|---|---|---|
| **G-01** | A tela da ordem por pontuação lista as 8 inscrições sem posição, com o motivo "Sem pontuação nas Etapas enumeradas", e **ainda assim oferece "Emitir ordem", irreversível**. Nada recusa, e a confirmação mostra só "com posição: 0 / sem posição: 8", sem o motivo. A ordem vazia fica obsoleta quando os resultados chegarem, e a sucessão exige motivo | `32`; `classificacao/application/emissao.py:148-163`; `ordenacao_confirmar.html:44-53` | Segurança operacional; decisão de regra | **Spec A** (A6): recusar enquanto alguma Etapa enumerada não tiver resultado, ou dizer o motivo na confirmação |
| **G-02** | A condução de marco por pontuação diz *Falta* na ordem quando o que falta são as avaliações | `31` | Orientação | Spec B |
| **G-03** | O detalhe do Edital não leva às Etapas; distribuir só se alcança por Processo → Alocação por Etapa, ou por Minhas Etapas | `30` | Navegação | Spec B (o nível 1 leva à distribuição) |
| **G-04** | A `104` não tem objeto de trabalho para a presidência (distribuir, consolidar), e a Supervisão não tem sinal de "falta consolidar" | `interface/trabalho.py:176-196`; mapa §4 | Orientação | Spec B, B1 |
| **G-05** | No 69, 71 e 72, uma Etapa decisória **não eliminatória** chamada "Sorteio" é enumerada pelo marco de sorteio. Ela aparece na Mesa, é distribuível e nunca consolida | configuração publicada; mapa §3.2 d | Configuração ambígua | Registro para a equipe |
| **G-06** | Com 8 ou 9 colunas, a matriz não cabe a 1280 px | primeira montagem de `G1` | Apresentação | Requisito da Spec B |
| **G-07** | Resultado de Etapa não enumerada (governada ou sem ligação) **não é visível ao candidato nem recorrível**; e Etapa sem ligação não tem efeito a jusante. No 35, as duas Etapas decisórias (análise da documentação, autodeclaração) não alteram a relação, a ocupação nem a convocação | mapa §3.1 e §3.2 | **Governança**: o Edital declara uma etapa que o sistema não aplica | Registro para a equipe; não é escopo de orientação |

---

## 10. Recomendação sobre a Spec B

**Não aprovar como está. Aprovar com cinco ajustes de escopo**, sem mudar a direção:

1. **O contrato ganha a seção Etapa e a expectativa por ligação** (§2). A ordem por pontuação é
   *Depois* das Etapas enumeradas, e a relação do sorteio é *Depois* da Etapa de habilitação.
2. **O nível 2 se compõe pela `jornada()` da `094`**, sem colunas fixas. Tem grupos de colunas por
   origem, a Etapa ocupando todas as listas, e rolagem dentro da moldura em toda largura.
3. **Os incrementos escalonam níveis, e não famílias** (D6 c). A B1 entrega o nível 1 para todas as
   famílias, com objeto de trabalho para a presidência (G-04). A B2 entrega o nível 2 para todas.
4. **A D9 é decidida antes do plano**: como mostrar a Etapa que nada consome.
5. **O critério de aceitação cobre uma família por linha da matriz do §8.** S1 (35), S2 (72), P1 (91),
   P2 (51) e CR (91) usam o banco de demonstração. S3 e P3 usam cenários compostos para a spec,
   porque o banco não os tem. Um critério que só o sorteio satisfaça não aprova a B.

**Fora da B**: a G-01 vai para a Spec A, como decisão de regra. A G-05 e a G-07 vão para registro,
porque são de configuração e de governança, e não de orientação.

**O nome do nível 2 volta a ser "Andamento da seleção"**, como a revisão preferiu. O nível 1 continua
"O que fazer agora", que é o cartão de hoje (D5).

### D9. A Etapa que nenhum ato do GPS consome

| Opção | Efeito |
|---|---|
| a. Cobrar como qualquer Etapa | O nível 1 manda distribuir e avaliar o que não muda nada no sistema; e a Supervisão já faz isso (UX-003) |
| **b. Mostrar sem cobrar** | No nível 1, uma linha "Atenção", que diz que a Etapa está declarada e que nada no GPS depende dela; no nível 2, a coluna "sem efeito no GPS" |
| c. Esconder | Some do sistema uma etapa que o Edital publicou |

**Recomendo b.** Ela não esconde o que o Edital declarou, e não faz a orientação mandar trabalho que o
sistema não usa. Ela também aponta para a G-07, que é a decisão de fundo: se a Etapa deve ou não ter
efeito, o que se resolve na configuração do Edital, e não na tela.

---

## Limites deste complemento

- **S3 e P3 não têm cenário no banco.** S3 tem fixtures; P3, não achei. As duas linhas são leitura de
  código e da `jornada()`, e não percurso.
- **As contagens por Perfil das maquetes `G1`** (8 inscrições) supõem a anotação do Perfil no
  panorama, que não existe e não foi medida.
- **Nenhuma avaliação, consolidação ou recurso foi praticado no navegador.** O fluxo vem do mapa das
  Etapas e das telas de distribuição.
- **A primeira captura da G-01 era do Perfil errado**, sem inscrição: a ordem vazia ali é legítima
  ("ninguém concorreu"). A `32` atual é a do Perfil com 8 inscrições.
- **As maquetes v3 mostram o nível 2 aberto**, para exibir a composição. Recolhido, a altura é a da v2.
