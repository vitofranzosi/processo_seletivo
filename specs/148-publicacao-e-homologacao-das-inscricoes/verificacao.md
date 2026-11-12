# Verificação: publicação e homologação das inscrições

**Data**: 2026-11-11 · **Banco**: `ps_148_demo` (`make preparar` + `seed_demo` + o script de
demonstração descrito abaixo) · **Servidor**: entrada `inscricoes-148` do `.claude/launch.json`,
porta 8148 · **Navegador**: painel do aplicativo, 1280×900 e 375×812.

## Como o cenário foi montado

Dois Editais novos foram publicados no banco de demonstração **pelo mesmo caminho dos testes**
(`tests/fixtures/inscricoes_publicadas.py::montar`: canal administrativo, comissão, Mesa e
consolidação pelos comandos), porque o `seed_demo` não tem a forma da análise das inscrições — a
Análise documental dele é a terceira Etapa, com resultados incompletos:

| Edital | Forma | Inscrições |
|---|---|---|
| 7701/2026 | Análise documental decisória (Deferido/Indeferido) + Prova didática; Evento de recurso até 25/11 | Maria Silva (indeferida), João Souza, Carla Mendes, Diego Ramos (deferidos) |
| 7711/2026 | Só Etapas pontuadas — sem análise individual | Carla Mendes, Diego Ramos |

E três do `seed_demo`: 26/2026 (sorteio com relação de habilitados congelada), 51/2026 (dois
Perfis, duas listas, resultados divulgados) e 01/2026 (inscrições abertas).

**Dois atalhos de demonstração, e só dois**, ambos fora da jornada desta feature: o julgamento do
recurso de Maria foi gravado pelo shell com as funções das fixtures da `018` (admitir, decidir com
correção fixada, suceder o resultado) — o julgamento pela tela é da `018` e não mudou —, e o término
do prazo do preliminar foi antecipado no banco de demonstração para não esperar até 25/11, com o
gatilho desligado só pelo tempo da escrita (o padrão de `tests/integration/recursos/test_janela.py`).
Tudo o que é desta feature foi feito pela tela de quem o faz.

## Os sete cenários do pedido

| # | Cenário | Onde | O que se viu |
|---|---|---|---|
| 1 | Edital com sorteio e relação de habilitados | 26/2026 | A tela abre; a prévia da relação de recebidas lista as 7 inscrições do Perfil; a relação do sorteio continua a mesma (nenhuma leitura cruzada) |
| 2 | Análise de títulos/prova e homologação | 7701/2026 | A Etapa de análise é reconhecida sozinha ("Análise documental"); a Prova didática não entra no ato |
| 3 | Preliminar, indeferimento, recurso e homologação | 7701/2026 | capturas 01 a 11, abaixo |
| 4 | Edital sem homologação formal | 7711/2026 | O preliminar aparece indisponível — "O Edital não declara Etapa decisória de análise das inscrições." —; a homologação sem análise contempla as duas inscrições; publicá-la é opcional |
| 5 | Múltiplas vagas/listas | 51/2026 | O preliminar é recusado: "2 inscrição(ões) ainda sem conclusão consolidada na Etapa Análise documental"; a relação de recebidas agrupa por Perfil, uma linha por inscrição, sem repartir por lista |
| 6 | Edital anterior que não usa a feature | 51/2026 | Resultados divulgados e página da seleção respondem como antes; a seção "Inscrições" só aparece quando há ato |
| 7 | Publicação seguida de alteração | 7711/2026 | Publicada a homologação, uma inscrição enviada depois (Retificação que reabre o prazo, simulada no shell) faz a gestão dizer "O ato vigente difere da situação atual em 1 inscrição — 1 enviada depois dele"; o ato não muda, e a tela oferece a correção com motivo. No 7701, a correção do resultado de Maria por recurso fez a homologação contemplar as 4, e o preliminar continuou com 3 nomes |

E o período em curso (01/2026): "As inscrições ficam abertas até 01/12/2026 às 16:43. A relação das
inscrições só se publica depois que o período termina."

## A jornada do 7701, pelas telas

