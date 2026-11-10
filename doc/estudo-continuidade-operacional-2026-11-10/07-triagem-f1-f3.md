# Triagem dos achados F-1, F-2 e F-3 (10/11/2026)

Pedida depois da avaliação do estudo. Para cada achado, a triagem responde três perguntas:
1. **A ação aparece como disponível sem dever** — no Centro (a derivação da 127) e na tela do ato?
2. **Se o operador a pratica, o serviço impede a operação inválida?**
3. **Se o serviço permite, isso é intencional** — por qual spec, decisão ou código?

Nada foi implementado, e a D-5 não foi decidida. As alternativas dela estão na seção 4.

**Onde.** A `main` em `594d8494`, no banco descartável do estudo (`ps_continuidade`), com os
cenários da `134`. Os testes que sustentam as conclusões foram rodados contra PostgreSQL:
`test_sorteio_extracao_inviavel.py`, `test_demonstracao_so_a_data.py`, `test_ordem_sem_resultado.py`,
`test_reabilitacao.py`, `test_publicabilidade.py`, `test_corte_apos_recurso.py` e
`test_corte_obsoleto.py`. São **64 casos, e todos passaram**. As capturas novas têm o prefixo `t`.

## A resposta curta

| | Classificação | Em produção? |
|---|---|---|
| **F-1a** — sem aviso antes de congelar depois da semente | **comportamento intencional** (102, FR-2657, D-006): só a fonte que publica só a data é conferida | não: a Loteria Federal publica só a data, e para ela o aviso existe |
| **F-1b** — o Centro oferece o sorteio de uma relação condenada | **particularidade da fonte de demonstração**, consequência da mesma D-006 | não: com a fonte "só a data", a derivação marca *Impedido* e, depois, *Obsoleto* |
| **F-2** — o Centro oferece a ordem sucessora antes da avaliação do reabilitado | **falha confirmada na derivação**; o serviço aceita por decisão (128), com aviso na conferência | **sim** |
| **F-3** — o resultado do sorteio é publicado com a Etapa enumerada sem consolidação | **comportamento intencional** (127, FR-4060 e D-019; 136, D-008) | — |

Só o F-2 pede correção. O F-1 muda o que se sabe sobre a D-5 (seção 4).

---

## 1. F-1 — a semente antes da segunda lista

### 1.1 Reprodução

| Condição | O que acontece | Evidência |
|---|---|---|
| **Fonte de demonstração** (publica a hora), C06 rodada 1 | congelar a ampla → observar → congelar a PPP: **aceito sem aviso** → o sorteio da PPP é **recusado** → o Centro segue oferecendo "Realizar o sorteio · PPP" | `a04`–`a11`; a tela do sorteio da PPP, depois da recusa, continua sem diagnóstico e com o botão |
| **Fonte "só a data"** (a condição da Loteria Federal), C06 rodada 4, extração declarada em 12/12 | congelar a ampla **hoje** → o retorno **não** aponta "Observar a extração" (a semente fica *Aguarda* até 12/12) | `t01`, `t02` |
| a mesma rodada 4, a derivação avaliada **no dia da extração** (`andamento.do_edital(…, agora=12/12 10h)`) | "Congelar a relação · PPP" vira **Impedido**: "congelar hoje condenaria o sorteio: a extração declarada é de 12/12/2026, e o caminho é retificá-la" | saída do shell, abaixo |

```
== hoje
   pendente | Distribuir 10 inscrições sem avaliador suficiente
   aguarda  | Observar a extração  | a extração 806004106 está prevista para 12/12/2026
   pendente | Congelar a relação · PPP
== 12/12 10h
   pendente | Distribuir 10 inscrições sem avaliador suficiente
   aguarda  | Observar a extração  | a extração 806004106 está prevista para 12/12/2026
   impedido | Congelar a relação · PPP | congelar hoje condenaria o sorteio: a extração declarada é de 12/12/2026, e o caminho é retificá-la
```

