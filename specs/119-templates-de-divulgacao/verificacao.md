# Verificação: Templates de Divulgação por Família e Formato

## Templates aprovados (FR-3834, SC-1135)

A aprovação nomeia exatamente uma versão e um resumo. `tests/unit/kit/test_familias.py` confere que
cada linha desta tabela tem o resumo que o código fixa em `RESUMOS`; a liberação no ambiente
(`KIT_DE_DIVULGACAO_TEMPLATES`) nomeia a mesma versão e o mesmo resumo curto.

| Template | Versão | Resumo curto | Quem aprovou | Data |
|---|---|---|---|---|
| pos-lato-sensu/post · 1 | 1 | `bfcb25490b8e` | responsável pelo produto, por adoção (P-4) | 04/11/2026 |
| pos-lato-sensu/story · 2 | 2 | `8a16aef0abbd` | responsável pelo produto, pela decisão do resumo (FR-3836) | 04/11/2026 |
| pos-lato-sensu/banner · 1 | 1 | `1badbdf0cb93` | responsável pelo produto, por adoção (P-4) | 04/11/2026 |

**Por adoção, e não sobre a galeria.** A resposta à P-4, em 04/11/2026, foi "apenas adote o
template": a aprovação da comunicação sobre a galeria (SC-1135) foi dispensada pelo responsável
pelo produto, e a adoção dele é o registro. A galeria continua gerada por
`scripts/galeria_do_kit.py --familia pos-lato-sensu`, como prova visual de cada versão.

**A liberação em produção** continua da operação, pela configuração:

```text
KIT_DE_DIVULGACAO_TEMPLATES=pos-lato-sensu/post@1#bfcb25490b8e,pos-lato-sensu/story@2#8a16aef0abbd,pos-lato-sensu/banner@1#1badbdf0cb93
```

## O resumo por falta de espaço (FR-3836)

**Decidido em 04/11/2026** pelo responsável pelo produto, depois da revisão do incremento 2: a FR-3425
da `111` só previa o resumo acima de quatro opções, e os templates da Pós Lato Sensu — cuja foto ocupa
a metade de baixo — passavam ao total sem dizer. A FR-3836 formaliza a exceção, e a ordem é lista,
lista no corpo mínimo da oferta, recusa pela carga horária (EC-3), resumo.

**A versão 2 do story.** Listar no corpo mínimo antes de resumir mudou uma peça de referência: o
story do 91 sem localidade, de dois polos, que a versão 1 resumia, passou a listá-los. A versão
subiu, e não foi regravada na 1 (EC-22). A versão 1 nunca foi liberada fora do desenvolvimento.
Post e banner não mudaram de peça nem de resumo.

Medido depois da mudança, em 04/11/2026, com opções de 20 vagas e carga "360h"; "curto" é um nome
de 8 caracteres, e "longo", de 41 ("Especialização em Informática na Educação"):

| Formato | 1 opção | 2 curtas | 2 longas | 3 curtas | 3 longas | 4 |
|---|---|---|---|---|---|---|
| post | lista | lista | resumo | resumo | resumo | resumo |
| story | lista | lista | resumo | lista | resumo | resumo |

O banner não tem bloco de ofertas (EC-6). O caso real do 91 sem localidade, de dois polos com nomes
distintos, lista no story e resume no post.

## Cenários de referência 18 a 25 na Pós Lato Sensu (FR-3831)

| Cenário | Onde está coberto |
|---|---|
| 18. FIC com três Perfis de carga declarada | Da família FIC (incremento 3a, abaixo); na Pós, o caso de várias ofertas é o 91 de quatro polos |
| 19. Carga vazia num Perfil e longa noutro | Galeria (`c_carga`) e `test_peca_das_familias.py` |
| 20–22. Atendimento declarado, ausente e de 255 caracteres | Nenhum template da Pós tem caixa de contato (FR-3820): a peça não muda; o contato é dos textos, em `test_textos_com_carga_e_contato.py` |
| 23. Internos nas duas variantes | Da família Internos (incremento 3e, T051): os cenários comuns na variante `servidores` e o `23-estudantes` em `test_referencias.py`, e a chamada como única diferença em `test_familia_internos.py` |
| 24. Edital de unidade sem família | `test_familias_na_tela.py::test_unidade_sem_familia_so_tem_a_institucional` |
| 25. Caractere sem grafia só na fonte de título | `test_peca_das_familias.py::test_caractere_sem_glifo_so_na_fonte_de_titulo`; na galeria não cabe, porque as três Poppins têm o mesmo repertório |

## Cenários de referência na FIC (incremento 3a, T047)

Os da `111` e o 17 rodam na FIC como em toda família; os de baixo são só dela, em
`test_referencias.py::test_a_peca_dos_cenarios_da_familia_e_a_referencia`, e não entram na pasta da
Pós, cujo resumo não muda.

