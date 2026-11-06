# Estudo — o GPS orienta quem conduz a jornada do Edital?

Investigação técnico-funcional e de UX, 06/11/2026, sobre a `main` em `250efe97`. É **diagnóstico e
proposta**: nada do produto mudou, e nenhuma spec foi aberta. A decisão de abrir uma é do usuário.

| Artefato | Conteúdo |
|---|---|
| Este arquivo | Relatório executivo, as dez perguntas, os percursos no navegador, limitações |
| [mapa-da-jornada.md](mapa-da-jornada.md) | A jornada real lida no código: ato, pré-requisito, evidência, papel, tela, transição e exceções; com `arquivo:linha` |
| [matriz-de-lacunas.md](matriz-de-lacunas.md) | 8 pontos que já funcionam (P-) e 16 lacunas (J-), com captura, código, gravidade e causa |
| [alternativas-e-proposta.md](alternativas-e-proposta.md) | **v2**: alternativas, prioridades P0–P3, a proposta em dois níveis, as decisões D1–D8 com recomendação, e o escopo de duas specs |
| [contrato-de-derivacao.md](contrato-de-derivacao.md) | As sete situações (ausência de ato não é pendência) e como cada uma se deriva do que já existe, ato por ato |
| [validacao.md](validacao.md) | O roteiro das cinco tarefas, com critérios fixados antes |
| [generalidade-da-jornada.md](generalidade-da-jornada.md) | **Complemento exigido para a Spec B**: as formas de classificação que o GPS implementa, a matriz de compatibilidade por família, e os ajustes da v3 |
| [mapa-das-etapas.md](mapa-das-etapas.md) | O fluxo das Etapas de avaliação no código (distribuição, avaliação, consolidação, recurso) e como elas se ligam aos marcos |
| `capturas/` | 25 telas reais do banco de demonstração |
| `maquetes/` | As maquetes v2 (`N1`–`N5`, por papel), as de transição e condução (`M3`, `M3b`, `M4`) e, em `v1/`, as primeiras |
| `roteiro/` | `capturar.py`, `transicao.py`, `maquetes.py` (v1 e `M*`) e `maquetes_v2.py`, para refazer tudo |
| [Página de comparação](https://claude.ai/artifact/RkN4Hd6jyHN8Sm4ewsRwmo) | As telas de hoje e as maquetes lado a lado, para a discussão (privada; compartilhe pelo menu da página) |

---

## Relatório executivo

**Resposta curta: até a publicação, sim; depois dela, não.** O GPS orienta muito bem cada tela de
operação por dentro, mas não orienta a jornada entre elas.

**Antes da publicação, a orientação é boa.** A trilha de situação, "O próximo ato é seu", o botão
desabilitado com o motivo e a Validação que diz onde corrigir respondem às quatro perguntas
(`capturas/03`). A faixa "Ações disponíveis para você", da 104, faz o mesmo na entrada para quem
elabora, homologa, publica, julga ou avalia (`02`).

**Cada tela de operação também se explica bem.** Sorteio, corte, ocupação e convocação explicam o seu
recorte (`09`, `14`, `22`): dizem o que abrir não faz, distinguem "estado do percurso" de erro e
apontam o caminho nas recusas.

**Depois da publicação, a orientação acaba.** É aí que acontece quase todo o trabalho: congelar,
observar a semente, sortear, cortar, apurar, divulgar, convocar, conferir e decidir. As evidências
centrais:

1. **O cartão "O que fazer agora" é o mesmo em seis Editais em momentos diferentes** (`05`): um
   esperando a semente, um sorteado pela metade, um em avaliação, dois em convocação e um com
   Retificação à espera. O código explica: o bastão (`PROXIMO_RESPONSAVEL`) para em *Homologado*.
2. **O quadro da seleção está espalhado por marco e por recorte.** Para dizer o que falta no Edital 35
   são precisas 7 telas. A única tela que lista as pendências do Edital inteiro é a **confirmação de
   Encerrar** (`16`), um ato irreversível.
3. **O resumo do detalhe não vê o sorteio nem a convocação** (`06`): o 57, com relações congeladas à
   espera da semente, e o 91, sem relação nenhuma, leem igual.
4. **As transições confirmam, mas não conduzem.** Depois de emitir o corte, a tela diz "Corte emitido",
   e o botão de maior peso que aparece em seguida é outro "Emitir corte", o de sucessão (`13b`).
5. **A condução do marco termina na publicação.** Ela diz "nenhum recorte em falta" com uma convocação
   parada (`10`), e mostra "Falta" em todas as células de um Perfil que não teve inscrito (`11`).

**Onde está a dificuldade**: na arquitetura de informação e na comunicação de estado, e **não** nas
regras de negócio. O domínio já deriva quase tudo o que falta mostrar:

- `resumo_dos_marcos` e `sorteios_do_edital`;
- `recortes_do_marco` do sorteio e `leitura_do_recorte` da convocação;
- `pendencias_do_edital.situacoes` e `fatos_do_edital`.

O que falta é um lugar que leia isso junto.

> **v3, depois da segunda revisão de 06/11.** O [complemento de generalidade](generalidade-da-jornada.md)
> verificou a proposta contra todas as formas de classificação do GPS. O GPS combina Etapas de
> avaliação (pontuadas ou decisórias) com marcos que ordenam por pontuação ou por sorteio; isso dá sete
> famílias.
>
> As sete situações e o nível 1 são genéricos. O nível 2 da v2 não era: as colunas eram as do sorteio,
> e as Etapas de avaliação não apareciam em lugar nenhum. A v3:
>
> - compõe o nível 2 pela `jornada()` da `094`;
> - deriva a expectativa de cada Etapa pela ligação dela com os marcos. Uma Etapa que nada consome
>   aparece sem ser cobrada (D9), como as duas do 35 e a Entrevista do 91;
> - escalona os incrementos por nível, e não por família.
>
> A Spec A ganha a G-01: a ordem por pontuação pode ser emitida vazia, irreversível, antes de qualquer
> avaliação.
>
> **A Spec B não deve ser aprovada como estava, e sim com os cinco ajustes do complemento, §10.**

**Recomendação (v2, depois da revisão de 06/11): comunicar melhor o que o GPS já controla, em duas
specs pequenas, e não numa "da jornada completa".**

- **Spec A (P0)**: as correções que induzem a erro e não dependem de nada. É a sucessão em destaque
  logo depois do ato, *Falta* em lista sem inscrito, o erro cru da Caixa, "aguardando resposta" sem
  comunicação enviada e o aviso de congelamento fora do lugar.
- **Spec B, incremento 1 (P1)**: "O que fazer agora" passa a começar pelas providências em aberto do
  Edital, por papel: as da pessoa primeiro, depois as de outros papéis, depois as que esperam fato
  externo. As mensagens de sucesso dizem o próximo passo da lista.
- **Spec B, incremento 2 (P2)**: o "Andamento por Perfil", recolhido, no lugar do cartão
  "Classificação".

A derivação segue o [contrato](contrato-de-derivacao.md): sete situações, e ausência de ato nunca é
mostrada como pendência. Não há estado novo, nem percentual, nem "próximo passo" único.

Para quem conduz o 35, a página cai de 1767 para 1732 px, e as providências da pessoa terminam a 458 px
do topo (maquete `N1`). A condução estendida e a Lista ficam para o P3.

**Não recomendo uma barra com os seis momentos do material pedagógico.** Eles não são estado do
sistema: no 35, um Perfil está em convocação e o outro não tem momento nenhum.

**O que fica com o usuário**: as decisões D1 a D8, cada uma com opções e recomendação
(proposta §4), e a decisão de abrir as specs. Antes do plano da B1, o [roteiro de validação](validacao.md)
com as maquetes.

A v1 desta recomendação, um bloco "Andamento da seleção" com a matriz inteira acima da dobra, está em
`maquetes/v1/`. A revisão mostrou que ela acrescentava ~400 px e punha a matriz no lugar mais
importante da página.

---

## As dez perguntas

**1. O GPS apresenta hoje uma jornada operacional suficientemente compreensível?**
Não, depois da publicação. Até ela, sim. Cada tela de operação é compreensível sozinha; a sequência
entre elas, não.

**2. Quais evidências sustentam isso?**
`05` (o mesmo cartão em seis momentos), `06` (o resumo que não vê o sorteio), `13b` (a transição
muda), `10` e `11` (a condução que termina cedo e conta o vazio como falta) e `16` (a única lista do
que falta mora em Encerrar). No código: `acoes.py:407-411`; `conducao_do_marco.py:348`;
`corte.html:53`; mapa §8 e §9.

**3. O que já está bem resolvido?**
A pré-publicação, a faixa da 104, a condução do marco dentro do seu alcance, as telas de convocação e
de ocupação, as recusas que dizem o caminho e a confirmação de Encerrar (P-01 a P-08).

**4. Quais as lacunas mais relevantes?**
J-01 (nenhum bastão depois da publicação), J-03 (fragmentação), J-04 (o resumo cego ao sorteio e à
convocação), J-05 (a condução sem relação, semente e convocação) e J-08 (as transições mudas).

**5. Em que pontos o operador depende de conhecimento externo?**
- Saber que, depois das inscrições, vêm congelar, observar a semente e sortear, e em que ordem.
- Saber que a convocação não aparece na condução do marco.
- Saber que um Perfil sem inscrito não pede nada.
- Saber que "Falta a ordem" num marco de sorteio pode ser "espere a Caixa".
- Saber o que fazer depois de cada ato.
- Saber que a lista do que falta está em Encerrar.

**6. A principal dificuldade é de arquitetura de informação, navegação, comunicação de estado ou regra
de negócio?**
De arquitetura de informação e de comunicação de estado. A navegação existe (cada célula leva à sua
tela). Não é regra de negócio: os poucos defeitos funcionais vistos (J-06 em parte, J-14 a confirmar)
estão registrados à parte e não são o problema.

**7. Uma visão geral da jornada agregaria valor real?**
Sim, em dois níveis: primeiro as providências por papel, no cartão que já existe; depois o andamento
por Perfil, recolhido. Não, se for uma barra de fases ou uma matriz no lugar mais importante da
página. O ganho medido por inspeção é de 7 telas para 1 na pergunta "o que falta e quem faz", sem
deixar a página mais alta (v2). Só o teste com pessoas diz se a pessoa confia na resposta sem abrir as
telas.

**8. Como representar várias listas e operações paralelas?**
No nível 1, como providências independentes, cada uma com o seu lugar (Perfil, lista) e o seu
responsável. No nível 2, uma linha por Perfil com resumo em palavras e, aberta, uma linha por lista e
uma coluna por ato. O paralelo é coluna, e não fase. O Edital não tem "a etapa atual".

**9. Quais melhorias têm a melhor relação entre impacto e esforço?**
- Em primeiro lugar, as correções do P0. São pequenas, independentes e reduzem risco: a sucessão
  recolhida, o *Não se aplica*, a mensagem da Caixa, o rótulo da convocação e o aviso no lugar.
- Depois, as providências em "O que fazer agora" (P1), que reaproveitam a `104` e o
  `encerramento.da_confirmacao`.
- Por último, o andamento por Perfil (P2).

**10. Faz sentido criar uma spec? Qual o escopo mínimo?**
Sim, duas. A spec A, de correções (P0), é pequena e pode começar já. A spec B, de orientação do
andamento, tem dois incrementos (P1 e P2) e começa depois das decisões D1 a D8 e do roteiro de
validação com as maquetes. A condução estendida e a Lista ficam fora (P3). Os requisitos e os critérios
candidatos estão na proposta, §5.

---

## Percursos no navegador (Etapa C)

Feitos com o roteiro Playwright (`roteiro/`), papel a papel, a 1280 px. As dúvidas listadas são as
que um operador sem o rito de cor provavelmente teria: são inferência de inspeção, não observação de
pessoas.

| # | Cenário | Edital e papel | Caminho | O que se vê | Dúvida provável | Capturas · achados |
|---|---|---|---|---|---|---|
| 1 | Edital em elaboração | 90, quem elabora | Lista → faixa "Continuar a elaboração" → detalhe | Trilha, "O próximo ato é seu", Submeter desabilitado com "1 pendência impeditiva", Validação | "Qual das sete é a impeditiva?" | `02`, `03` · P-01, J-15 |
| 2 | Inscrições encerradas | 57, quem conduz | Lista (nada aguarda) → detalhe → Classificação → sorteio de cada marco | Design: relações congeladas, semente 6116 não observada. Tecnologias Digitais: relação não congelada. O detalhe diz zero para tudo | "Já posso congelar? O que estou esperando? Quando volto?" | `01`, `04b`, `06`, `07` · J-01, J-04, J-12, J-16 |
| 3 | Sorteio realizado | 26, quem conduz | detalhe → conduzir o marco → corte → ocupação | Ampla sorteada; PPP sem relação. Depois do corte, a mesma tela com "Emitir corte" de novo; depois da apuração, link para a convocação | "E agora? Por que a PPP está em falta?" | `09`, `13a`, `13b`, `14` · J-05, J-08, P-07 |
| 4 | Classificação parcial | 35, quem conduz | detalhe → os dois marcos → condução de cada um | Cefor tudo feito; Polo Vitória sem inscrito e com "Falta" em tudo | "O Polo Vitória está atrasado?" | `04`, `10`, `11`, `12` · J-03, J-05, J-06 |
| 5 | Convocação em andamento | 35, quem conduz e quem publica; 51 | convocação por recorte → Encerrar (só a confirmação) | 7 chamadas, 6 desfechos, 1 sem comunicação; o publicador lê "Nenhum ato disponível" | "Falta algo? É comigo?" | `16`, `17`, `22` · J-07, J-09 |
| 6a | Retificação depois de ato | 35 | sorteio | "Registros fora da operação atual" bem explicados; e o aviso "Não congele hoje" fora de contexto | "Preciso retificar?" | `08` · J-10 |
| 6b | Extração indisponível | 57 | Observar a ocorrência 6116 | A Caixa respondeu 500; mensagem com `**` literal e erro técnico | "Errei? Caiu? É cedo?" | `15` · J-12 |
| 6c | Lista sem disponível | 35 Polo Vitória | convocação | Duas orientações opostas | "Apuro ou peço a faixa seguinte?" | `12` · J-06 |
| 6d | Desistência, nova chamada | 35 ampla | convocação | Desistência registrada; "próxima da fila é suplente: chamar a vaga que vagou é a chamada individual" | (clara) | `22` · P-05 |
| — | Presidência de comissão | 91 | Lista → detalhe | "Avaliar (12 pendentes)" na Lista e nada no detalhe | "Onde estão as 12?" | `18` · J-09 |
| — | Visões de conjunto | gestor | Visão Geral, Agenda, Processo | Só inscrições; previsto sem realizado | "O evento de 03/11 aconteceu?" | `19`, `20`, `21` · J-13, J-14 |

---

## Limitações e o que não foi comprovado

- **Nenhum teste com pessoas.** Toda conclusão é de inspeção. A medida "7 telas para 1" é contagem de
  telas, e não tempo nem acerto de alguém.
- **Conferência documental na convocação (115/117) não exercitada no navegador.** Nenhum Edital do clone
  pede documento na convocação, e montar o cenário exigiria a infraestrutura de arquivos da suíte. O
  que se diz dela vem do código (mapa §6) e das revisões de 04/11 e 05/11
  ([jornada do convocado](../revisao-ux-jornada-do-convocado-2026-11-04),
  [experiência da convocação](../estudo-experiencia-da-convocacao-2026-11-05)).
- **Documento recusado e nova Retificação não foram praticados.** Desistência e nova chamada foram vistas
  só como registro e como opção.
- **A jornada por avaliação (91) foi vista só na Lista, em Minhas Etapas e no detalhe.** Distribuição,
  avaliação e consolidação não foram percorridas.
- **Uma chamada real à Caixa.** Observar a semente 6116 do 57 consultou a fonte declarada (Loteria
  Federal). A Caixa respondeu HTTP 500 e nada foi gravado. Não se repetiu.
- **O banco mudou durante o estudo.** O corte e a apuração da ampla do 26 foram praticados no clone
  para observar as transições, e as capturas `09`, `13a` e `13b` são de antes ou do instante do ato. Quem
  rodar `capturar.py` de novo verá o 26 depois desses atos.
- **As maquetes não foram conferidas a 375 px nem com leitor de tela.**
- **J-14** depende de como o 35 conduz as Etapas de análise documental e heteroidentificação, e precisa
  da equipe.

## Como reproduzir

- **Banco**: `ps_jornada` é clone de `processo_seletivo_guia`, a cópia pseudonimizada do Edital 35
  feita para o guia de 05/11: nomes `Pessoa C1…C11`, protocolos `INS-2026-FICTC0NN` e operadores por
  papel. Ele roda no container `postgres:18` da porta 55435 e foi migrado nesta base (só a
  `convocacao.0006` faltava).
- **Servidor**: `runserver 8140` com `DB_HOST=localhost DB_PORT=55435 DB_NAME=ps_jornada` e o seletor de
  identidade ligado. A entrada foi posta no `.claude/launch.json` local e não foi versionada.
- **Ordem dos roteiros**, do `backend/`, com `uv sync --extra dev --extra navegador`:
  1. `transicao.py`, para as três transições (grava no banco);
  2. `capturar.py`, que só lê;
  3. `maquetes.py`, que só lê e injeta o trecho proposto na página.
- **Por que não pelo painel do app**: ele não guarda a sessão de demonstração da gestão.
