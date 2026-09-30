# Quickstart — como repetir a medição

## Preparar

```bash
createdb -T ps_polish_audit ps_056_polish
cd backend && DB_NAME=ps_056_polish DB_USER=$USER DB_RUNTIME_USER=$USER uv run python manage.py migrate --check
```

Se `ps_polish_audit` não existir: `createdb ps_056_polish`, `migrate` e `seed_demo`. O Edital de
trabalho é o **76/2027**, em elaboração.

Servidor nativo com o seletor de identidade (`INTERFACE_SELETOR_IDENTIDADE=true`), entrar como
`ana.gestora` com os papéis de responsabilidade, janela de **1280 × 900**.

## Medir

Em cada etapa de `/gestao/editais/<76/2027>/compor/<etapa>`, pelo console da página:

- **stepper**: altura de `ol.assistente`, quantos topos distintos têm os `li`, as larguras deles;
- **topo do trabalho**: o `top` do primeiro `h2` depois do stepper;
- **envio**: `new FormData(formulário, botão "Salvar rascunho")`, sem o `csrfmiddlewaretoken`,
  serializado em pares — comparado como conjunto ([D-005](research.md)); **não enviar**;
- **Cronograma**: altura do `fieldset.evento`, `top` de Início e de Término, largura de Descrição e de
  "Onde acontece";
- **Etapas, Inscrição, editor do Perfil**: se o grupo de ações divide faixa vertical com algum campo;
  texto da legenda;
- **Conteúdo e Revisão**: `document.documentElement.scrollHeight`;
- **Anexos**: `left` e `right` de "Avançar", comparados com os de outra etapa;
- **Retificar do 01/2026**: controle, largura e `scrollWidth > clientWidth` de Título, Descrição e
  Declaração; ordem dos rótulos do primeiro Perfil.

E a **375 px** (viewport emulado): `scrollWidth` do documento igual à janela no stepper, no
Cronograma e no Conteúdo.

## O teto da distribuição

```bash
cd backend && make test-pg DB_NAME=<banco-próprio> PYTEST_ADDOPTS="-q -s tests/performance/test_escala_da_mesa.py -k distribuicao_nao_cresce"
```

com um `print(len(corpo))` temporário antes da asserção, revertido depois.

## A suíte

```bash
cd backend && make lint check test-pg DB_NAME=<banco-próprio>
```
