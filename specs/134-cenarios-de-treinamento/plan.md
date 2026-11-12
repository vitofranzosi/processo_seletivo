# Plano: cenários de treinamento e homologação

**Spec**: [spec.md](spec.md) · **Tarefas**: [tasks.md](tasks.md) · **Verificação**:
[verificacao.md](verificacao.md)

## Diagnóstico técnico

### O que já existia, e o que serviu

| Recurso | O que é | Uso nesta feature |
|---|---|---|
| `seed_demo` | demonstração de quatro Editais pelo fluxo real, com atores distintos | **moldes** dos rascunhos (Perfil docente, Perfil de sorteio, Cronograma, Etapas, método do sorteio), que a suíte prova publicáveis a cada commit (D-005); a credencial verificada da pessoa fictícia; a sequência de passos de cada etapa |
| Comandos da aplicação | `create_process_with_first_edital`, `replace_draft`, `submit/homologate/publish_edital`, `create/transition/publish_retification`, `abrir_inscricao`, `gravar_dados`, `anexar_documento`, `enviar_inscricao`, `adicionar_membro`, `alocar`, `distribuir`, `concluir`, `consolidar`, `emitir_ordem`, `publicar_resultado`, `emitir_corte`, `emitir_apuracao`, `convocar`, `comunicar`, `apresentar`, `conferir`, `publicar_relacao`, `cancel_edital`, `cancel_process` | **todo** estado de cenário; nenhuma linha de domínio é gravada fora deles (FR-4640) |
| Fonte de demonstração do sorteio | adaptador de semente fixa, ligado por `SORTEIO_FONTE_DE_DEMONSTRACAO`, recusado em produção | o sorteio sem espera (D-004) |
| Seletor de identidade | entrada da demonstração, com os papéis e as comissões tirados do banco | o acesso da equipe; a presidência e a avaliação dos cenários aparecem sozinhas |
| Barreiras de produção | `AMBIENTE_DE_PRODUCAO` e as recusas de `production.py` | a primeira barreira, e a recusa da chave nova |
| Fixtures de teste (`tests/fixtures/*`) | cenários montados pela API, com identificadores fixos | **não** reaproveitadas: dependem do cliente de teste e colidem entre si (dois cenários de convocação no mesmo banco falham) |

### O que precisou ser desenvolvido

- o **manifesto** (`CenarioDeTreinamento`), única tabela nova (D-001);
- o **remapeamento** de identificadores, porque Perfil, Etapa, marco e Evento têm identidade global
  e os moldes usam `00000000-…-00NN-…` (FR-4630);
- a **montagem** (`construcao.py`), uma sequência de passos sobre os comandos, e o **catálogo** com
  as quinze receitas;
- o **retrato** do cenário, por introspecção, para dizer se foi exercitado (FR-4617);
- os **quatro comandos** e as **barreiras**.

### Restrições do domínio que decidiram o desenho

1. **Nada se exclui.** Publicação, trilha, inscrição enviada, ordem, corte, apuração, convocação,
   itens e apresentações são append-only por gatilho e por privilégio ausente. Restaurar por
   exclusão é impossível, e por isso a restauração cria a rodada seguinte (D-002).
2. **Publicar com o prazo vencido é recusado** (a FR-346 da `028`). Os Editais com inscrições
   encerradas são publicados com o prazo aberto, recebem as inscrições e têm o prazo encerrado por
   Retificação — o caminho do `seed_demo`.
3. **Distribuir exige o conjunto fechado**: avaliação só depois da Retificação de encerramento.
4. **Ocorrência única por fonte e referência** no acervo: cada rodada de sorteio declara o seu
   concurso (`8NNRRRUUU`: cenário, rodada e um resumo da unidade).
5. **O primeiro uso de uma autoridade a torna imutável** (a FR-1121 da `060`). Achado da suíte desta
   feature: o instantâneo linha a linha acusou a autoridade da suíte alterada pela carga. Daí a
   FR-4616.
6. **Conforme exige abertura registrada pela tela** (a FR-3611 da `115`) (D-007).
7. **Definitivo sem janela computável exige declaração expressa** (a FR-085 da `018`): C09 e C14
   declaram, com fundamento, que o marco não admite recurso.

### Divergências encontradas entre documentação e código

- O `seed_demo` diz que a autoridade é "reaproveitada" entre execuções; ele **cria** autoridades
  quando não acha as dele, o que um gerador num banco compartilhado não pode fazer (FR-4615).