| Cenário | Post | Story | Banner |
|---|---|---|---|
| 18. Três Perfis de carga declarada | lista as três | lista as três | lista as três |
| 19. Carga vazia num Perfil e longa noutro | recusa nomeando a carga (EC-3) | recusa nomeando a carga | recusa nomeando a carga |
| 20. Atendimento declarado | "Dúvidas?" no lugar do contato dos slides | idem | sem caixa de contato, como o slide do site |
| 22. Atendimento de 255 caracteres | sai da peça, com o aviso (EC-4) | idem | sem caixa de contato |
| 91, quatro polos (e o prorrogado) | lista as quatro | lista as quatro | recusa: o painel não as comporta, e a FIC não está na FR-3836 |

O 21 (unidade sem atendimento) é o caso de todos os outros cenários, e `test_peca_da_fic.py` o
confere à parte. A prorrogação é a faixa vermelha do alto, e não item do painel.

## Validações que dependem do ambiente de implantação

Nenhuma delas se faz na máquina de desenvolvimento, e nenhuma está feita. **Em host local a peça não
é gerada** (EC-12, regra da `111`): sem endereço público não há link na peça, e a tela diz o motivo
no lugar das prévias. Por isso a prévia com imagem, o download do PNG e do SVG e o ZIP da família
foram provados pela suíte e pela galeria, **e nunca num navegador**. A adoção registrada acima
(P-4) aprova o desenho dos templates; ela não comprova a jornada de quem os usa.

### Roteiro de homologação

**Antes.** O ambiente com o código dos dois PRs, o `resvg-py` instalado, e:

```text
KIT_DE_DIVULGACAO_PECA=true
KIT_DE_DIVULGACAO_TEMPLATES=pos-lato-sensu/post@1#bfcb25490b8e,pos-lato-sensu/story@2#8a16aef0abbd,pos-lato-sensu/banner@1#1badbdf0cb93
```

Dois Editais publicados do Cefor: um de **um** polo e um de **quatro** (o resumo da FR-3836), e uma
pessoa com o papel de comunicação.

1. **Liberação (FR-3808, SC-1140).** Na tela do kit, a família "Pós Lato Sensu" aparece, e os três
   formatos sem "em aprovação". Uma entrada com resumo trocado deixa aquele formato com "versão nova
   em aprovação" — conferir uma vez e restaurar.
2. **Servidor (SC-1137, SC-1134).** No servidor, `scripts/medir_kit_de_divulgacao.py` com
   `--edital`, `--base-url` e `--lote 20`, nos dois Editais. Ele não grava nada e imprime a mediana
   e o máximo da tela e do ZIP, e se o PNG de cada formato saiu idêntico em duas gerações.
3. **Navegador (SC-1137).** Abrir a tela do kit 20 vezes, com o cache desligado, e anotar o tempo
   até a última prévia carregar (a aba de rede das ferramentas do navegador). Baixar o ZIP 20 vezes
   e anotar o tempo de cada um.
4. **Prévias e downloads (FR-3806, FR-3829, FR-3830).** Em cada Edital: trocar de imagem e conferir
   que as três prévias mudam só o fundo; baixar PNG e SVG de cada formato e abrir o SVG fora do
   GPS; baixar o ZIP e conferir que traz `peca-post.*`, `peca-story.*`, `peca-banner.*`, a ficha e
   o manifesto com a entrada de cada formato. No de quatro polos, a tela diz em quais formatos as
   opções saíram resumidas, e a legenda lista os quatro com a carga horária (FR-3836). Voltar para a
   Institucional pelo formulário funciona.
5. **Trilha (FR-3828).** Cada download aparece na trilha do Edital com família, imagem e template.
6. **Jornada (SC-1136, T056).** Uma pessoa da comunicação, sem ajuda, obtém post, story e banner de
   um dos Editais, cronometrada, sem abrir o PDF e sem digitar texto. Anotar o tempo e o que a fez
   parar.

| O quê | Requisito | Tarefa | Passo | Situação |
|---|---|---|---|---|
| A liberação nomeia versão e resumo, e o divergente não sai | FR-3808, SC-1140 | — | 1 | pendente |
| Tempo do servidor e PNG idêntico em duas gerações | SC-1134, SC-1137 | T044 | 2 | pendente |
| Tela com as três prévias em menos de 2 s e ZIP em menos de 3 s, num lote de 20 | SC-1137 | T044 | 3 | pendente |
| Prévias, downloads PNG, SVG e ZIP, e o aviso do resumo, pelo navegador | FR-3806, FR-3829, FR-3830, FR-3836 | T056 | 4, 5 | pendente |
| Jornada com uma pessoa da comunicação em menos de três minutos | SC-1136 | T056 | 6 | pendente |

**Referência da máquina de desenvolvimento**, em 04/11/2026, com outra suíte rodando no mesmo
cluster, num lote de 3 sobre o 91 de quatro polos: tela 0,94 s de mediana, ZIP 1,12 s, PNG idêntico
nos três formatos. Não substitui a medição no ambiente.

## Desempenho (SC-1137)

Pendente no ambiente de implantação (T044), pelo roteiro acima. Na máquina de desenvolvimento, a galeria da Pós Lato
Sensu compõe e rasteriza os 51 pares cenário × formato pelo fluxo real.