| Captura | Ator | O que mostra |
|---|---|---|
| [01](capturas/01-gestao-previa-recebidas.jpg) | Publicadora | Histórico vazio, os três atos com o que cada um é, a prévia da relação de recebidas (4) |
| [02](capturas/02-gestao-confirmacao-recebidas.jpg) | Publicadora | O que acontece ao confirmar; autoridade signatária |
| [03](capturas/03-gestao-recebidas-vigente-e-previa-do-preliminar.jpg) | Publicadora | Recebidas vigente; a tela sugere o preliminar: 3 deferidas, 1 indeferida |
| [04](capturas/04-gestao-preliminar-com-prazo-do-cronograma.jpg) | Publicadora | O período de recurso escolhido no Cronograma; o aviso de sucessão |
| [05](capturas/05-gestao-homologacao-espera-o-prazo.jpg) | Publicadora | A homologação espera o prazo, com a data; sem botão |
| [06](capturas/06-portal-preliminar-publico.jpg) | Público | Deferidos nominados em ordem; a indeferida só contada; prazo aberto |
| [07](capturas/07-portal-preliminar-375px.jpg) | Público | 375 px, `scrollWidth` = 375 |
| [08](capturas/08-candidata-nao-aceita-com-parecer-e-recurso.jpg) | Maria | "Inscrição não aceita (resultado preliminar)", o parecer, recorrer até 25/11 |
| — | Maria | Recurso interposto pelo formulário da `018`; a peça grava a janela do preliminar (11/11 16h46 a 25/11 23h59) |
| — | Publicadora | A homologação nomeia "Há 1 recurso(s) sem decisão…" e o prazo |
| [09](capturas/09-gestao-homologacao-apos-correcao.jpg) | Publicadora | Depois da correção e do prazo: 4 homologadas, 0 não homologadas |
| [10](capturas/10-gestao-cadeia-completa.jpg) | Publicadora | A cadeia: homologação vigente, preliminar e recebidas sucedidos |
| [11](capturas/11-candidata-aceita.jpg) | Maria | "Inscrição aceita"; "Isso ainda não é a classificação"; o resultado corrigido e o recurso julgado |

O console do navegador não registrou violação de CSP nem erro em nenhuma das telas.

## Achados da validação

| Achado | Tratamento |
|---|---|
| Perfil sem inscrição desaparecia do ato (51/2026, Técnico de Laboratório) | **Corrigido**: o ato lista todo Perfil da versão, com "Nenhuma inscrição … neste Perfil" (FR-5419) |
| O impedimento, em `<li class="erro">`, desenhava a barra do alerta dentro do marcador | **Corrigido**: um parágrafo de erro por impedimento |
| "Minhas inscrições" continua dizendo "Inscrição enviada" depois do ato | Registrado como trabalho futuro: a situação mora no acompanhamento, a um clique |
| O cartão "Resultado das etapas" diz "Eliminada" para a análise, enquanto o topo diz "não aceita" | Registrado como trabalho futuro: o vocabulário do cartão é o da `063` para toda Etapa |

## Revisão de 12/11/2026 — a relação por lista (D-011)

O cenário foi montado pelo caminho normal, pelas fixtures da 148 com `com_cotas=True`, e servido por
um `live_server` temporário. O Edital tem um Perfil com PcD, PPI e a Modalidade apontada como a
ampla. São seis inscrições: 702 e 704 declararam PPI, 703 declarou PcD, 705 declarou a apontada, e
701 e 706 não declararam nenhuma. A 704 foi indeferida na análise. As telas foram percorridas com o
publicador do seletor de demonstração.

| Captura | O que se vê |
|---|---|
| [12](capturas/12-portal-preliminar-por-lista-375px.jpg) | Portal, preliminar a 375 px: "Ampla concorrência (5)", "Pessoas com deficiência (1)" e "Pretos, pardos e indígenas (1)". A indeferida é contada na ampla e na PPI, e não é nomeada. A 705 está só na ampla. Não há rolagem horizontal (largura do documento 375 = viewport). |
| [13](capturas/13-gestao-previa-da-homologacao-por-lista.jpg) | Gestão, prévia da homologação: contagem por Perfil e lista, conferência dos nomes por lista e "6 inscrições contempladas… O total conta cada inscrição uma vez." |
| [14](capturas/14-documento-preliminar-por-lista.jpg) | O PDF do preliminar: um título por lista com a quantidade, e a frase das listas junto da explicação do ato. |

O console não registrou erro nem violação de CSP. O ato no formato anterior à revisão está coberto
por `test_o_ato_no_formato_anterior_a_revisao_continua_como_foi_publicado`: mesmos bytes, mesmo
resumo, página sem título de lista e PDF servido dos bytes gravados.
