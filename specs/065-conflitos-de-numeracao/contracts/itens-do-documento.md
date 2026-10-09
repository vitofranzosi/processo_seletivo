# Contrato — os itens que o documento imprime

Função pura em `publicacoes/infrastructure/pdf.py`, ao lado de `numeracao` (`D-004`).

## Entrada e saída

- **Entrada:** o snapshot, o mesmo que o compositor recebe.
- **Saída:** a lista dos itens que o documento imprime como identificação, cada um com número,
  natureza e descrição (ver [data-model.md](../data-model.md)), e o total de tabelas.

## O que ela promete

1. **Mesma regra da composição.** Os números das seções são os de `numeracao`; os das subseções de
   Perfis são `N.1 … N.k` na ordem do snapshot, seguidos das subseções comuns da `064`
   (`grupos_de_atribuicoes`); os das Etapas, `N.1 … N.m`. O total de tabelas é o número de legendas
   "Tabela N" que a composição escreveria.
2. **Seção que não sai não tem item** — nem ela, nem subseção dela.
3. **Nenhum efeito.** Não compõe, não lê banco, não muda o snapshot.
4. **A composição não muda** por causa dela: os documentos saem com os mesmos bytes (`FR-1219`).

## O guardião

Um teste compõe o documento — os conteúdos congelados de A e de B da auditoria e casos sintéticos
(um Perfil só; Perfil sem quadro; Perfil sem modalidade; sem Etapa; Etapas sem Perfis com
atribuições comuns; seção gerada vazia) — e colhe da composição os títulos de subseção numerados e
as legendas "Tabela N". Os números colhidos e os da função têm de ser os mesmos. Mudar a composição
sem mudar a função reprova.
