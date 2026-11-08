# Validação da POC

08/11/2026 · base `da566ff2`. Registro consolidado da conferência técnica e visual.

## Coerência do domínio

`backend/.venv/bin/python doc/gps-por-dentro/conferir_cenarios.py --conferir` compara os estados
embutidos no HTML com `cenarios.json` e com a execução das funções oficiais. Sem banco e sem atos.

Verifica: mínimo 60 inclusivo; eliminação em 55; ausência não vira zero; desempate por nascimento;
ordem inicial e corrigida; cortes por lista e união de cinco; média final de cada participante;
concomitância estática; ocupação antes, após desistência e após aceite; empate excedente e recusa do
estrito; sorteio oficial sobre entradas fictícias determinísticas.

Resultados esperados fixados no [roteiro](roteiro-pedagogico.md). Publicação, recursos, documentação
e pré-condições da convocação foram confrontados com os comandos e testes existentes, sem emitir
atos reais. A POC não executou integração com correio, Caixa, armazenamento ou Registro Acadêmico.

## Critérios de compreensão a verificar com pessoas

| Pergunta operacional | Evidência que a interface oferece | Resposta esperada |
|---|---|---|
| Qual a diferença entre marco e corte? | Cenas 3 e 5 com botões e efeitos separados | Marco produz ordem; corte seleciona faixa dessa ordem por regra e lista |
| Classificar e apurar são a mesma operação? | Carla 1ª em duas listas; janela reservada a exclui e alcança Ana | Não: a apuração lê quadro, faixas, habilitações e efeitos |
| Por que classificado pode não estar convocado? | Cena 7 apura vagas sem chamadas; cena 8 cria atos próprios | Posição, faixa, ocupação e chamada não são sinônimos |
| O que fazem preliminar, recurso e definitiva? | Cena 4 preserva A, corrige nota e produz B, com prazo e providências | Recurso pode exigir sucessão; definitiva depende de impedimentos resolvidos |
| Quem avançou e por quê? | Duas listas e união de cinco na cena 5 | Elisa pela PcD; Ana/Carla nas duas; Bruno/Davi na ampla |
| Onde o conceito afeta a operação? | Bloco “Onde encontro no GPS”, fontes e captura real | Distinguir configuração na Composição de ato em Corte/Ocupação/Convocação |
| Por que uma ação seria inadequada? | Desafios de suplente sem aceite e arquivo sem conferência | Não promover por chamada; não aceitar só porque recebeu arquivo |

Não houve teste com operadores; a tabela é roteiro e cobertura implementada, não prova de aprendizagem.

## Inspeção no navegador

Chrome nativo, operado por controles de interface e teclado. Prévia local em loopback e abertura
posterior por `file:///…/index.html#duvidas`, comprovando que executar não depende do servidor.

| Percurso exercitado | Resultado observado |
|---|---|
| Início → história → revelar participação | Oito inscrições; Ana, Carla e Elisa nas duas listas |
| Consolidação da prova | Fábio 60 habilitado; Gabi 55 eliminada |
| Classificar → abrir a linha de Davi | Ordem 90,85,80,80…; explicação de nascimento 1988 antes de 1990 |
| Recurso → sucessoras → divulgação e prazo | Ordem A obsoleta e preservada; Carla 4ª → 2ª; definitiva descrita após providências e prazo |
| Aplicar os cortes | AC com quatro; PcD com três; Elisa alcançada na PcD; união de cinco |
| Fórmula: Carla → Davi, pelo seletor e teclado | 89,00 → 85,00, com parcelas visíveis; botão produz ordem final correta |
| Apuração em 375 × 812 | Carla desconsiderada na reservada; Ana titular; três lugares com nomes; aviso de nenhuma convocação ainda |
| Convocação → comunicação | Chamadas registradas antes da comunicação; envio não interpretado como leitura |
| Documento v1 → pendência → v2 → abertura → conforme → aceite | Cada estado surgiu separadamente, sem perder o contexto da chamada; limite da matrícula externa explícito |
| Desistência → chamada de Davi → aceite | Ocupação AC 2 → 1 → 1 → 2; chamada não promove automaticamente |
| Desafio documental: alternativa inadequada → correta | Feedback explica o erro; mudar a opção funciona sem penalidade |
| Abrir o HTML por arquivo e buscar “apuração” | Resultado “Apuração de ocupação” em primeiro; link correto ao laboratório; quatro conceitos relacionados |
| Mapa no arquivo local | Seis grupos, 17 links de conceitos e conexões entre marco, corte, apuração e convocação presentes |

