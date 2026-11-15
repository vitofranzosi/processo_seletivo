# Curadoria das Novidades do GPS

*Desde a [`168`](../specs/168-novidades-do-gps/spec.md), 14/11/2026.* Este guia é para quem escreve
as notas da página **Novidades do GPS**. O arquivo é
[`backend/processo_seletivo/novidades/novidades.toml`](../backend/processo_seletivo/novidades/novidades.toml),
e publicar uma nota é editar esse arquivo e abrir um PR.

## As duas regras que não se negociam

**Uma nota só entra depois de todos os PRs que ela cita estarem na `main`, e descreve só o que eles
entregaram.** A nota viaja com o código: o ambiente que roda um commit mostra as notas daquele
commit. Respeitada a regra, nenhum ambiente anuncia o que não roda — sem precisar saber quando cada
um foi implantado.

PR integrado não é capacidade entregue. Spec, plano, tarefas, estudo e auditoria não viram nota.
Spec entregue pela metade vira nota da metade que entrou: a `152` tem cinco de seis histórias, e a
nota fala das cinco.

**Todo PR mergeado desde o início da janela tem um destino, e um só.** Ele é citado por uma nota de
`novidades.toml`, ou está em `[[sem_nota]]` de
[`curadoria.toml`](../backend/processo_seletivo/novidades/curadoria.toml) com o motivo, ou é só de
documentação. Documentação desatualizada não é motivo para deixar uma capacidade de fora: confira no
código e na tela, e escreva a nota. A suíte recusa PR com dois destinos.

## O caminho

1. **Rascunho.** De `backend/`, com o `gh` autenticado:

   ```bash
   uv run python scripts/rascunhar_novidades.py --saida /tmp/rascunho-das-novidades.md
   ```

   O roteiro lê todo PR mergeado desde o `inicio` do registro — **pela data do merge, e não pelo
   número**: o número diz quando o PR foi aberto, e um PR antigo entra muitas vezes depois de um
   novo — e lista como pendente o que não tem destino, agrupado pela spec, com um esqueleto
   `[[nota]]` por grupo e a data do último merge no horário de Brasília. Os só de documentação ele
   conta à parte. Ele não escreve em arquivo nenhum do repositório.
2. **Curadoria.** Para cada grupo, decida: vira nota, junta-se a uma que já existe (acrescente o PR
   e atualize a data), ou fica de fora — e então vai para `[[sem_nota]]` do registro, com o motivo.
   A ordem do arquivo é da mais recente para a mais antiga. Rode o roteiro de novo: o rascunho deve
   dizer "Nada pendente".
3. **Validação.** `uv run pytest tests/novidades` confere a forma, as rotas, as âncoras, as
   configurações, as capacidades, as specs citadas, o vocabulário e que nenhum PR está em duas
   notas.
4. **Revisão no PR.** A pessoa que revisa lê a nota como quem opera, com a lista abaixo.

O registro é o que torna a curadoria verificável: quem revisa o PR vê, no diff, o que virou nota e o
que ficou de fora e por quê.

## O que vira nota

| Vira | Não vira |
|---|---|
| Tela, ação ou informação nova que alguém da comissão, da unidade ou o candidato percebe | Refatoração, teste, CI, desempenho da suíte, folha de estilo sem efeito visível |
| Comportamento que mudou o que a pessoa faz ou lê | Spec, plano, tarefas, estudo, auditoria, documentação |
| Erro que a pessoa podia encontrar e deixou de acontecer | Correção de teste intermitente, de achado interno sem efeito na tela |
| Capacidade presa a configuração, com `requer_configuracao` | Detalhe de segurança que só interessa a quem ataca |

## A diretriz: a nota é um anúncio, não um relatório

*Decisão do usuário em 14/11/2026, depois de ler a primeira versão do conteúdo: "tem que ser algo
simples, interessante e que mostre o valor daquela novidade — quase propaganda —, com exemplos".*

Quem lê é alguém da comissão, da presidência ou da unidade, entre uma tarefa e outra. A pessoa não
sabe — nem precisa saber — como o sistema funciona por dentro. Ela quer saber três coisas: **o que
ficou mais fácil, por que isso importa para ela e como é na prática.** A nota que obriga a pensar
para entender falhou, por mais correta que seja.

### As cinco regras

1. **O título é a promessa, e fala do ganho.** Comece por um verbo ou pelo resultado, do ponto de
   vista de quem usa. Até 70 caracteres.
   - Não: "Centro de Controle: a página do Edital publicado".
   - Sim: "Veja em segundos o que falta em cada Edital".
2. **O resumo diz o que muda na vida da pessoa, em duas frases curtas.** Use "você". A primeira frase
   diz o que agora é possível; a segunda, por que isso importa — o tempo que se ganha, o erro que se
   evita, a dúvida que acaba. Até 300 caracteres.
3. **Sempre que puder, um exemplo** (`exemplo`, que a página mostra como "Na prática"). Uma cena
   curta e concreta, com Edital, pessoa ou número: "Na segunda de manhã, você abre o Edital 12/2026 e
   vê: *Convocar os titulares — é com você*. Um clique e você está na tela certa." O exemplo é o que
   transforma a nota em algo que se entende de primeira. Até 300 caracteres.
4. **Palavras de quem opera, nunca do sistema.** Fale de Edital, inscrição, candidato, comissão,
   convocação, documento, lista, vaga, prazo, resultado. Não use "marco", "recorte", "derivação",
   "apuração", "predicado", "estado", "ato", "comando", "persistir", "renderizar" nem siglas
   internas — se a tela usa o termo, explique-o com palavras comuns na primeira vez. Nada de número de
   PR, spec, requisito ou arquivo.