- A página de acesso da demonstração sugere, para cada papel, o nome de quem mais o exerceu na
  trilha. Com os quinze cenários, os atores `treino.*` passariam a ser a sugestão para a equipe
  real, que agiria nos Editais de verdade com esses nomes. `treino.` entrou nos sujeitos fora da
  equipe, como `cand:` (`interface/demonstracao.py`).

### Riscos

| Risco | Mitigação |
|---|---|
| Carga no banco errado | `--banco` por extenso, conferido com o conectado; pré-visualização que mostra destino |
| Carga em produção | três barreiras; `production.py` recusa a chave |
| E-mail para fora | correio de memória na montagem; domínio `.test` |
| Cenário parcial | uma transação por cenário, com o manifesto |
| Restauração apagando o que não devia | ela não apaga; cancela pelos comandos, só os Editais e o Processo do manifesto, conferida a propriedade |
| Arquivo órfão no disco depois de falha | aceito e documentado: o banco não aponta para ele |
| Lista de Processos poluída | uma rodada em uso por cenário em "Em andamento"; as substituídas em "Cancelados" |

## Estrutura

```text
backend/processo_seletivo/treinamento/
├── ambiente.py          # as três barreiras
├── identificadores.py   # uuid5 por unidade, cenário e rodada, CPF, pessoa fictícia
├── construcao.py        # Montagem: os passos sobre os comandos da aplicação
├── catalogo.py          # as quinze fichas e receitas
├── retrato.py           # o estado de um cenário, por introspecção
├── servico.py           # carregar, planejar, verificar, restaurar
├── models.py            # CenarioDeTreinamento (o manifesto)
└── management/commands/ # carregar, listar, verificar, restaurar
```

## Verificação

`cd backend && make lint check test-pg`, com os testes da feature em
`tests/integration/treinamento/` e `tests/unit/treinamento/`.

## Revisão de 12/11/2026 — o provisionamento da formalização

Spec: FR-4615 revista, FR-6720 a FR-6729, SC-2210 a SC-2212, D-009 e D-010.

### O que já existia, e o que serviu

| Recurso | Uso |
|---|---|
| `seguranca.application.acessos.conceder` (107) | o vínculo Formalização, com motivo e trilha; recusa pessoa inativa e vínculo já vigente |
| `formalizacao.application.designar.designar` e `revogar` (117) | a designação do C16, e a revogação na restauração |
| `formalizacao.application.definir.definir` (117) | a definição dos documentos, pela presidência |
| `convocacao.application.desfechar.desfechar` (019) | o aceite que torna a pessoa apta |
| `_FORA_DA_EQUIPE` em `interface/demonstracao.py` | `treino.formalizacao` fica fora das sugestões sem mudança nenhuma |

### O que precisou ser desenvolvido

- em `construcao.py`: o ator `treino.acessos`, a identidade `treino.formalizacao` (a única escrita
  pelo ORM, como a do candidato fictício), e os passos `desfechar`, `definir_formalizacao`,
  `habilitar_formalizacao` e `designar_formalizacao`;
- em `catalogo.py`: o C16 e o C17, sobre um Edital de notas com documento só na inscrição (D-010);
- em `servico.py`: a linha da pré-visualização sobre a identidade e o vínculo, e a revogação das
  designações da rodada anterior na restauração (FR-6726).

### Restrições que decidiram o desenho

1. **A designação exige o vínculo** (a FR-3663 da `117`): o vínculo vem antes, na mesma transação.
2. **Ninguém designa a si mesmo**, nem pelo banco: quem designa é `treino.acessos`, e quem é
   designada, `treino.formalizacao`.
3. **O aceite exige os obrigatórios da convocação conformes**, e conforme exige abertura pela tela:
   daí o Edital sem documento na convocação (D-010).
4. **A pessoa institucional começa por `pessoa-`.** `treino.formalizacao` não começa, e por isso não
   entra na busca da gestão de acessos nem pela autenticação institucional — o isolamento é o do
   formato, e não uma regra nova.

### Riscos

| Risco | Mitigação |
|---|---|
| Uma pessoa chamada `treino.formalizacao` que o gerador não criou | a entrada institucional só cria `pessoa-…`; criada à mão (um `createsuperuser`), é reaproveitada sem alteração e recebe o vínculo — num banco de treinamento, o nome é do gerador (FR-6721) |
| O gerador concedendo mais que o papel | `conceder` é chamado com um papel só, e a suíte conta os vínculos (SC-2212) |
| O exercício de designar sem quem designe pela demonstração | declarado na ficha e nas limitações; depende da revisão da `117` |
