# O piloto do design system: fotografia, comparação e resultado

*A implementação da [spec 172](../../../specs/172-piloto-do-design-system/spec.md), que parte da
`main` em `499491be` (o merge do #563). Aqui ficam o instrumento de comparação e o que ele mediu. O
relatório para decisão está na pasta da spec.*

| O quê | Onde |
|---|---|
| O "antes": inventários de 64 estados × 5 larguras, e uma captura a 1440 px de cada estado | [`antes/`](antes/) |
| O "depois", no mesmo formato | [`depois/`](depois/) |
| A comparação, estado a estado, e o resumo | [`comparacao/`](comparacao/) |
| O comparador e as sequências declaradas | [`scripts/comparar.py`](scripts/comparar.py), [`scripts/sequencias.toml`](scripts/sequencias.toml) |
| O catálogo dos estados e a jornada que fotografa | `backend/tests/navegador/piloto/` e `backend/tests/navegador/test_fotografia_do_piloto.py` |

## Como reproduzir

De `backend/`, com as variáveis do `make test-pg` e o grupo `navegador`:

```bash
PILOTO_DS_FOTOGRAFIA=/caminho/antes PYTEST_ADDOPTS="tests/navegador/test_fotografia_do_piloto.py -q" make test-pg PYTEST_WORKERS=4
```

```bash
uv run python ../doc/auditoria-design-system-2026-11-14/piloto/scripts/comparar.py /caminho/antes /caminho/depois /caminho/saida
```

A jornada leva cerca de um minuto com 4 workers. Sem a variável, o módulo pula.

## O que o levantamento achou (fase 1 das tarefas)

**De onde vem cada estado (T002).** Cada um dos 64 estados é uma função do catálogo, com a prova de
que foi alcançado. A tabela código → montagem → prova → papel é o próprio catálogo:
[`confirmacao.py`](../../../backend/tests/navegador/piloto/confirmacao.py),
[`ocupacao.py`](../../../backend/tests/navegador/piloto/ocupacao.py),
[`conferencias.py`](../../../backend/tests/navegador/piloto/conferencias.py) e
[`lista.py`](../../../backend/tests/navegador/piloto/lista.py). Os estados que nenhum teste de tela
desenhava, e que o catálogo monta pela primeira vez: C-01 (submeter sem pendência, com o cronograma
no futuro), C-04 (o texto da revogação), O-03, R-04, K-01 com o processo administrativo e K-03.

**Quatro desvios do catálogo da spec (D-004), registrados e não escondidos:**

- **C-12 virou C-12 e C-13.** A spec juntava num código a recusa do envio e a tela de quem não tem a
  permissão, e são duas páginas. São 64 estados, e não 63.
- **O-06 mostra dois estados e o "Não se aplica"**, e não um recorte vigente ao lado. O único
  cenário com três recortes e um sem inscrito (`certame_com_cotas`) não tem ordem emitida em nenhum
  deles; montar um vigente ali seria cenário novo, sem teste que o sustente.
- **O-14 mostra o movimento de vaga, e não a recusa do acréscimo fora da linha geral.** Os dois
  dependem de cenários incompatíveis (um sorteio com reversão e um Perfil com reserva e cota).
  A frase do impedimento fica sem fotografia.
- **O retorno de cada gesto (R-NN) é montado pelo cliente da sessão**, e não por clique: a tela guarda
  o resultado na sessão e o mostra no GET seguinte, e a recusa precisaria de um botão que a tela, de
  propósito, não oferece. As conferências (K-NN), que só existem como resposta de um POST, são
  montadas por clique no navegador.

**Scripts e classes (T003).** Nenhuma das cinco telas carrega `rascunho.js`, `remocao.js`,
`visualizador.js` nem `envio.js`: a única folha de script da gestão nelas é `shell.js`, da moldura.
As classes que os testes de tela procuram nelas (`resumo`, `consequencias`, `aviso`, `erro`, `nota`,
`sucessao`, `confirmar`, `salvar`, `acoes`, `bastao`, `irreversivel`, `processo`,
`linha-do-edital`, `abas-da-lista`, `busca-da-lista`, `frase-do-recorte`, `acoes-disponiveis`,
`sem-acoes`, `codigo`, `situacao`, `marca-da-retificacao`) ficam nos elementos em que estão.

**Tokens (T004).** `grupos/acesso.css` já declara em `:root` os neutros da entrada, com os mesmos
nomes e os mesmos valores que o estudo propõe. Acrescentá-los a `tokens.css` com os mesmos nomes não
muda tela nenhuma (a entrada os redeclara iguais), e por isso **não levam prefixo**. Os pares de
contraste novos entram na lista `PARES` de `tests/interface/test_acessibilidade.py`.

**Colisão de cenários (T010).** A jornada monta um estado por caso, e o banco do caso some: a
colisão dos identificadores fixos de linha só importa no banco da validação com a equipe, e é medida
lá (US4).

## O que a checagem de sanidade mostrou (T013)

A jornada rodou duas vezes sobre o mesmo código, e o comparador comparou as duas fotografias.

- **Zero diferença de texto, de quantidade, de ação e de sequência** nos 64 estados, depois de três
  correções no comparador: casamento exato, por classe, por etiqueta e por item nos termos das
  sequências (o trecho solto achava o rótulo "Fundamento da homologação" dentro da recusa que o
  cita); a T-S1 da spec saiu da conferência, porque a trilha é da moldura, fora do `main`; e a
  ampla concorrência do R-10 saiu da comparação, porque o sorteio da fixture a muda de uma montagem
  para a outra (0 e 1 ocupadas).
- **As 28 sequências se aplicam** a pelo menos um estado.
- **O "antes" já reprova dois critérios absolutos, e é o que o piloto existe para corrigir:** 244
  das 320 fotografias têm linha de prosa acima de 80 caracteres (até 193 a 1920 px, no aviso da vaga
  sem quem a ocupe), e sete estados têm a ação principal abaixo da dobra a 1280 × 800 (C-01, C-06,
  K-01, K-04, K-06, O-13 e O-15). Nenhuma a 375 px.
