# Curadoria das Novidades do GPS

*Desde a [`168`](../specs/168-novidades-do-gps/spec.md), 14/11/2026.* Este guia é para quem escreve
as notas da página **Novidades do GPS**. O arquivo é
[`backend/processo_seletivo/novidades/novidades.toml`](../backend/processo_seletivo/novidades/novidades.toml),
e publicar uma nota é editar esse arquivo e abrir um PR.

## A regra que não se negocia

**Uma nota só entra depois de todos os PRs que ela cita estarem na `main`, e descreve só o que eles
entregaram.** A nota viaja com o código: o ambiente que roda um commit mostra as notas daquele
commit. Respeitada a regra, nenhum ambiente anuncia o que não roda — sem precisar saber quando cada
um foi implantado.

PR integrado não é capacidade entregue. Spec, plano, tarefas, estudo e auditoria não viram nota.
Spec entregue pela metade vira nota da metade que entrou: a `152` tem cinco de seis histórias, e a
nota fala das cinco.

## O caminho

1. **Rascunho.** De `backend/`, com o `gh` autenticado:

   ```bash
   uv run python scripts/rascunhar_novidades.py --saida /tmp/rascunho-das-novidades.md
   ```

   O roteiro lista os PRs mergeados depois do maior PR citado no arquivo, agrupados pela spec, marca
   os que só tocam documentação e escreve um esqueleto `[[nota]]` por grupo, com a data do último
   merge no horário de Brasília. Ele não escreve no arquivo das notas.
2. **Curadoria.** Para cada grupo, decida: vira nota, junta-se a outra, ou fica de fora. Escreva a
   nota no topo do arquivo — a ordem é da mais recente para a mais antiga.
3. **Validação.** `uv run pytest tests/novidades` confere a forma, as rotas, as âncoras, as
   configurações, as capacidades, as specs citadas, o vocabulário e que nenhum PR está em duas
   notas.
4. **Revisão no PR.** A pessoa que revisa lê a nota como quem opera, com a lista abaixo.

PR que ficou de fora de propósito não volta no rascunho seguinte só se o arquivo citar um PR maior
que ele. Para não perdê-lo de vista, anote-o na descrição do PR de curadoria.

## O que vira nota

| Vira | Não vira |
|---|---|
| Tela, ação ou informação nova que alguém da comissão, da unidade ou o candidato percebe | Refatoração, teste, CI, desempenho da suíte, folha de estilo sem efeito visível |
| Comportamento que mudou o que a pessoa faz ou lê | Spec, plano, tarefas, estudo, auditoria, documentação |
| Erro que a pessoa podia encontrar e deixou de acontecer | Correção de teste intermitente, de achado interno sem efeito na tela |
| Capacidade presa a configuração, com `requer_configuracao` | Detalhe de segurança que só interessa a quem ataca |

## Como agrupar

**Uma nota por capacidade, e não por PR.** O Centro de Controle são sete PRs e uma nota; o Kit de
divulgação, onze PRs e uma nota. Um PR nunca está em duas notas — a suíte recusa.

## Como escrever

- **Título**: o que a pessoa ganha, em até 90 caracteres. "Conferir documentos com o arquivo ao lado
  do formulário", e não "Visualizador lateral na conferência".
- **Resumo**: o que mudou, em duas a quatro frases, com os rótulos que aparecem na tela, entre aspas
  quando forem texto literal. Nada de número de PR, de spec, de requisito, nome de arquivo ou jargão
  de desenvolvimento.
- **Para que serve** (`beneficio`): uma frase, só quando o resumo não diz.
- **Onde** e **passos**: só quando a pessoa precisa ser guiada. No máximo quatro passos.
- **Destino**: uma seção da barra (`interface:agenda`). O link só aparece a quem alcança a seção.
- **Documentação**: a âncora da seção da Documentação do Sistema que descreve a capacidade. Prefira
  isso a explicar de novo.
- **Público**: `para_capacidade` quando a nota só interessa a quem tem a capacidade (administrar
  acessos, auditar).
- **Data**: o dia do último PR citado, no horário de Brasília.
- **Categoria**: *novidade* é o que não existia; *melhoria*, o que existia e ficou melhor;
  *correção*, o comportamento errado que deixou de acontecer.

## Lista da revisão

- [ ] Todos os PRs citados estão mergeados na `main`?
- [ ] A nota descreve só o que esses PRs entregaram, e não o que a spec promete?
- [ ] Os rótulos citados existem na tela, com essa grafia?
- [ ] Quem opera entende sem saber o que é um PR?
- [ ] A capacidade depende de configuração desligada em algum ambiente? Então `requer_configuracao`.
- [ ] A nota não expõe falha de segurança nem problema interno sem efeito para quem opera?
