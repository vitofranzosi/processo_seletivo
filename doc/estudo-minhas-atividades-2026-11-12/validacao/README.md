# Validação: as providências de cada pessoa, nos cenários de treinamento

**O que se mediu.** O que cada identidade veria numa visão pessoal **se ela lesse a derivação que já
existe**. A leitura roda `andamento.do_edital` (127) em cada Edital e separa os itens do nível 1 pela
regra de "sua" (`e_sua`). Ao lado, para comparar, roda a faixa da `104` (`trabalho.do_ator`). Nada
novo foi escrito no código de produção, e nada foi gravado.

**Sobre quê.** Os quinze cenários de treinamento (134), rodada 1, num banco próprio
(`ps_minhas_atividades`) sobre a `main` em `4194e035`. Os cenários dão de graça o caso "uma pessoa em
várias comissões". `treino.presidencia` preside onze comissões. `treino.avaliacao1` e
`treino.avaliacao2` são membros das mesmas onze e estão alocados a 27 Etapas cada um. Nenhum cenário
usa a alocação à conferência (115) nem a designação para a formalização (117).

## Como reproduzir

Os três primeiros comandos são os de `doc/estudo-centro-de-controle-2026-11-09/04-prototipos.md`. O
gerador precisa, além disso, de `ARQUIVOS_CANDIDATOS_RAIZ`: sem ela, só o C01 é criado e os demais
falham com `ImproperlyConfigured`.

```bash
cd backend && export LC_ALL=pt_BR.UTF-8 DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps_minhas_atividades DB_USER=$USER DB_RUNTIME_USER=$USER ARQUIVOS_CANDIDATOS_RAIZ=/um/diretorio/fora/do/repo
```

```bash
CENARIOS_DE_TREINAMENTO=true uv run python manage.py carregar_cenarios_de_treinamento --banco ps_minhas_atividades --autoridade <pk>
```

```bash
uv run python manage.py shell < ../doc/estudo-minhas-atividades-2026-11-12/validacao/agenda_por_pessoa.py
```

A saída integral está em [`agenda.txt`](agenda.txt).

## Resultado

| Identidade | Base | Suas | De outro papel | Em espera | Faixa da 104 hoje | Consultas (15 Editais) |
|---|---|---|---|---|---|---|
| `treino.presidencia` | presidência de 11 Processos | **20 atos em 11 Editais** | 3 | 10 | **0** | 1157 (1,3 s) |
| `treino.avaliacao1` | membro + alocação | 1 (Avaliar 5, SIM05) | 22 | 10 | 1 (o mesmo) | 1939 (2,0 s) |
| `treino.avaliacao2` | membro + alocação | 0 | 23 | 10 | 0 | 1939 |
| `treino.gestao` (Gestor) | `comissao:gerir`, sistêmica | **22 atos em 12 Editais** | — | — | 0 | — |
| Publicador | `resultado:publicar` | 0 | 23 | 10 | 0 | 1165 |
| Julgador | `recurso:julgar` | 0 | 23 | 10 | 0 | 1179 |
| `treino.elaboracao` | Elaborador | — | — | — | 1 (Continuar a elaboração, SIM01) | — |

Os vinte atos da presidência, agrupados como o nível 1 já agrupa:
- **sorteio:** congelar a relação (SIM06) e observar a extração (SIM07);
- **avaliação:** distribuir (SIM05, SIM06, SIM07) e consolidar (SIM05);
- **classificação:** emitir a ordem (SIM04), emitir o corte (SIM09, SIM14), e emitir a ordem que
  declara que ninguém concorreu (sete Editais);
- **convocação:** convocar titulares (SIM10, SIM15);
- **documentos:** conferir (SIM11, SIM12).

## Achados

**V-1. A pessoa com mais trabalho é a que a faixa não vê.** A presidência tem vinte atos seus em onze
Editais, e a faixa "Ações disponíveis para você" mostra zero. Para cada um desses atos, o Centro de
Controle do Edital já põe a marca SUA. O que falta é juntar, e não derivar. O guia da equipe diz isso
sem querer: "abra o Processo e, nele, o Edital… o quadro O que fazer agora… marca com SUA"
(`doc/cenarios-de-treinamento/guia-da-equipe.md`).

**V-2. Para o avaliador, a visão pessoal já existe.** O único ato dele (Avaliar 5, SIM05) é o único
item da faixa. A mesma derivação mostra a ele 22 providências de outro papel, e a visão pessoal
**não deve** mostrá-las: elas são do Centro de cada Edital.

**V-3. Entre Editais, o mesmo ato se repete.** "Emitir a ordem que declara que ninguém concorreu
nesta lista" aparece em sete Editais, sempre na lista PPP do mesmo Perfil de treinamento. É um ato
legítimo (135), e não ruído. Mas sete linhas iguais escondem os cinco atos de convocação e de
documentos. O agrupamento da 127 (D-016) vale dentro de um Edital. A visão pessoal precisa de um
agrupamento **entre** Editais, pelo mesmo ato.

**V-4. A permissão sistêmica faz tudo virar "seu".** O Gestor, por `comissao:gerir`, recebe 22 atos
como seus em 12 Editais. São todos os atos de condução da unidade, inclusive os de um Edital em que
a comissão ainda nem foi alocada (SIM03). `pode_gerir_comissao` já devolve **qual** base autoriza
(`PERMISSAO_SISTEMICA` ou `BASE_PRESIDENCIA`). A visão pessoal deve separar o que é seu por vínculo
do que você **pode** fazer porque intervém. Sem essa separação, a lista do Gestor vira o inventário
da unidade.

**V-5. `ate` é o fim da espera, e não o prazo de quem age.** As datas que aparecem são o fim das
inscrições (12/12), o fim do prazo de recurso (17/11) e o prazo de resposta do candidato (12/12).
Nenhuma é prazo da comissão. Ordenar uma lista pessoal por elas misturaria três significados.

**V-6. O custo é linear no número de Editais, e o avaliador paga mais.** São ~77 consultas por Edital
para a presidência e ~130 para o avaliador. `do_edital` chama `trabalho.do_ator(ator, [edital])`
por Edital, e isso relê as alocações do avaliador a cada um. Uma leitura pessoal deve chamar a
104 uma vez e passar o resultado adiante, como já faz com `em_curso`.

**V-7. O que é do Publicador e do Julgador não tem fronteira de comissão.** Hoje os dois têm zero:
o resultado definitivo espera o prazo de recurso em cinco Editais, e nenhum recurso foi interposto no
C08. Quando o prazo vencer, "Publicar o resultado definitivo" vira providência de **todo** Publicador
da unidade, em cada Edital. É o caso caro: a leitura teria de percorrer todos os Editais publicados da
unidade, e não só os das comissões da pessoa.

**V-8. Os cenários não exercitam a distribuição de trabalho.** Nenhum usa a alocação à conferência
nem a designação para a formalização, e o C08 não tem recurso interposto. A visão da presidência
sobre "quem faz o quê" não pode ser validada com eles como estão.
