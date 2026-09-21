# Quickstart — validar a expansão do Perfil

**Feature**: `041-perfil-na-visao-institucional` · **Data**: 2026-09-21

O cenário de ponta a ponta que o **Princípio VI** exige e que `SC-215` descreve: executável pela
interface administrativa, sem shell de banco.

> Guia de validação. As formas estão em [data-model.md](./data-model.md); as garantias, em
> [contracts/expansao-do-perfil.md](./contracts/expansao-do-perfil.md).

---

## 1. Pré-requisitos

A `040` precisa estar de pé — esta feature é uma coluna a mais na tabela dela. Banco próprio da
worktree, preparado na ordem *provisionar · migrar · provisionar*, com a contagem `N de M` **não**
começando em `0`.

```bash
cd backend && uv sync --extra dev && make preparar
```

---

## 2. O cenário que a `SC-215` nomeia

O `seed_demo` **não** produz o Edital desta feature. Ele é montado pela interface, na composição de
Perfis, e **cada linha abaixo existe por um motivo**:

| Perfil | Vagas imediatas | Cadastro de reserva | Inscrições a submeter | Por que está aqui |
|---|---:|---|---:|---|
| **Polo A** | 20 | não há | 45 | é ele que põe a razão do Edital **acima de 1** |
| **Polo B** | 20 | não há | **0** | o Perfil vazio que o agregado esconde |
| **Polo C** | **0** | **ilimitado** | **0** | *sem procura* **sem denominador** (`FR-615`), e vagas `0` como zero legítimo |
| **Polo D** | 10 | **limitado a 5** | 15 | a terceira espécie de reserva (`SC-217`) |

**Os números do Edital**: `50` vagas, `60` submetidas, e razão **`1,2`** — numerador recortado,
`60 ÷ 50`, porque o Polo C não publica vaga imediata.

> **É `1,2` que faz este cenário valer.** Acima de 1, esta linha **não recebe marca nenhuma** sob as
> regras da `040`: o agregado diz que houve procura de sobra. E dois dos quatro Perfis não tiveram
> inscrição alguma. É exatamente a capacidade que a `US2` entrega, e um cenário com razão global
> abaixo de 1 a deixaria passar sem prova — o Edital já seria marcado hoje.

**Publique com o prazo aberto e encerre por Retificação.** A `028` recusa publicar certame cujo
período já terminou — *"publicado assim, o Edital não receberá inscrição alguma"* —, e o atalho de
publicar com a data vencida não existe na realidade. Encerrar prazo é ato de quem assina o Edital.

**Para o caso da `FR-613a`**, retifique removendo o **Polo D** depois de as inscrições existirem: as
15 dele continuam contando no Edital e deixam de pertencer a Perfil vigente.

---

## 3. Subir e entrar

```bash
cd backend && INTERFACE_SELETOR_IDENTIDADE=true make runserver
```

`http://localhost:8000/gestao/visao-geral` — **`localhost`, e não `127.0.0.1`**. Identifique-se como
**Gestor**.

---

## 4. O percurso

| # | Ação | O que deve acontecer | Prende |
|---|---|---|---|
| 1 | Abrir a Visão Geral | a linha mostra `50 vagas · 60 submetidas · **1,2** inscr./vaga`, e a expansão está **recolhida** | `FR-606` |
| 2 | Ler a coluna Atenção da linha | **"2 de 4 Perfis sem nenhuma inscrição"** — sobre os **quatro** vigentes — e **"1 de 3 Perfis com vaga imediata abaixo da oferta"** — sobre os **três** que publicam vaga, porque o Polo C não tinha como estar abaixo de nada. *Sob a `040` esta linha não teria marca alguma: `1,2` é acima de 1* | `FR-614` · `SC-218` |
| 3 | Expandir a linha **pelo controle**, e não clicando na linha | os quatro Perfis, com denominação **e código ao lado**, vagas, reserva, submetidas, em preenchimento e razão — e a **localidade como publicada**, em branco onde o Perfil não a declara | `FR-607` · `FR-609` · `FR-620` |
| 4 | Conferir o **Polo B** | `20` vagas, `0` submetidas, razão `0,0`, e **as duas marcas** — o Perfil que o agregado escondia | `SC-215` |
| 5 | Conferir o **Polo C** | vagas `0` — zero legítimo —, reserva *ilimitado*, razão `—` com o motivo, e **sem procura mesmo sem denominador** | `FR-611` · `FR-615` · `SC-220` |
| 6 | Conferir o **Polo D** | *limitado a 5* — distinto de *ilimitado* e de *não há*, e com o limite dito | `FR-608` · `SC-217` |
| 7 | Somar a coluna Vagas dos Perfis | `50`, igual à linha | `FR-612` |
| 8 | Somar Submetidas dos Perfis | `60`, igual à linha | `FR-612` |
| 9 | Ler a linha principal com a expansão aberta | ela continua com as **sete colunas** do Edital, e a visão macro continua legível | `FR-617` |
| 9a | Clicar no **link do Edital**, com a expansão aberta | navega para o Edital — o link não virou gatilho de expansão | `FR-620` |
| 10 | Abrir e fechar **só com o teclado** | `Tab` até o resumo, `Enter` ou `Espaço` abre e fecha | `FR-619` · `SC-219` |
| 11 | Ver o código-fonte da linha | o `<details>` está **dentro de um `<td>`**, e não solto na `<tr>` | contrato §2 |
| 12 | Ler a página sem cor | as marcas dos Perfis e o resumo da linha continuam legíveis | `FR-614` |

