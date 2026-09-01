# Fase 1 — Como demonstrar e validar

**Feature**: 010 — Área do Candidato e Acesso sem Senha | **Data**: 2026-09-01

A condição de conclusão de cada entrega é o **percurso navegado**, não a contagem de testes
(princípio VI da Constituição, P-009 da spec). Este guia diz como preparar o ambiente, o que rodar, o
que abrir e o que se deve ver.

Detalhes de entidade estão em [data-model.md](./data-model.md); as rotas, em
[contracts/acesso.md](./contracts/acesso.md) e [contracts/area.md](./contracts/area.md); o porquê de
cada escolha, em [research.md](./research.md).

---

## Pré-requisitos

Três particularidades do ambiente, todas conhecidas, nenhuma da feature. Valem como na `009`:

- **PostgreSQL local precisa de `LC_ALL`**, e a role padrão da máquina não existe no cluster —
  sobrescreva `DB_USER`.
- **`TEST_DB_ENGINE=postgresql` é obrigatório e é o que se esquece.** Sem ela a suíte cai para sqlite
  em memória **sem avisar**, e nesta feature o custo é grande: a exclusividade do endereço canônico, a
  restrição de CPF em inscrição enviada e o bloqueio de linha da reconciliação simplesmente não são
  exercidos.
- **Um banco de teste por worktree.** Duas suítes em paralelo disputam o mesmo banco e se destroem.

```bash
cd backend && TEST_DB_ENGINE=postgresql LC_ALL=en_US.UTF-8 DB_USER="$(whoami)" DB_NAME=ps010 uv run pytest -q
```

Uma particularidade nova: **o envio de mensagem precisa de mecanismo declarado**. Em
desenvolvimento, o mecanismo de console imprime o código no terminal — que é exatamente o que a
recusa de inicialização impede em produção (`FR-081`).

```bash
cd backend && INTERFACE_SELETOR_IDENTIDADE=true DJANGO_EMAIL_BACKEND=console DEFAULT_FROM_EMAIL=nao-responda@exemplo.test ARQUIVOS_CANDIDATOS_RAIZ=/tmp/ps-arquivos DB_USER="$(whoami)" uv run python manage.py runserver 8010
```

Note o que **não** está aí: `PORTAL_IDENTIDADE_DEMO`. A partir desta feature a identificação por
declaração não existe, e a variável permanece apenas como armadilha na recusa de produção (D-011).

---

## Preparação dos dados

A demonstração precisa de participação anterior, criada **antes** da migração de reconciliação — é a
única forma de exercer o caminho que a feature existe para resolver.

1. Com o repositório na `009`, publique um Edital com um Perfil e documentos exigidos, e faça uma
   inscrição completa como Maria, com um CPF e um endereço, submetendo dois documentos.
2. Anote o protocolo.
3. Aplique as migrações desta feature. A reconciliação roda aqui.

```bash
cd backend && DB_USER="$(whoami)" uv run python manage.py migrate
```

**O que se deve ver**: a migração conclui, e o registro em log não menciona CPF algum. Se houver
inscrição enviada sem CPF utilizável, ela **interrompe** enumerando as inscrições que a impediram —
e isso é o comportamento correto (`FR-046`).

---

## Entrega 1 — informar endereço, informar código, chegar à área

**Abrir**: `/acesso`.

1. Informe um endereço qualquer que não tenha participação anterior. A tela responde que, *se* o
   endereço puder ser utilizado, um código será enviado — sem dizer se existe (`FR-020`).
2. Copie o código do terminal do servidor e cole-o **inteiro** no campo único (`UX-005`).
3. **Deve-se ver**: a área pessoal, vazia, convidando a consultar os processos seletivos — sem
   aparência de erro (`FR-061`).

**Verificar também**: repita com um endereço inexistente e com um existente, e compare a resposta, o
texto e a janela de reenvio. Devem ser idênticos (`SC-005`). Peça o código seis vezes seguidas: a
sexta responde igual às cinco primeiras.

**Não deve acontecer**: pedido de CPF em nenhum momento (`SC-006`).

---

## Entrega 2 — reencontrar a participação anterior

**Abrir**: `/acesso`, com o endereço que Maria usou na inscrição da `009`.

1. Confirme o código. Aparece o convite: *encontramos participação anterior associada a este
   endereço*.
2. **Recuse** — "Continuar sem isso". Deve-se cair numa área vazia, com sessão válida (`FR-052`).
3. De dentro da área, **retome** a reconciliação e confirme o CPF de Maria.
4. **Deve-se ver**: a inscrição de Maria, com o protocolo anotado na preparação, e o mesmo titular de
   antes (`SC-007`, `SC-025`).

