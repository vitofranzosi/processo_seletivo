# Checklist de acessibilidade, responsividade e proteção de dados — 011

**Feature**: [spec.md](./spec.md) | **Data**: 2026-09-01

Os critérios abaixo são **herdados** dos padrões institucionais já adotados pelo projeto. Eles não
são requisitos da 011 e por isso não ocupam FR na spec — mas continuam sendo condição de entrega, e
é aqui que são conferidos, tela a tela, antes de fechar cada slice.

O que é específico desta feature está na spec e não se repete aqui: o estado "sem membros alocados"
que não pode depender de cor, o nome acessível que distingue as duas remoções, os 375 px sem rolagem
horizontal e o limite do que se expõe da pessoa.

## Telas cobertas

1. Comissão do Processo (lista e adicionar membro)
2. Alteração de função e remoção de membro
3. Organização por Etapa, por Edital publicado
4. Gerenciar membros de uma Etapa
5. `Minhas Etapas` e o detalhe da atribuição

## Teclado

- [ ] Cada fluxo crítico é concluível somente pelo teclado, do início ao fim: constituir, alocar,
      remover da Etapa, remover da comissão.
- [ ] A ordem de foco segue a ordem visual em cada uma das cinco telas.
- [ ] O foco é visível em todos os controles, inclusive nos destrutivos.
- [ ] Nenhum controle recebe foco sem ter nome acessível.
- [ ] Confirmação de remoção devolve o foco a um ponto previsível depois de fechada.

## Nomes, rótulos e estados

- [ ] Todo campo de formulário tem rótulo associado — inclusive o identificador institucional e o
      rótulo de exibição, que não podem ser distinguidos só por `placeholder`.
- [ ] O aviso de que o identificador não é verificado pelo sistema é programaticamente associado ao
      campo, e não texto solto ao lado.
- [ ] Mensagens de erro identificam o campo que as causou.
- [ ] Estados de sucesso após alocar, remover ou alterar função são anunciados, e não apenas
      exibidos.

## Contraste e conformidade

- [ ] Contraste de texto e de componentes conforme os critérios eMAG/WCAG vigentes adotados pelo
      projeto.
- [ ] Nenhuma informação essencial depende exclusivamente de cor — verificado também em escala de
      cinza.
- [ ] Zoom de 200% não corta conteúdo nem controle.

## Responsividade

- [ ] As cinco telas funcionam em 375 px sem rolagem horizontal da página.
- [ ] A organização por Etapa agrupa em vez de virar tabela horizontal em telas estreitas.
- [ ] Alvos de toque das ações destrutivas não ficam adjacentes a ponto de errar o alvo.

## Proteção de dados

- [ ] Nenhum identificador sensível em URL.
- [ ] Log técnico não registra dado pessoal completo quando o identificador estável basta.
- [ ] Nenhuma tela desta feature exibe dado de candidato — a 011 não opera sobre eles.
- [ ] A trilha de auditoria não recebe o rótulo de exibição, que não é identidade.