5. **Uma ideia por nota, e o peso certo.** O valor vem antes do funcionamento: diga o que ficou
   possível, e só depois a regra. O ajuste pequeno é uma nota *incremental*, de uma linha — nunca um
   pacote de assuntos. Correção se anuncia pelo alívio: "Resolvido: …".

### Antes e depois

> **Antes** — *Centro de Controle: a página do Edital publicado.* A página de um Edital publicado ou
> encerrado passou a ser o Centro de Controle: em que fase o Edital está, as providências em aberto e
> de quem é cada uma (com a marca SUA no que é seu), e o andamento da seleção.
>
> **Depois** — *Veja em segundos o que falta em cada Edital.* A página do Edital publicado agora
> mostra em que fase ele está, o que ainda precisa ser feito e quem faz cada coisa — o que é seu vem
> marcado. Acabou a caça por menus para descobrir o próximo passo.
> **Na prática:** você abre o Edital 12/2026 e lê "Convocar os titulares — SUA". Um clique, e você
> está na tela da convocação; feito o ato, o sistema volta ao Edital.

### Os campos

- **Título** (`titulo`) e **resumo** (`resumo`): as regras 1 e 2.
- **Na prática** (`exemplo`): a regra 3. Exemplo inventado, mas plausível; nunca com nome ou dado de
  pessoa real.
- **Para que serve** (`beneficio`): raramente necessário — o resumo já diz. Use só quando o ganho
  merece uma frase à parte.
- **Onde** e **passos**: só quando a pessoa precisa ser guiada. No máximo quatro passos curtos.
- **Destino**: uma seção da barra (`interface:agenda`). O link só aparece a quem alcança a seção.
- **Documentação**: a âncora da seção da Documentação do Sistema, para quem quiser o detalhe. O
  detalhe mora lá, e não na nota.
- **Público**: `para_capacidade` quando a nota só interessa a quem tem a capacidade.
- **Data**: o dia do último PR citado, no horário de Brasília.
- **Categoria**: *novidade* é o que não existia; *melhoria*, o que existia e ficou melhor;
  *correção*, o problema que deixou de acontecer.

### Duas camadas: a vitrine e o histórico

*Revisão de 14/11 (`D-012` da 168).* O PR não é a unidade de comunicação: dez, vinte PRs podem ser uma
capacidade só. A página tem duas camadas:

- **A vitrine, "Descubra o que o GPS já faz"** — as capacidades do produto, em `[[capacidade]]` no fim
  de `novidades.toml`. Cada uma reúne as notas que a construíram e é escrita em três tempos: **o que
  agora é possível**, **por que isso facilita** e **por onde começar**. Título até 70 caracteres,
  resumo até 240, até três passos. Não tem data: o cartão diz quantas atualizações a construíram.
- **O histórico** — cada nota, com a **relevância** (`relevancia`), que é independente da categoria:
  - *transformadora*: cria capacidade ou elimina operação trabalhosa — cartão com filete;
  - *relevante*: melhora uma jornada que já existia — cartão normal;
  - *incremental*: ajuste, legibilidade, correção pontual — uma linha enxuta, sem "Na prática".

  Meça pelo benefício para quem opera, nunca pelo número de PRs nem pela dificuldade técnica.

### Os destaques

- **No máximo dez capacidades, seis à vista.** A vitrine que vira lista deixa de destacar.
- **Entra** a capacidade que cria uma possibilidade nova ou elimina uma operação trabalhosa — e só
  quando o que ela promete está disponível. Em desenvolvimento, só no desenvolvimento local ou atrás
  de chave desligada: não entra.
- **Sai**, quando passar de dez, a de menor uso na rotina da comissão; a decisão vai na descrição do
  PR.
- **Destaque não é novidade recente.** A capacidade de setembro fica enquanto for das mais
  importantes.
- **A nova nota de uma capacidade que já existe** entra em `notas` dela: a página diz "faz parte de", e
  a capacidade não se repete como novidade.
- A matriz que fundamentou a vitrine está em `specs/168-novidades-do-gps/capacidades.md`.

### Como agrupar

**Uma nota por mudança que alguém perceberia, e não por PR.** O Centro de Controle são sete PRs e uma
nota. **Não junte assuntos distintos numa nota só** — "Pequenas melhorias no Edital, nos e-mails e nas
páginas" esconde o que cada um vale: cada assunto é uma nota, e a incremental, uma linha enxuta, não
pesa no histórico. Um PR nunca está em duas notas — a suíte recusa.

## Lista da revisão

- [ ] O rascunho, rodado de novo, diz "Nada pendente"?
- [ ] Cada PR em `[[sem_nota]]` tem um motivo que convence quem opera?
- [ ] Todos os PRs citados estão mergeados na `main`?
- [ ] A nota descreve só o que esses PRs entregaram, e não o que a spec promete?
- [ ] Os rótulos citados existem na tela, com essa grafia?
- [ ] Lida em voz alta para alguém da comissão, a nota se entende de primeira?
- [ ] O título promete um ganho, e o exemplo mostra esse ganho numa cena concreta?
- [ ] Nenhuma palavra do sistema ("marco", "recorte", "derivação", "ato", "estado")?
- [ ] A relevância está pelo benefício? A nota de uma capacidade que já existe entrou em `notas` dela?
- [ ] Um servidor que não acompanhou o desenvolvimento entende, em 15 segundos, o benefício?
- [ ] A capacidade depende de configuração desligada em algum ambiente? Então `requer_configuracao`.
- [ ] A nota não expõe falha de segurança nem problema interno sem efeito para quem opera?