### O caso que só a Retificação produz

| # | Ação | O que deve acontecer | Prende |
|---|---|---|---|
| 13 | Retificar removendo o **Polo D**, e reabrir | ele some da expansão; as `15` inscrições continuam no total do Edital; a expansão **diz em texto** que 15 foram para Perfil que a versão vigente não tem mais — e **não** aparece linha alguma chamada *"Outros"* ou *"Sem Perfil"* | `FR-613a` |

### O filtro *Somente com atenção*

| # | Ação | O que deve acontecer | Prende |
|---|---|---|---|
| 14 | Com um Edital marcado e um sem marca no recorte, ligar **Somente com atenção** | a tabela fica com **um**, e o consolidado muda **junto** | `FR-621` · `SC-221` |
| 15 | Ligar o filtro num recorte sem nenhum Edital marcado | a página declara o recorte vazio, sem afirmar nada sobre o acervo | `FR-621` |

---

### O caso do Perfil único

| # | Ação | O que deve acontecer | Prende |
|---|---|---|---|
| 16 | Abrir um Edital do `seed_demo`, de um Perfil só, com demanda baixa | a marca é a **do Perfil**, sem *"1 de 1"* | `R-004` |

---

## 5. A verificação automatizada

```bash
cd backend && make lint check test-pg
```

**`test-pg`, e não `test`** — sem o par `TEST_DB_ENGINE=postgresql` e o usuário do banco, a suíte cai
para SQLite em silêncio. **`lint` são dois passos.** E **não edite arquivo durante a execução**.

### Os arquivos desta feature

```bash
cd backend && uv run pytest tests/unit/test_visao_institucional.py tests/interface/test_visao_geral.py tests/performance/test_visao_institucional.py -q
```

### Os guardiões que a `040` deixou, e que esta feature aciona

```bash
cd backend && uv run pytest tests/interface/test_larguras.py tests/interface/test_acessibilidade.py tests/performance/test_escala_da_mesa.py tests/test_citacoes_de_requisito.py -q
```

O estilo da expansão vai no **bloco de página** que a `040` criou — e os dois primeiros arquivos
acima já sabem lê-lo ali, inclusive num parcial, porque resolvem `include`. O terceiro é o teto de
peso que a `040` estourou uma vez: folha de uma tela **não** volta para a base.

---

## 6. O critério de pronto

`SC-215` está satisfeito quando, num Edital de **50 vagas com 60 inscrições e razão `1,2`** — acima
de 1, e portanto **sem marca nenhuma** sob as regras de hoje —, quem abre a página descobre **sem
sair dela** que **dois dos quatro Perfis não tiveram inscrição alguma**.

É essa a leitura que o agregado escondia: não um número baixo, mas um número **bom** cobrindo dois
Perfis vazios.

> **Nota sobre a redação anterior.** Ela fechava com *"o número `0,5 inscr./vaga` da linha"*, e
> `0,5` era `19 ÷ 40` — a razão **não recortada**, que é precisamente a que a decisão do numerador
> da `040` existe para nunca calcular. O critério de fechamento citava o número que a feature
> anterior proíbe, e quem percorresse o roteiro concluiria que a implementação falhou.
