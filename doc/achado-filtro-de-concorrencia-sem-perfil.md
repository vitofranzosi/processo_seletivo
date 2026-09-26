# O filtro de concorrência repete a Modalidade por Perfil sem dizer de qual

**Data:** 2026-09-25
**Origem:** [conferência do envio e da análise documental](conferencia-envio-e-analise-documental.md),
§3 e §7, e a `044` (*Riscos e lacunas*, R-014 e a tarefa T067), que o registrou como defeito de tela
independente e fora do escopo dela. Os três passaram a apontar para este documento.
**Natureza:** rótulo ambíguo. O filtro funciona; quem filtra é que não sabe em qual opção clicar.
**Situação:** **corrigido** em 2026-09-25, por decisão do usuário: o nome do Perfil no rótulo, e só
o rótulo. A restrição do seletor ao Perfil ativo ficou registrada, fora do escopo.

## O defeito

A consulta administrativa *Inscrições recebidas*, do Gestor, tem um seletor **Concorrência**
(`interface/templates/interface/inscricoes.html`). As opções saem de `por_modalidade`, montado em
`inscricoes/application/consulta.py::_contagens` com uma entrada por Modalidade **de cada Perfil**.
A Modalidade é do Perfil, e não do Edital: dois Perfis com "Ampla Concorrência" têm duas Modalidades
distintas, com identidades distintas. O seletor as mostra com o mesmo texto:

```
Todas
Ampla concorrência (0)                    ← 403, Professor de Informática
Pessoas pretas, pardas e indígenas (0)
Ampla concorrência (0)                    ← 407, Técnico de Laboratório
```

O valor de cada opção é a identidade certa, e filtrar por ela devolve só as inscrições daquele
Perfil. O defeito é só o rótulo: as duas opções se leem iguais, e a contagem entre parênteses é a
única pista de qual é qual.

No Edital 903/2026 da conferência, com C1 (AC, PcD, PPIQ) e C2 (AC, PcD), "Ampla Concorrência" e
"Pessoas com Deficiência" aparecem duas vezes cada.

## Confirmado

Medido em 2026-09-25 contra PostgreSQL, com uma sonda descartável sobre a fixture `selecao`
(`tests/fixtures/selecao.py`), que já tem dois Perfis com "Ampla concorrência". O HTML do seletor é
o do bloco acima. A sonda não ficou no repositório.

## Por que ninguém viu

- **O dado já estava lá.** `_contagens` entrega, em cada item de `por_modalidade`, a chave `perfil`
  com o nome do Perfil. O template nunca a leu.
- **Os testes da tela filtram por identidade.**
  `test_o_filtro_por_modalidade_responde_a_pergunta_da_cota` (`test_inscricoes_em_escala.py`) monta a
  URL com o UUID e confere as linhas. O rótulo da opção não é afirmado em teste nenhum.
- **A fixture tinha o caso.** O Técnico tem "Ampla concorrência" com o mesmo nome do Docente. O
  defeito estava na tela de todos os testes da consulta, e nenhum olhava o seletor.

## O que foi feito

Proposto e aprovado nesta forma. Nomear o Perfil no rótulo da opção e manter o valor, que é a identidade da Modalidade:

```
Professor de Informática · Ampla concorrência (0)
Professor de Informática · Pessoas pretas, pardas e indígenas (0)
Técnico de Laboratório · Ampla concorrência (0)
```

- **Só quando o Edital tem mais de um Perfil**, a mesma condição que já decide se os cartões por
  Perfil aparecem (`por_perfil|length > 1`). Com um Perfil só, o prefixo repetiria a mesma palavra em
  todas as linhas sem desfazer ambiguidade nenhuma.
- **O nome do Perfil, e não o código.** Os cartões acima do seletor e a coluna *Perfil* da tabela
  identificam o Perfil pelo nome. O código ("C1") só aparece no editor
  (`interface/templates/interface/_documento.html`, "C1 — Curso · AC — Ampla"). Usá-lo aqui obrigaria
  quem filtra a saber de cor que C1 é o Curso de teste, que é o mesmo cruzamento de cabeça que a
  conferência apontou na Mesa. O custo é o comprimento: nome de Perfil de Edital real pode ser longo,
  e o seletor fica largo. A alternativa era o código, curto e sugerido no registro original. O
  usuário escolheu o nome.
- **Custo zero de consulta.** A mudança é só de template, sobre uma chave que `_contagens` já
  entrega. `test_o_custo_da_tela_e_o_da_pagina_e_nao_o_do_certame` não se move.
- **Dois testes** em `backend/tests/integration/interface/test_inscricoes_em_escala.py`:
  `test_a_opcao_de_concorrencia_diz_de_qual_perfil_e`, sobre a fixture `selecao`, afirma o texto de
  cada opção, com as duas "Ampla concorrência" sob Perfis diferentes. Reprovou antes da mudança do
  template. `test_com_um_perfil_so_a_opcao_nao_repete_o_nome_dele` prende a condição dos cartões.

## O que fica registrado, e não vira escopo

- **O seletor ignora o Perfil escolhido.** Com o cartão do Técnico ativo (`?perfil=…406`), o seletor
  continua oferecendo as Modalidades do Docente. Escolher uma delas devolve "Nenhuma inscrição
  recebida corresponde a este filtro", porque as duas condições não se cruzam. Restringir as opções
  ao Perfil ativo resolveria, e seria mudança de comportamento, e não de rótulo.
- **Os demais filtros da gestão.** A conferência diz "os filtros da gestão", no plural. A varredura
  dos templates da `interface` encontrou só este seletor de Modalidade. O do editor de Documento
  Exigido já nomeia o Perfil.
