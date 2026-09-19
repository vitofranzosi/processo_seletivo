# Percursos — e o que registrar quando não houver caminho

**Tudo pela interface.** Shell, banco e relógio servem para preparar o ambiente e diagnosticar,
**nunca para atravessar um passo que deveria estar disponível à pessoa**. Não havendo caminho pela
interface, o percurso **registra a lacuna** e segue — foi o que a `034` fez, e é o protocolo.

## Antes de começar

O seletor de identidade da gestão e o do canal do candidato precisam estar ligados; sem eles as
telas devolvem 503. O Edital de trabalho precisa de **um marco classificatório** e de **um Perfil**.

---

## Cenário 1 — o caminho até o corte, e o caminho que ele oferece (`SC-188`)

1. Componha um marco classificatório **sem declarar regra de corte** e publique o Edital.
2. Abra a tela do Edital como quem conduz a classificação.

**Esperado**: o destino do corte **é oferecido**. Hoje ele não é.

3. Abra o destino do corte.

**Esperado**: a tela diz que **este marco não declara regra de corte**, e o caminho que ela oferece é
**o da regra**, e não o da classificação.

### A contraprova, e é ela que separa a feature de um beco novo

4. No mesmo Edital, num marco **com** regra de corte mas **sem ordem emitida**, abra o corte.

**Esperado**: a recusa é outra — falta a ordem — e o caminho **continua sendo o da classificação**.
Se os dois casos oferecerem o mesmo caminho, a `FR-539a` não foi cumprida, ainda que o link do
cenário 1 tenha aparecido corretamente.

5. Volte ao marco **sem regra** e abra o corte como alguém que classifica e **não alcança a
   Retificação**.

**Esperado**: ele lê a recusa e recebe **a frase que diz a quem pedir** — e não um caminho que não
abre. É o segundo lugar desta feature onde o beco da `033` cabe.

6. Entre como alguém que **não alcança** a classificação deste Edital.

**Esperado**: nenhum destino de corte é oferecido. A garantia da `033` não foi desfeita.

---

## Cenário 2 — as duas frases, e o percurso que decide se há o que fechar (`SC-189`)

**Este cenário começa decidindo, e não conferindo** (`FR-542b`).

1. Crie um Edital **sem Perfil** e abra a validação como o gestor que a auditoria usou.

**Observe e registre**, porque disto depende metade da `US2`:

- a pendência **já diz** o que falta e **já leva** à etapa de Perfis? *(medido no código: sim)*
- o gestor **consegue** criar o Perfil ali, ou alguma permissão o impede?

**Se nada o impede**, o achado se fecha **registrando isso**, e a condução do `ACH-02` não é
escrita — escrever frase para problema que não existe é pior do que não escrever.

2. Abra a tela de um Edital **publicado** como gestor **sem** a permissão de retificar.

**Esperado**: junto de *"Conteúdo imutável"*, a tela nomeia a ação e a permissão — na formulação
**cheia**, *"peça a alguém com a permissão de X **que Y**"*.

3. Abra a mesma tela como alguém que **pode** retificar.

**Esperado**: a ação **Retificar aparece na lista** — ela já aparecia — e o aviso **cala**. Repetir
*"peça a alguém"* ao lado do botão que a pessoa pode clicar ensina a desconfiar da tela.

4. Conte as ações da lista nos dois casos.

**Esperado**: **nenhuma ação nova**, e Retificar **não** virou botão desabilitado. Navegação que o
ator não abre continua não sendo oferecida — e desfazer isso desfaria a regra da `007` e da `033`.

---

## Cenário 3 — o Edital que abre inscrições no dia em que é publicado (`SC-190`, `SC-191`)

1. Componha um Cronograma cujo período de inscrições **comece no passado e termine no futuro**.

2. Olhe o selo da etapa do Cronograma.

**Esperado**: **concluída**. Hoje ela fica pendente, e não há como concluí-la.

3. Peça a conferência de publicação.

**Esperado**: **nenhuma advertência** sobre esse Evento. As outras advertências do Cronograma não
mudam.

4. Publique e abra a página pública da seleção.

**Esperado**: o mesmo Evento aparece como **acontecendo agora** — e a gestão, que antes o chamava de
vencido, agora concorda com ela.

### As duas contraprovas da régua

5. Acrescente um Evento **pontual** cujo instante já passou — sem término declarado.

**Esperado**: ele **continua** vencido, e a frase nomeia o **início**. Se ele deixou de ser acusado,
a correção foi feita do jeito errado, e o `FR-546` é exatamente o que ela desrespeitou.

6. Acrescente um Evento com início **e** término passados.

**Esperado**: vencido, e a frase nomeia o **término**, como hoje.

---

## Cenário 4 — o peso, no momento em que a Etapa é enumerada (`SC-192`)

1. Declare uma Etapa classificatória **sem peso** e leia o rótulo do campo.

**Esperado**: ele **declara a condição** — o vazio é legítimo até que um marco enumere esta Etapa —
em vez de dizer "opcional" sem ressalva.

2. Vá ao marco e **enumere essa Etapa**.

**Esperado**: o cartão do marco **nomeia a Etapa** que falta pesar, **naquele momento**. Hoje isso só
aparece na conferência, nove etapas adiante.

3. Volte, declare o peso, e retorne ao marco.

**Esperado**: a cobrança **some**.

4. Deixe uma Etapa sem peso que **nenhum** marco enumera.

**Esperado**: **nada** a acusa. O vazio continua legítimo, e acusá-lo transformaria a correção em
defeito novo.

---

## Cenário 5 — o que **não** pode ter mudado (`SC-193`, `SC-194`)

1. Conte os controles do cartão do marco, antes e depois.

**Esperado**: **o mesmo número**. Nenhum controle novo entrou (`FR-551a`).

2. Confira que o peso continua sendo campo **da Etapa**, e que nenhuma migration existe.

3. Confira que a régua do vencido continua **advertindo e nunca recusando**, e que o impedimento por
período encerrado — que é outra regra — continua exatamente como estava.

**Esperado**: mesmas entradas, mesmos desfechos. **Zero** atos decididos de outro jeito.
