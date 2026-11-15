# Implementation Plan: Novidades do GPS

**Branch**: `claude/gps-novidades-feature-16ea57` | **Date**: 2026-11-14 | **Spec**: [spec.md](spec.md)

## Summary

Uma página de leitura na gestão, alimentada por um arquivo TOML do próprio app, com o registro, por
identidade, do que já foi visto. A barra ganha um item com a contagem, guardada na sessão para
continuar sem consulta ao banco. Nenhuma regra do certame muda.

## Technical Context

**Language/Version**: Python 3.13, Django 5.2 · **Storage**: PostgreSQL (uma tabela nova, mutável) e
um arquivo `novidades.toml` lido com `tomllib` (biblioteca padrão) · **Testing**: pytest contra
PostgreSQL · **Dependências novas**: nenhuma · **Performance**: zero consulta nova nas telas da gestão;
uma na entrada da sessão e duas (leitura e gravação) na abertura da página.

## Constitution Check

| Princípio | Como se cumpre |
|---|---|
| II — imutabilidade, nada se exclui | A tabela não é ato nem dado normativo: guarda o que a identidade viu e muda a cada visita. Nada se exclui; a nota que sai do arquivo deixa o registro inerte. |
| III — negar por padrão | A página é de toda identidade da gestão, como a Agenda, e só diz o que mudou no produto. A nota de um público se esconde de quem não o integra, e o link segue o predicado da barra. Nenhum dado de candidato. |
| V — simplicidade | Sem CMS, sem chamada externa em execução, sem dependência nova; TOML da biblioteca padrão. |
| VI — jornada | O operador abre a gestão, vê a contagem, abre a página e chega à tela nova pelo link. |

## Project Structure

```text
backend/processo_seletivo/novidades/        app novo
  models.py         LeituraDasNovidades (subject, vistas, ultima_visita)
  catalogo.py       leitura e forma do arquivo; CatalogoInvalido
  leitura.py        disponibilidade, contagem da sessão, registro da visita
  novidades.toml    as notas
  curadoria.toml    o registro: o início da janela e os PRs deixados sem nota, com o motivo
backend/processo_seletivo/interface/
  novidades_do_gps.py                 a view
  templates/interface/novidades.html  a página
  static/interface/telas/novidades.css
  navegacao.py      o item Novidades e a contagem no item
  identidade.py     ao_entrar() na entrada de demonstração e na institucional; recontar() na troca
  templates/interface/base.html       o ícone e a contagem no item
  static/interface/gestao/moldura.css a contagem, e o ponto na barra recolhida
backend/scripts/rascunhar_novidades.py      o roteiro de curadoria (fora da aplicação)
doc/curadoria-das-novidades.md              o guia
```

## Decisões de implementação

- **R-001 — A contagem na sessão, calculada na entrada.** A barra tem um guardião de zero consultas
  (`test_montar_a_barra_nao_consulta_o_banco`). A entrada da gestão grava na sessão os identificadores
  não vistos; a barra cruza a lista com as notas disponíveis, que estão em memória. A sessão aberta
  antes da implantação fica sem número até a próxima entrada.
- **R-002 — A contagem nasce na camada de identidade.** `identidade.identificar()`,
  `entrar_institucional()` e `trocar_unidade()` chamam `leitura.ao_entrar()` (sessão nova) ou
  `leitura.recontar()` (troca de unidade, que não apaga o bloco da visita). Na primeira versão os
  ganchos estavam nas três views de entrada; a revisão de código de 14/11 os levou para onde a sessão
  nasce, para que um caminho novo de entrar não fique sem contagem em silêncio. Nenhum teste chama
  essas funções fora das views.
- **R-003 — O arquivo é relido só quando muda.** O carregador guarda o resultado pela data de
  modificação, e a falha também: em produção, a release é imutável e o arquivo é lido uma vez por
  processo; com o arquivo inválido, o erro não é reinterpretado a cada tela.
- **R-004 — O que pede o resto do sistema se confere na suíte, não no carregador.** Rotas, âncoras da
  Documentação do Sistema (que não vai para o servidor), configurações, capacidades e specs: o
  carregador confere só a forma, para a página não quebrar em produção.

## Complexity Tracking

Nenhuma violação.