Teclado exercitado com Tab, Enter e setas no seletor de candidato; após uma transição, o foco segue
para a próxima ação, ou para Reiniciar no estado final. Botões e expansões são nativos. Há foco
visível, nome acessível no reinício, área de anúncio e suporte CSS a `prefers-reduced-motion`.
A regra de redução foi inspecionada no código; não foi feita auditoria com leitor de tela nem
certificação WCAG. O link de pular conteúdo recebeu prevenção de navegação pelo roteador.

Desktop inspecionado na janela de 1512 px e na área de 957 px com DevTools aberto; celular em 375 px.
As capturas completas não mostraram texto cortado nos corpos de conteúdo. A navegação das cenas é
uma região horizontal própria no celular; o item ativo agora é trazido para dentro dela. Não foi
medida responsividade em todos os dispositivos ou navegadores.

### Capturas reais da POC

Geradas pela função “Capture full size screenshot” do Chrome e salvas nesta pasta:

- [Marco no desktop](capturas/02-marco-desktop.png): 1914 × 3688 pixels (área de 957 CSS px, escala 2).
- [Corte no desktop](capturas/03-corte-desktop.png): 1914 × 3854 pixels, com as duas listas e a união.
- [Apuração no celular](capturas/04-apuracao-375.png): 750 × 4864 pixels (375 CSS px, escala 2).

As três imagens de referência **do GPS** embutidas no aplicativo são outras: Composição,
Ocupação de vagas e Portal/Convocação. Suas legendas indicam origem e diferença do cenário.
O diálogo de referência, sorteio e empate alternativo foram conferidos nas composições programáticas;
não se registrou percurso manual completo desses três controles. O controle de navegador ficou
intermitente ao final; não se tratou o resultado programático como teste manual.

### Contraste e ajustes

Contrastes calculados pela luminância relativa sRGB: tinta/fundo 10,80:1; texto secundário/branco
6,14:1; texto laranja/fundo pêssego 5,06:1; texto claro/botão escuro 11,69:1. Bordas de campos e
alternativas ajustadas para 3,85:1 contra o fundo claro. Isso cobre os pares principais, não substitui
uma auditoria de acessibilidade de todos os estados.

Corrigidos durante QA: erro inicial de sintaxe na fórmula; representação de posição ainda não
emitida (“—”, sem ordinal/NaN); suplentes iguais nas duas listas do mesmo marco; rótulo da vaga
já apurada após desistência (“Vaga faltante”); salto de conteúdo sem trocar de rota; visibilidade da
cena ativa na faixa horizontal; contraste das entradas e tamanho dos rótulos numéricos móveis.
As últimas alterações de rótulo, salto, borda e faixa ativa passaram pela conferência programática;
não se refez toda a sequência manual depois delas.

## Verificações executáveis

| Verificação | Resultado |
|---|---|
| `make -s lint check` em `backend/` | Ruff check e format aprovados; Django sem issues; nenhuma migration pendente de criação |
| Ruff check e format dos dois auxiliares Python da POC | Aprovados |
| `conferir_cenarios.py --conferir` | Aprovado; HTML = JSON de estados = funções oficiais |
| `node doc/gps-por-dentro/verificar_interface.cjs` | 33 estados, 17 conceitos, 14 feedbacks (correto/incorreto), busca e ausência de dependências externas aprovados |
| Suíte inteira PostgreSQL, 4 workers, banco próprio `ps_guia_20261108` | **17340 passaram, 12 pulados, 1 falhou**, em 1429,51 s. A falha era exclusivamente a referência da nova spec na tabela do README |
| Após corrigir README: arquivos de README e citações, PostgreSQL serial | **8 passaram**, em 2,04 s. Não se repetiu a suíte inteira: a correção mudou somente a tabela documental |
| `git diff --check` | Aprovado |

Logs brutos: [suíte completa](verificacao-postgresql.txt) e
[reexecução documental](verificacao-documentacao.txt). Não se afirma que uma segunda execução da
suíte completa foi verde: a execução completa teve a falha indicada, e os arquivos afetados foram
reexecutados com sucesso depois da correção. Nenhum teste comportamental do GPS falhou.

## Limites da evidência

Não há observação com operadores, leitor de tela, teste de upload real ou matrícula externa. As
sete perguntas de compreensão acima continuam sendo o roteiro de teste humano. Não se executaram
publicações, convocações, mensagens ou chamadas à Caixa no sistema real. A única execução contra
PostgreSQL foi a suíte em bancos de teste isolados.
