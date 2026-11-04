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
| 18. FIC com três Perfis de carga declarada | Da família FIC (incremento 3a); na Pós, o caso de várias ofertas é o 91 de quatro polos |
| 19. Carga vazia num Perfil e longa noutro | Galeria (`c_carga`) e `test_peca_das_familias.py` |
| 20–22. Atendimento declarado, ausente e de 255 caracteres | Nenhum template da Pós tem caixa de contato (FR-3820): a peça não muda; o contato é dos textos, em `test_textos_com_carga_e_contato.py` |
| 23. Internos nas duas variantes | Da família Internos (incremento 3) |
| 24. Edital de unidade sem família | `test_familias_na_tela.py::test_unidade_sem_familia_so_tem_a_institucional` |
| 25. Caractere sem grafia só na fonte de título | `test_peca_das_familias.py::test_caractere_sem_glifo_so_na_fonte_de_titulo`; na galeria não cabe, porque as três Poppins têm o mesmo repertório |

## Validações que dependem do ambiente de implantação

Nenhuma delas se faz na máquina de desenvolvimento, e nenhuma está feita. **Em host local a peça não
é gerada** (EC-12, regra da `111`): sem endereço público não há link na peça, e a tela diz o motivo
no lugar das prévias. Por isso a prévia com imagem, o download do PNG e do SVG e o ZIP da família
foram provados pela suíte e pela galeria, **e nunca num navegador**. A adoção registrada acima
(P-4) aprova o desenho dos templates; ela não comprova a jornada de quem os usa.

| O quê | Requisito | Tarefa | Como | Situação |
|---|---|---|---|---|
| Prévias dos três formatos e downloads PNG, SVG e ZIP pelo navegador, num Edital publicado, com o endereço público | FR-3806, FR-3829, FR-3830 | T056 | Abrir o kit de um Edital publicado da Pós Lato Sensu, escolher imagem, baixar cada formato e o ZIP, e conferir que o ZIP traz os três formatos e o manifesto | pendente |
| Jornada com uma pessoa da comunicação: post, story e banner em menos de três minutos, sem abrir o PDF e sem digitar texto | SC-1136 | T056 | Cronometrar, registrar aqui nome do papel, Edital, tempo e o que travou | pendente |
| Tela com as três prévias em menos de 2 s e ZIP em menos de 3 s, num lote de 20 | SC-1137 | T044 | 20 gerações seguidas de cada, registrando mediana e máximo | pendente |
| O PNG da mesma ficha e escolha sai idêntico em duas gerações | SC-1134 | T044 | Comparar o SHA-256 de dois downloads seguidos de cada formato | pendente |
| A liberação nomeia versão e resumo, e template divergente não é gerado | FR-3808, SC-1140 | — | Conferir `KIT_DE_DIVULGACAO_TEMPLATES` do ambiente contra a tabela acima; a recusa do divergente é coberta pela suíte | pendente |

## Desempenho (SC-1137)

Pendente no ambiente de implantação (T044). Na máquina de desenvolvimento, a galeria da Pós Lato
Sensu compõe e rasteriza os 48 pares cenário × formato pelo fluxo real.