**Verificar no banco**: nenhum `identity_subject` de inscrição mudou (`SC-007`).

**Verificar o fechamento da janela**: repita o percurso, recuse o convite, abra qualquer rascunho, e
tente retomar. A ação não é mais oferecida (`FR-053`).

---

## Entrega 3 — nome, CPF e continuar de onde parou

1. Como candidato novo, abra a vitrine e inicie uma inscrição. Nome e CPF são pedidos **uma vez**.
2. Saia, entre de novo, inicie outra inscrição em outro Perfil. **Não** são pedidos de novo
   (`SC-020`).
3. Volte a um rascunho por `Continuar inscrição`: o conteúdo está como estava (`SC-019`).
4. Em `/conta`, corrija o nome. **Deve-se ver** o nome corrigido no rascunho aberto, e inalterado em
   qualquer inscrição já enviada (`SC-011`, `FR-014`).

---

## Entrega 4 — conferir o que foi submetido

**Abrir**: a inscrição enviada de Maria.

**Deve-se ver**, numa única tela: oportunidade, situação, protocolo, instante do envio, versão
normativa aceita, dados informados, e os dois documentos com nome de arquivo, tamanho e instante de
envio (`SC-021`).

Visualize e baixe cada documento; obtenha o comprovante. As evidências de integridade continuam as
mesmas de antes da feature (`SC-022`).

---

## Entrega 5 — acompanhamento

Na mesma inscrição, abra o acompanhamento. **Deve-se ver** dois blocos visualmente distintos: os
fatos da participação e o cronograma do processo (`SC-023`).

Retifique o Edital pelo canal institucional e recarregue: aparece o aviso de atualização, a versão
aceita **não** muda, e nada é reaberto (`SC-024`).

---

## Entrega 6 — credenciais

Em `/conta`: adicione um segundo endereço e prove-o por código — sem que CPF seja pedido. Torne-o
principal. Remova o primeiro. Tente remover o último: recusado (`FR-018`).

Verifique que nenhuma inscrição mudou (`SC-011`).

---

## Demonstração de segurança — condição de conclusão

Seis casos, todos observáveis no navegador. Prepare duas identidades: Maria, com inscrição e
documentos; João, com os seus.

| # | O que fazer | O que deve acontecer |
|---|---|---|
| 1 | Na sessão de Maria, trocar o identificador da inscrição e do documento pelos de João | `404` nos dois, sem revelar existência (`SC-012`) |
| 2 | Controlar um endereço próprio, conhecer o CPF de Maria, entrar | área vazia; nada de Maria; nenhum vínculo com aquele CPF (`SC-013`) |
| 3 | Antes de Maria existir, tentar reservar o CPF dela; depois, submeter inscrição declarando-o | Maria entra normalmente, e a inscrição dela **não** é recusada; a coincidência aparece assinalada na consulta administrativa (`SC-027`) |
| 4 | Provar um endereço que Maria digitou por engano anos atrás | entra na própria identidade, sem ver nada de Maria; a identidade dela permanece intacta |
| 5 | Recusar o convite por engano, ainda sem inscrição, e retomá-lo | recupera o acesso à participação anterior (`SC-025`) |
| 6 | Anotar o identificador de sessão antes de entrar e conferir depois | é outro (`SC-004`) |

---

## Concorrência — o que a suíte precisa exercer

Três pontos, e nenhum deles é observável clicando:

1. **Mesmo código, duas requisições simultâneas** → um único consumo (`SC-003`).
2. **Mesmo endereço, duas confirmações simultâneas** → uma única credencial, recusada pelo banco e
   não por consulta prévia (`SC-015`).
3. **Retomada da reconciliação concorrente com a abertura de um rascunho** → ou a movimentação
   acontece inteira, ou não acontece; nunca uma identidade descartada com credencial para trás, nem
   inscrição órfã (`SC-016`, D-010).

---

## Antes de considerar concluída

```bash
cd backend && make check && make lint && TEST_DB_ENGINE=postgresql LC_ALL=en_US.UTF-8 DB_USER="$(whoami)" DB_NAME=ps010 uv run pytest -q
```

E a verificação que só a produção responde:

```bash
cd backend && DJANGO_SETTINGS_MODULE=config.settings.production DJANGO_EMAIL_BACKEND=console uv run python manage.py check
```

**Deve-se ver** a recusa de inicialização nomeando a variável a corrigir (`SC-017`).
