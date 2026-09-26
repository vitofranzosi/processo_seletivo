# Quickstart: validar Duplicar Perfil

**Feature**: [spec.md](./spec.md) · **Contrato**: [contracts/duplicar-perfil.md](./contracts/duplicar-perfil.md)

Roteiro de validação, e não de implementação. Os dois primeiros blocos provam os requisitos por
teste; o terceiro é o cenário demonstrável do princípio VI (`SC-235`); o quarto mede `SC-230` e
`SC-231`.

## Pré-requisitos

- PostgreSQL local com `LC_ALL` exportado; worktree com `uv sync --extra dev` feito.
- Banco de teste **próprio** desta worktree: `DB_NAME=ps_043`.
- Para a demonstração, banco de desenvolvimento preparado (`make preparar`: o `N de M` com `N`
  diferente de zero) e o runserver com `INTERFACE_SELETOR_IDENTIDADE=true`.

## 1. Verificação do repositório

```bash
cd backend && make lint check test-pg DB_NAME=ps_043
```

## 2. Os testes desta feature

```bash
cd backend && TEST_DB_ENGINE=postgresql DB_USER=$(whoami) DB_RUNTIME_USER=$(whoami) DB_NAME=ps_043 uv run pytest tests/unit/editais/test_duplicacao.py tests/interface/test_duplicar_perfil.py tests/authorization/test_duplicar_perfil.py -q
```

O que cada família prova:

| Arquivo | Prova |
|---|---|
| `tests/unit/editais/test_duplicacao.py` | a transformação de [data-model.md](./data-model.md): identidades novas, remapeamento para dentro, preservação para fora, completude contra o contrato, marco derivado × escrito à mão, identidade vazia, origem intocada |
| `tests/interface/test_duplicar_perfil.py` | o fragmento: cartão devolvido, colisão e Código vazio, avisos de marcos e de documentos, travessia do campo em trânsito por gravação e por recusa, cadeia sem gravar, origem intacta nos três desfechos |
| `tests/authorization/test_duplicar_perfil.py` | 404 fora do escopo e sem `edital`; 403 sem `edital:elaborar` e com Edital fora da elaboração; origem de outro Edital não é lida |

## 3. Demonstração de ponta a ponta (`SC-235`)

Pela interface, com o papel de quem elabora, sem shell nem banco:

1. Criar um Edital com uma Etapa classificatória e um Evento de inscrição com datas futuras.
2. Na etapa Perfis, compor o **LP01**: quatro Modalidades com fundamento e percentual, uma delas
   declarada ampla concorrência, quantidades nas linhas reservadas, dois fatos declarados. Gravar.
3. Na etapa Classificação, declarar o marco do LP01 com um critério de desempate que cite um fato.
   Gravar.
4. Na etapa Documentos, declarar um documento restrito ao LP01. Gravar.
5. Voltar à etapa Perfis. No LP01, *Duplicar este Perfil* → Código `LP02`, Localidade `Serra`.
   Conferir: o cartão LP02 aparece logo abaixo, com foco; o anúncio diz que leva **1** marco e que
   **1** documento não foi replicado.
6. No LP02 ainda não gravado, duplicar para `LP03` / `Cariacica`. Gravar a etapa.
7. Na Classificação, conferir que LP02 e LP03 têm marco com código `LP02` e `LP03`, e o critério
   apontando o fato **do próprio Perfil**.
8. Submeter, homologar, trocar de identidade e publicar. No documento publicado: três Perfis com o
   conteúdo do LP01 e os Códigos e Localidades informados.

## 4. Medição contra o baseline (`SC-230`, `SC-231`)

Mesma unidade do estudo de 21/09: cada clique, campo preenchido e escolha de *radio* ou lista.

1. Compor a etapa Perfis do conteúdo do 140/2025 (16 Perfis, 64 Modalidades), com datas futuras:
   o primeiro Perfil inteiro; os quinze seguintes por duplicação, ajustando só o que o Edital
   diverge (os três blocos de requisito de Letras).
2. Contar as interações **da etapa Perfis** no percurso, e registrar a contagem por Perfil.
3. Critério: total ≤ **150** (baseline ~530); média por cópia ≤ **8** (baseline ~33).
4. Relatar à parte, sem somar ao critério, a economia na etapa Classificação (`R-011`).
