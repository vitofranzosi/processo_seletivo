# Verificação: Centro de Controle do Edital (136)

## A conferência no navegador (09/11/2026)

Banco `ps136`, com os cenários C04, C06, C08, C12 e C14 da `134` carregados pelo comando de carga;
servidor pela entrada `centro-136` do `.claude/launch.json` (porta 8136). Dois papéis por cenário:

| Cenário | Papel | O que se viu |
|---|---|---|
| C06 | presidência (`treino.presidencia`) | "Há algo em aberto em avaliação e classificação. 2 ações são suas." Mapa com Avaliação e Classificação *Em curso*, cada uma com "1 sua". Destaque **Fixar os participantes**, "Por que esta: É a que destrava os próximos passos…", "Esperam por ela: Obter a semente pública → Realizar o sorteio". A Avaliação diz que é paralela ao sorteio. Classificação consultada por padrão, com o roteiro: "Obter a semente pública — Ainda não começou: nenhuma relação deste marco está congelada". Nenhuma mensagem no console. |
| C06 | avaliação (`treino.avaliacao1`) | "2 estão com outros papéis." "Nenhuma ação é sua agora." As duas ações nomeadas com "Quem conduz a seleção:". Sem tabela por lista, sem "Onde cada lista está", sem Encerrar e Cancelar. "Você acompanha este Edital sem ato a praticar nele." |
| C08 | presidência | "1 ação é sua e 2 aguardam prazo ou resposta (a primeira até 14/11)." Destaque **Classificar a lista** (PPP), "É a única ação sua disponível agora." Resultado e recursos *Em curso*, "Resultado publicado em 1 de 2 listas", "◷ até 14/11". **A providência não diz que a PPP não tem inscritos**: é a `135`. |
| C08 | Publicador (`treino.publicacao`, papel `publicador`) | "Você publica resultados." "Nenhuma ação é sua agora." Na espera, "Publicar o resultado definitivo" com "…ou publique como resultado preliminar" — o achado A-08 do estudo, que a `135` corrige. Detalhe da fase sem tabela, com a frase de quem vê o detalhe por lista. |
| C12 | presidência | Sem destaque: "Você tem 2 ações disponíveis agora. Todas já podem ser feitas… e o GPS não escolhe a ordem entre elas." Com `?fase=classificacao`, o cartão da Classificação ganha o contorno; a Convocação continua *Em curso*, "1 sua", "◷ até 09/12", sem contorno. Vagas *Em curso* com "nada a fazer agora". |
| C12 | Gestor (`treino.gestao`, papel `gestor`), a 375 px | Nenhuma rolagem horizontal (`scrollWidth` 375 = `clientWidth` 375). O mapa vira lista vertical. "Encerrar ou cancelar o Edital" recolhido no fim. |

## A suíte

`make lint check test-pg`, com os grupos `dev`, `navegador` e `assistente`, 4 workers.

**Primeira rodada (09/11, antes das correções abaixo): 3 falhas, 17 685 passando, 12 pulados.** As três
eram desta feature, e nenhuma do produto:

1. `test_folha_estatica.py::test_cada_folha_de_tela_e_carregada_so_por_quem_a_usa` — o registro
   `QUEM_CARREGA` não tinha a folha nova nem a página nova entre as que carregam `andamento.css` e
   `terminais.css`. O registro foi atualizado.
2. e 3. `test_auditoria_passagem_da_retificacao.py` — o censo das páginas que citam a Retificação
   (pendente e publicada) agora alcança o Centro, pelo link de ida do detalhe. É uma porta nova
   legítima (FR-4728, FR-4740), e o censo a inclui, com o motivo escrito no teste.

**Sobre "a suíte do detalhe passa sem alteração" (FR-4703, SC-1478).** Os testes do detalhe passam
sem alteração. Os dois do item 2 e 3 não são do detalhe: são o rastreador de navegação da `103`, que
percorre tudo o que a Lista alcança em dois cliques — e o Centro entrou no alcance.

A segunda rodada está registrada no fim deste arquivo.

## O que não foi verificado

- **A validação com operadores.** É do plano de produção do estudo, na homologação, e não desta spec.
- **O texto da lista vazia no C08.** Depende da `135`, que ainda não está na `main`.
- **Leitor de tela de verdade.** O `aria-current` e o texto oculto estão no HTML e nos testes; ninguém
  ouviu a página com um leitor.

## A segunda rodada (09/11/2026)

Depois das três correções acima, sobre a `main` em `0254fb91`: `make lint` limpo, `make check` sem
problema e sem migration, e **`make test-pg`: 17 688 passando, 12 pulados, nenhuma falha** (4 workers,
`worksteal`, 938 s), com os grupos `dev`, `navegador` e `assistente`. Os 12 pulados são os deliberados
do `CLAUDE.md` para quem tem os dois grupos opcionais. O total é o da primeira rodada (17 685 + as 3
que falhavam). Os casos desta feature são 133: 116 puros, 10 da página, 3 dos cenários (cada um com
os quatro papéis), 2 de orçamento e 2 de navegador — mais os guardiões que ela tocou.
