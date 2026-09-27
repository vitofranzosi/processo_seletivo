# Percursos — a Retificação que acrescenta, pela tela

**Tudo pela interface.** Shell e banco preparam o ambiente e diagnosticam, mas **não atravessam passo
que deveria estar disponível à pessoa**. Não havendo caminho, registre a lacuna e siga (protocolo da
`034`). O Princípio VI é o critério: demonstrar por chamada de API o que a tela não oferece não conta.

## Ambiente

- Banco próprio da worktree (`DB_NAME`), `migrate`, a preparação dos papéis **duas vezes** — a saída
  deve dizer `34 de 34` — e `seed_demo`.
- `INTERFACE_SELETOR_IDENTIDADE=true` e `PORTAL_IDENTIDADE_DEMO=true`. Abra sempre por
  `http://localhost:<porta>`.
- As identidades são **Elaborador**, **Homologador** e **Publicador**, uma para cada ato; a segregação
  exige três pessoas distintas, na composição e na Retificação.
- **Crie um Processo novo pela tela** para os percursos 1 a 3. O Edital do `seed_demo` não tem o
  Perfil sem ampla.
- A Retificação publica com vigência imediata. Para ver a versão nova no portal, recarregue a página.

---

## 1 — O Perfil sem a ampla ganha a ampla (`SC-288`, `FR-777` a `FR-782`)

1. Como **Elaborador**, componha um Edital com um Perfil **P1** com duas Modalidades de cota — *PPI*
   e *PcD*, cada uma com a sua linha do quadro — e **nenhuma** ampla. Deixe o período de inscrições
   aberto. Submeta, homologue e publique. A Revisão avisa *ampla por declarar*, e a publicação aceita.
2. No portal, como candidato, abra a inscrição de **P1**. **Esperado**: o formulário exige escolher
   *PPI* ou *PcD*, e não há como se inscrever sem declarar cota. É o achado.
3. Como **Elaborador**, abra *Retificar*. Na seção *Perfis de Vaga*: **esperado**, a frase *"Modalidades
   de Concorrência ainda não são definidas por aqui"* não aparece mais.
4. *Acrescentar Modalidade*: Perfil **P1**, código `AC`, denominação *Ampla concorrência*, marque *"É a
   ampla concorrência deste Perfil"*, vagas em branco. Informe a justificativa e confira.
   **Esperado**: o resumo mostra o acréscimo da Modalidade e a declaração da ampla, com *antes* em
   branco.
5. Volte, preencha vagas **e** mantenha a ampla marcada, e confira. **Esperado**: recusa, dizendo que a
   ampla não tem linha própria (cenário 7 da US1). Limpe as vagas.
6. Confirme, submeta, homologue (**Homologador**) e publique (**Publicador**).
7. No portal, abra de novo a inscrição de **P1**. **Esperado**: *Ampla concorrência* está entre as
   opções, e a inscrição de um não-cotista é enviada.
8. Abra o documento da Retificação. **Esperado**: a Modalidade *AC* aparece no Perfil **P1**.

## 2 — A cota acrescentada com as suas vagas (`FR-779`, `FR-781`)

1. No mesmo Edital, retifique acrescentando a Modalidade `EP` (*Escola pública*) ao **P1**, com
   fundamento, versão e percentual, e **3** vagas. Confira. **Esperado**: o resumo mostra a Modalidade e
   a linha do quadro, *"3 vaga(s)"*.
2. Tente de novo com o código `PPI`. **Esperado**: recusa, dizendo que o Perfil já tem esse código.
3. Publique a versão com `EP`. Na classificação de **P1**, **esperado**: o recorte *EP* aparece sem
   ordem, e o da ampla e os das outras cotas continuam como estavam.
4. As inscrições enviadas no percurso 1 continuam com a Modalidade que declararam. Confira na Mesa.

## 3 — A tela do corte deixa de terminar num beco (`SC-291`, `FR-788` a `FR-790`)

1. Componha e publique um Edital com um marco **sem regra de corte** num Perfil com dois marcos, um
   deles cortando. É a forma que a `046` ainda admite.
2. Como quem classifica e pode retificar, abra a tela do corte do marco sem regra. **Esperado**: a
   recusa por falta de regra, com o caminho *"Retificar o Edital para declarar a regra de corte"*.
3. Siga o caminho. **Esperado**: o cartão daquele marco oferece a regra inteira — espécie do alvo,
   quantidade, excedente, desfecho do empate, Etapa governada e continuação —, cada campo com o rótulo
   do vazio.
4. Preencha só a quantidade e confira. **Esperado**: recusa, com as mensagens da publicação (regra pela
   metade).
5. Preencha a regra inteira, governando uma Etapa **ainda sem Resultado**, e publique. Volte à tela do
   corte. **Esperado**: ela não recusa mais por falta de regra.
6. A guarda da `D-002` — a Etapa governada que já tem Resultado — exige Resultado registrado pela Mesa,
   que não cabe num percurso curto. Ela é provada por teste de integração, e se o percurso for feito, o
   esperado é a frase do [contrato](contracts/a-retificacao-que-acrescenta.md), §2.

## 4 — O marco sem janela ganha o prazo de recurso (`FR-786`, `FR-787`)

1. Num Edital publicado cujo marco não prevê recurso, abra *Retificar*. **Esperado**: o marco oferece
   só o prazo, em dias corridos, e o vazio diz que o marco continua sem prever recurso. Não há pergunta
   *"admite recurso?"*.
2. Informe `3` e publique. **Esperado**: o resultado divulgado a seguir abre a interposição com prazo de
   3 dias corridos.

## 5 — O critério de desempate se corrige (`FR-792` a `FR-794`)

1. Num Edital publicado com um critério *maior pontuação na Etapa X*, retifique **removendo-o** e
   **acrescentando** *maior pontuação na Etapa Y*, com a mesma ordem.
2. **Esperado**: o resumo mostra a remoção e o acréscimo; a publicação aceita; na classificação, a
   ordem já emitida daquele marco aparece obsoleta e recomputável.
3. Tente acrescentar um critério com ordem igual à de outro que continua, e confira. **Esperado**:
   recusa já na conferência, antes de confirmar.

## 6 — O Perfil sem reversão (`FR-791`)

1. Num Edital publicado com quadro e sem reversão, abra *Retificar*. **Esperado**: o Perfil oferece a
   espécie da reversão, em *"Nenhum"*.
2. Escolha *no esgotamento* e publique. **Esperado**: a versão nova declara a reversão.

## 7 — Regressão: retificar um texto emite um texto (`SC-294`, `FR-785`)

1. Num Edital publicado com marcos sem janela e sem corte e Perfis sem reversão, retifique **só** a
   descrição do Edital.
2. **Esperado**: o resumo tem **uma** linha, e o ato publicado tem **uma** alteração.

---

## Verificação automatizada

```bash
cd backend && make lint check test-pg DB_NAME=test_retificacao_048
```