**Mais uma proteção, de antes do sorteio.** Gerar a rodada com a extração "só a data" **anterior** ao fim
das inscrições foi recusado na submissão do Edital: "Com este cronograma, o sorteio será sempre
recusado" (102, impeditivo de publicação).

### 1.2 A regra e a origem

- **102, FR-2657 / D-006.** O aviso antes de congelar, o diagnóstico da relação congelada e a conferência
  de publicação valem **só** para fonte que publica só a data: "Hoje nenhuma fonte de produção publica
  a hora". Teste: `test_com_a_fonte_que_publica_a_hora_nao_ha_aviso`.
- **102, FR-2659 / D-005.** O congelamento condenado é **avisado, e nunca recusado**: "a relação pode ter
  data de publicação no cronograma, e quem conduz decide, ciente do que vai acontecer".
- **102, D-007.** A segunda fonte de demonstração ("só a data") existe para reproduzir o caso sem rede.
  A fonte de demonstração de sempre "fica como está".
- **134, D-004.** Os cenários usam a fonte de demonstração de sempre, que publica a hora, para que o C07
  congele e sorteie no mesmo dia. Com "só a data", isso é impossível por construção: a observação é o
  início do dia corrente.
- **A derivação já trata o caso** (`interface/andamento.py`, `situacao_da_relacao`): com o diagnóstico
  da 102, a relação congelada vira *Obsoleta*, com "o caminho começa por uma Retificação"; com o aviso,
  a relação por congelar vira *Impedida*. As duas leem a maquinaria da 102, que se cala para fonte com
  hora.

### 1.3 As três camadas

| Camada | Fonte com hora (treinamento) | Fonte "só a data" (produção) |
|---|---|---|
| **Centro** (derivação) | oferece "Obter a semente" com lista por fixar; depois do congelamento condenado, oferece "Realizar o sorteio" | a semente *Aguarda* até o dia; no dia, congelar é *Impedido*; congelada, é *Obsoleta* |
| **Tela do ato** | sem aviso; sem diagnóstico; o botão "Realizar o sorteio" segue | aviso antes do botão de congelar; diagnóstico e saída em três passos (testes da 102) |
| **Serviço** | congela (D-005); **recusa o sorteio**, com a saída | congela (D-005); recusa o sorteio; antes disso, recusa publicar Edital com extração inviável |

### 1.4 Classificação

- **F-1a** (sem aviso antes do congelamento): **comportamento intencional**, pela D-006.
- **F-1b** (o Centro oferece o sorteio condenado): **particularidade da fonte de demonstração**. É
  efeito da mesma D-006, e só existe onde ela existe: no treinamento e no desenvolvimento.

O serviço protege a integridade nos dois casos, porque nenhum sorteio inválido se constitui. O dano
é o retrabalho: Retificação, sucessão e nova observação. No treinamento, ele se desfaz restaurando o
cenário.

