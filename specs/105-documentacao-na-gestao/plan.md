# Implementation Plan: A Visão do Sistema dentro da gestão

**Spec**: [spec.md](spec.md) · **Tarefas**: [tasks.md](tasks.md)

## Resumo técnico

Uma view só leitura, `interface/documentacao.py::visao_do_sistema`, em `/gestao/documentacao/` e
`/gestao/documentacao/<arquivo>`, lê de `docs/visao-sistema/` os arquivos de uma lista literal com
o tipo de cada um (D-002) e os devolve em `HttpResponse` (D-003). A barra ganha o grupo "Ajuda" e o
símbolo `i-livro` no sprite do `base.html`. O manual perde o que a política de conteúdo recusaria: o
script de tema vai para `assets/iniciar.js`, o `style` do sprite de símbolos vira classe, e o ícone
da aba sai do endereço `data:` para `assets/icone.svg`.

As rotas levam barra no fim, ao contrário das vizinhas: o manual pede os arquivos por endereço
relativo, e sem a barra o navegador os procuraria em `/gestao/assets/`.

## Verificação constitucional

- **Negar por padrão**: sem identidade, a porta pede identificação; com identidade, só os arquivos
  da lista saem, e o resto é 404 classificado no inventário das negativas da `033`.
- **Publicação imutável, nada excluído**: não se aplica — nada é gravado.
- **Rastreabilidade**: [rastreabilidade.md](rastreabilidade.md).

## Fora do escopo

- Reescrever o conteúdo do manual: as PRs de documentação seguem como estão.
- Atualizar a própria Visão do Sistema para descrever esta feature: fica com o próximo ciclo dela.