**Um conflito entre duas decisões, e não um defeito.** A D-004 da 134 escolheu treinar com a fonte que a
D-006 da 102 deixou de fora. O guia da equipe compensa por escrito ("Congele as duas antes de observar
a ocorrência"), mas o GPS não ajuda o treinando a não cair no erro.

### 1.5 Consequência de praticar

- **Treinamento:** a PPP não sorteia com aquela extração. A saída é Retificar o método, suceder a
  relação e observar de novo. A ampla, congelada antes, sorteia normalmente.
- **Produção:** a mesma situação **não se forma pela ordem das ações**. A observação só é possível no
  dia da extração, e qualquer congelamento desse dia em diante já está condenado — com ou sem
  observação. O que condena é congelar tarde, e isso a 102 já avisa.

### 1.6 Correção mínima

**Nenhuma obrigatória.** Se o usuário quiser o treinamento fiel à produção, o menor caminho é:

> Em `sorteios/application/previa.py`, `_diagnostico_da_relacao` e `_congelar_agora_inviavel` usam o
> **instante observado** quando a ocorrência já foi observada, qualquer que seja a granularidade da
> fonte. Não há previsão a fazer, porque o instante é fato registrado. A derivação, que já lê os dois,
> passa a dizer *Obsoleto* e *Impedido* sem nenhuma mudança nela.

Isso **revê em parte a D-006**, e por isso é decisão do usuário. Ver também a relação com a D-5, na
seção 4.

### 1.7 Testes de regressão, se a correção for adotada

- fonte com hora: congelar A, observar, abrir a tela → o aviso aparece antes de congelar B;
- fonte com hora: congelar A, observar, congelar B → B tem o diagnóstico e a saída em três passos;
- derivação: B condenada → "Congelar a relação sucessora", com quem resolve "quem retifica", e
  **nenhuma** providência "Realizar o sorteio" em B;
- fonte com hora, sem observação → nada muda (o `test_com_a_fonte_que_publica_a_hora_nao_ha_aviso`
  continua valendo);
- C07 da 134 → congelar, observar e sortear no mesmo dia continua possível.

---

## 2. F-2 — a ordem sucessora antes da avaliação do reabilitado

### 2.1 Reprodução (C08)

1. O recurso do candidato 08 é deferido: Prova objetiva de 5,0 para 6,0, e ele volta ao universo.
2. O Centro oferece, lado a lado, "Distribuir 1 inscrição — Análise de títulos" e "Classificar a lista ·
   no GPS: **emitir a ordem sucessora**", com "o GPS não escolhe a ordem" (`c09`).
3. A prévia da ordem mostra o reabilitado "Sem posição — Sem pontuação nas Etapas enumeradas: Análise
   de títulos" (`c10`).
4. **Emitida a sucessora** (`t03`, `t04`): a conferência **avisa**: "1 das 8 inscrições … está sem
   resultado numa Etapa que o marco enumera … Quando os resultados forem consolidados, esta ordem ficará
   obsoleta, e sucedê-la exigirá motivo". O serviço aceita: 7 com posição e 1 sem.
5. **O Centro passa a oferecer o corte** sobre essa ordem. A publicação fica *Impedida*: "Há inscrição
   reabilitada por recurso cujo resultado ainda não foi consolidado … emita o ato sucessor antes de
   divulgar".
6. **Emitido o corte** (`t05`, `t06`): a tela não diz nada sobre o reabilitado. O serviço aceita: "6
   progridem", com o reabilitado fora da faixa, porque está sem posição. O Centro passa a oferecer
   "Distribuir 6 inscrições — Análise documental".

### 2.2 A regra e a origem

- **127, FR-4068** (`situacao_da_ordem`). A ordem fica *Depois* enquanto as Etapas que ela lê não estão
  feitas: "emiti-la antes delas grava uma ordem que envelhece quando os resultados chegam, e a sucessão
  exige motivo". A docstring registra que a derivação é **mais estrita que o comando de propósito**.
- **128.** O comando recusa a ordem **sem nenhum** Resultado e aceita a **parcial**, com o aviso na
  conferência.
- **A falha.** Em `situacao_da_ordem`, o ramo `estado == "obsoleto"` devolve "Emitir a ordem sucessora"
  **antes** de olhar `faltam`. A mesma função, com a mesma Etapa por fazer:

  ```
  falta    → depois   |                          | a ordem lê Análise de títulos, que ainda não está feita
  obsoleto → obsoleto | Emitir a ordem sucessora | a regra ou o universo mudaram depois da emissão
  ```

- **O que protege o resultado oficial.**
  - A publicação recusa com reingresso pendente (`divulgacao/domain/publicabilidade.py`,
    `REINGRESSO_PENDENTE`).
  - O corte fica obsoleto quando a ordem é sucedida e quando alguém reingressa
    (`classificacao/application/corte.py`, `_reingressou`).

### 2.3 As três camadas

| Camada | Comportamento | Correto? |
|---|---|---|
| **Centro** (derivação) | oferece a sucessora com a Etapa por fazer; depois, o corte sobre a ordem incompleta | **não** — contraria a própria regra da 127 para a primeira ordem |
| **Tela da ordem** | a conferência avisa que a ordem ficará obsoleta | sim |
| **Serviço da ordem** | aceita a parcial | intencional (128) |
| **Tela e serviço do corte** | aceitam sem aviso | lacuna de prevenção: a ordem sabe que está incompleta, e o corte não diz |
| **Publicação** | recusa com reingresso pendente | sim |

### 2.4 Classificação

**Falha confirmada na derivação**, sem perda de integridade. Nenhum resultado oficial sai errado,
porque a publicação recusa. O custo é o retrabalho em cascata, todo com motivo e na trilha:
1. a ordem sucessora é sucedida de novo;
2. o corte fica obsoleto, e é emitida a geração sucessora;
3. a Análise documental já distribuída aos 6 pode ter de mudar de gente.

### 2.5 Consequência de praticar

Seguir o Centro produz dois atos imutáveis que nascem para ser sucedidos. Pode também produzir
avaliações na Etapa seguinte de quem talvez não progrida, se o reabilitado, avaliado, passar à frente.

### 2.6 Correção mínima

Na derivação (`interface/andamento.py`), sem tocar o serviço:
1. **`situacao_da_ordem`:** com `estado == "obsoleto"` e `faltam` não vazio, a ordem não é providência.
   Fica *Depois* com a razão "a ordem sucessora lê Análise de títulos, que ainda não está feita; a vigente
   continua produzindo efeito", ou *Obsoleta* sem ato e com essa razão. A escolha entre as duas é da spec,
   porque o corte e o resultado leem a situação da ordem (`situacao_do_corte`, `_resultado`).
2. **O corte:** enquanto houver reingresso pendente no marco, o corte não é providência. Reaproveite o
   predicado que a publicação já usa (`REINGRESSO_PENDENTE`), em vez de escrever outro.
3. **Opcional, de prevenção:** a tela do corte repete o aviso que a conferência da ordem já dá, quando a
   ordem vigente tem participante sem posição por Etapa enumerada sem resultado.

O serviço continua aceitando a ordem parcial. Mudar isso desfaz a decisão da 128, e nada na triagem
pede isso.

### 2.7 Testes de regressão

- unitário: `situacao_da_ordem` com `obsoleto` e `faltam` → não é providência; sem `faltam` → continua
  "Emitir a ordem sucessora";
- integração, cenário do C08: deferido o recurso que reabilita, o andamento **não** tem "Emitir a ordem
  sucessora" até a Etapa do reabilitado ser consolidada, e passa a ter depois;
- o corte não é providência com reingresso pendente, e volta a ser depois da sucessora completa;
- `test_o_andamento_nunca_diz_pendente_para_a_ordem_que_o_comando_recusa` continua valendo;
- recurso que **não** reabilita (correção de nota de quem já tinha posição) → a sucessora continua
  oferecida na hora.

---

## 3. F-3 — o resultado do sorteio com a Etapa enumerada sem consolidação

### 3.1 Reprodução

No C06, rodada 2, o Publicador publicou o resultado preliminar com a "Análise de títulos" em 0 de 10
(`a16`–`a22`).

### 3.2 A regra e a origem

- O marco do C06 é `orderProduction: POR_SORTEIO` e enumera a Etapa em `stages`.
  `editais/domain/marcos.py::exige_etapa`: "Quem ordena por sorteio não precisa [de Etapa], porque a
  ordem vem da relação de habilitados e não de nota nenhuma".
- **127, FR-4060 e D-019:** a Etapa enumerada por marco de sorteio é "esperada só pela visibilidade e
  pelo recurso, e nenhum ato a lê". O código (`andamento.py`, laço das esperadas) a pula na progressão.
- **136, D-008:** a Etapa é "paralela" quando todos os marcos que a citam são de sorteio sem habilitação.
  É de onde vem a nota "Paralela ao sorteio" do Centro.
- **A publicação** confere, nas Etapas enumeradas, só reingresso e reavaliação pendentes
  (`publicabilidade.py`). No C06 não há nenhum dos dois.

### 3.3 Classificação

**Comportamento intencional.** A consolidação da Etapa enumerada por um marco de sorteio é operação
paralela, e não requisito da publicação. Não há correção a fazer, e impor a dependência contrariaria a
D-019.

**O que sobra é apresentação, já no escopo da 139 se couber.** Depois do sorteio, o retorno diz
"Próximo nesta lista: Distribuir 10 inscrições", e o Centro destaca a Etapa como "Sua próxima ação".
As duas leituras estão certas: é a única ação da pessoa. Mas, ali, o retorno não repete a nota
"Paralela ao sorteio" que o Centro mostra. Isso não pede spec.

---

## 4. A D-5 — as alternativas

> **Decidida pelo usuário em 10/11/2026: alternativa (d).**
> - A observação da semente continua como está: o GPS não impede e não exige confirmação adicional
>   quando há lista por congelar. Os motivos dele: a observação é compartilhada, e um bloqueio
>   prenderia a lista preparada no prazo por causa da atrasada, inclusive entre Editais.
> - Como melhoria pontual, a considerar, e não aprovada como escopo: usar o instante já observado
>   para diagnosticar a relação inviável na fonte de treinamento que publica a hora (seção 1.6).
> - Ressalva registrada por ele: a Loteria Federal real não foi exercitada. A conclusão sobre produção
>   apoia-se no código, nos testes e na fonte "só a data".
> - O texto abaixo é o das alternativas, como foram apresentadas.


**A pergunta.** Quando uma ocorrência vai ser observada e ainda há lista com participantes por
congelar, o GPS deve **(a)** impedir a observação, **(b)** exigir uma confirmação adicional, ou **(c)**
apenas alertar?

**O que a triagem acrescenta, e que muda o peso da decisão.**
1. **Com a Loteria Federal, a ordem "observar → congelar" não é o risco.** A observação só é possível
   no dia da extração, e todo congelamento desse dia em diante já está condenado, com ou sem
   observação. O risco real é congelar tarde, e a 102 já o avisa: na tela, antes do botão; no Centro,
   como *Impedido*; na publicação do Edital, como impeditivo. **Em produção, nenhuma das três
   alternativas muda o desfecho.**
2. **O risco da D-5 só se materializa com fonte que publica a hora**, e hoje essa fonte só existe no
   treinamento e no desenvolvimento.
3. **A observação é compartilhada.** Uma observação serve a todo marco da mesma fonte e referência
   (`andamento.py`, `chave_da_semente`), inclusive de outro Edital que cite o mesmo concurso.
   "Haver lista por congelar" precisa de um escopo: o marco, o Edital ou todos os que citam a
   referência.
4. **Há listas que legitimamente não podem ser congeladas ainda:** a que espera a Etapa de habilitação
   (*Depois*) e a vazia (*Não se aplica*). Nenhuma alternativa pode contá-las.

| Alternativa | O que faz | A favor | Contra | Por lista e por fonte |
|---|---|---|---|---|
| **(a) Impedir** | o serviço recusa observar enquanto houver lista com participantes por congelar no escopo | elimina a armadilha da fonte com hora | **em produção, prejudica:** a ampla congelada no prazo não poderia ser sorteada enquanto a PPP, que já não tem como ser congelada a tempo, não fosse congelada — e congelá-la a condena. Prende a lista boa por causa da ruim, e força Retificação de tudo. Pelo escopo compartilhado, um Edital pode travar outro | precisa excluir as listas *Depois* e *Não se aplica*, e definir o escopo entre marcos e Editais |
| **(b) Confirmar** | observar com lista por congelar passa por uma conferência que nomeia as listas e diz a consequência | informa sem travar; segue o padrão "Confira antes de…" (P-2) | mais um passo num ato raro; o texto depende da fonte (com hora: "a lista não poderá ser sorteada"; só a data: "ela já está condenada se for congelada hoje", o que independe da observação) | a conferência lista as listas do escopo; com fonte "só a data" quase sempre repete o aviso da 102 |
| **(c) Alertar** | uma frase junto do botão de observar, no retorno do congelamento e no Centro (o protótipo do estudo, marcado D-5) | o menor custo; coerente com a D-005 da 102 (avisar, nunca recusar) | pode ser ignorado; na fonte "só a data", duplica o aviso que já existe | idem (b), sem a parada |
| **(d) Não decidir agora** | deixar a observação como está e, se o usuário quiser, adotar a correção do F-1 (seção 1.6), que faz a 102 valer depois da observação para fonte com hora | ataca o caso onde ele existe (o treinamento) sem regra nova na observação | revê em parte a D-006 | — |

**A decisão é do usuário.** A triagem não recomenda nenhuma das quatro. Ela só registra o que muda:
em produção, o risco que motivou a D-5 já está coberto pela 102.

---

## 5. Tabela decisória

| Achado | Classificação | Evidência | Risco | Correção recomendada | Spec? |
|---|---|---|---|---|---|
| **F-1a** — sem aviso antes de congelar depois da semente | comportamento intencional (102, D-006) | `a04`–`a08`; `test_com_a_fonte_que_publica_a_hora_nao_ha_aviso` | baixo; só no treinamento | nenhuma obrigatória | não |
| **F-1b** — o Centro oferece o sorteio condenado | particularidade da fonte de demonstração (102, D-006; 134, D-004) | `a10`, `a11`; rodada 4, `t01`, `t02` e o shell no dia da extração | baixo em produção (não ocorre); médio no treinamento (ensina a armadilha) | **opcional:** usar o instante observado no diagnóstico e no aviso da 102 (1.6) | só se adotada: emenda à 102, com revisão da D-006 (decisão do usuário) |
| **F-2** — a ordem sucessora e o corte antes da avaliação do reabilitado | **falha confirmada na derivação**; o serviço aceita a parcial por decisão (128) | `c09`, `c10`, `t03`–`t06`; a função pura `situacao_da_ordem` | médio: retrabalho em cascata, sem resultado oficial errado (a publicação recusa) | derivação: sucessora e corte não são providência com Etapa por fazer ou reingresso pendente; aviso opcional no corte (2.6) | **sim, mínima**, no molde da 135 (correções da derivação) |
| **F-3** — o resultado do sorteio com a Etapa enumerada sem consolidação | comportamento intencional (127, FR-4060 e D-019; 136, D-008) | `a16`–`a22`; `andamento.py`, laço das esperadas | nenhum | nenhuma; a nota "Paralela ao sorteio" no retorno, se couber na 139 | não |
| **D-5** | **decidida em 10/11: alternativa (d)** | seção 4 | em produção, coberto pela 102 | nenhuma regra nova na observação; a melhoria do F-1 (1.6), a considerar | não |

## Capturas novas

| | |
|---|---|
| `t01-c06r4-so-a-data-apos-fixar-ampla` | fonte "só a data": depois de congelar a ampla, o retorno não aponta a semente |
| `t02-c06r4-centro-hoje` | o Centro da rodada 4: a semente aguarda o dia da extração |
| `t03-c08-sucessora-conferencia` | a conferência da sucessora avisa que ela ficará obsoleta |
| `t04-c08-sucessora-emitida` | emitida a sucessora parcial |
| `t05-c08-corte-sobre-ordem-incompleta` | a tela do corte, sem aviso sobre o reabilitado |
| `t06-c08-corte-emitido-sobre-incompleta` | o corte emitido; o próximo é distribuir a Análise documental |

## Limitações

- **A Loteria Federal real não foi chamada.** A condição de produção foi reproduzida com a fonte "só a
  data", que a 102 (D-007) criou para isso, e com a derivação avaliada num instante futuro. A tela no
  dia da extração não foi vista no navegador; quem a cobre são os testes da 102.
- **A correção do F-2 não foi prototipada.** As consequências para o corte e o resultado, que leem a
  situação da ordem, ficam para a spec, com os testes da seção 2.7.
