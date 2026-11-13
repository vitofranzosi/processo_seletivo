# Contrato: o cadastro de reserva no documento

**Feature**: [../spec.md](../spec.md) · **Decisões técnicas**: [../research.md](../research.md) (T-006, T-007)

As formas exatas que o documento imprime. `{N}` é o número por extenso como o documento já escreve
(`6 (seis)`), com o singular quando é 1. `{marco}` é o nome do marco que convoca. Nada aqui vale para o
Perfil legado (`Cadastro.legado`): ele imprime o que imprimia (FR-6944).

---

## C1 — A frase do cadastro (`frase_do_cadastro`)

| Caso | Frase |
|---|---|
| não há | `não há cadastro de reserva` *(sem mudança)* |
| ilimitado | `cadastro de reserva sem limite de classificados` *(sem mudança)* |
| limitado, sem Modalidade | `cadastro de reserva de até {N} classificados por Perfil` |
| limitado, com Modalidade, mesmo número em todas as listas | `cadastro de reserva de até {N} classificados em cada lista de concorrência` |
| limitado, números diferentes | `cadastro de reserva de até {N1} classificados na ampla concorrência, {N2} na lista {Modalidade 2} e {N3} na lista {Modalidade 3}` |
| qualquer limitado, com empate que admite excedente | a frase acima, seguida de `, além dos empatados na última posição` (FR-6938) |
| limitado sem corte no marco que convoca | `""`: o Perfil não é publicável (FR-6935), e a frase não inventa número |

O singular: `de até 1 (um) classificado`. A lista de números diferentes segue a ordem do quadro, com
"ampla concorrência" para a linha geral.

## C2 — A célula da tabela de Perfis (`_reserva`, redação vigente)

| Caso | Célula |
|---|---|
| limitado, sem Modalidade | `até {N} classificados` |
| limitado, mesmo número com Modalidade | `até {N} classificados por lista` |
| limitado, números diferentes | `até {N1} AC, {N2} {código 2}, {N3} {código 3}` |
| não há, ilimitado | *(sem mudança)* |

`AC` é a linha geral, como os Editais escrevem a ampla concorrência na ordem de chamada; os demais são
os códigos das Modalidades. A célula não carrega o empate: ele está na unidade do corte (K2).

Na **redação 1** (documentos antigos), a célula continua `limitado em {N}`: o legado com o número
digitado, o não legado com o derivado — `limitado em 1 AC, 2 PcD` quando difere por lista.

## C3 — A abertura da unidade do corte no Perfil só de reserva (`frases_do_corte`, FR-6943)

Vale só para o marco que convoca de um Perfil com 0 vaga imediata e cadastro limitado ou ilimitado.
`{de cada lista}` é ` de cada lista de concorrência` quando o Perfil tem linha de Modalidade.
`{Etapa}` só entra quando o corte governa uma Etapa.

| Caso | Abertura |
|---|---|
| limitado | `Compõem o cadastro de reserva os {N} primeiros classificados{de cada lista}.` |
| limitado, `N = 1` | `Compõe o cadastro de reserva o 1 (um) primeiro classificado{de cada lista}.` |
| ilimitado, alcance > 0 | `Compõem o cadastro de reserva todos os classificados, sem limite. São chamados primeiro os {A} primeiros{de cada lista}.` |
| ilimitado, alcance 0 | `Compõem o cadastro de reserva todos os classificados, sem limite.` |
| com Etapa governada | a abertura, seguida de `Eles participam da Etapa “{Etapa}”.` |

`{A}` é o alcance da faixa inicial (alvo fixo + excedente, ou o excedente no alvo do quadro). Depois da
abertura, a unidade continua como hoje: o empate (K2), sem a frase dos suplentes (C4), e a continuação
(K8), que só existe no ilimitado.

## C4 — Os suplentes e o cadastro (FR-6942)

Sai na unidade do corte do marco que convoca, quando o excedente é maior que zero e o Perfil tem vaga
imediata. Deixa de depender de **outro** Perfil do Edital.

| O Perfil | Frase |
|---|---|
| não há cadastro | `Os suplentes são chamados, na ordem, para as vagas deste Edital que não forem preenchidas pelos primeiros classificados.` *(a de hoje, sem mudança de texto)* |
| limitado ou ilimitado | `Os suplentes formam o cadastro de reserva deste Perfil e são chamados, na ordem, para as vagas que não forem preenchidas pelos primeiros classificados.` |

## Exemplos de aceitação

1. Perfil de 2 vagas, limitado, alvo do quadro, excedente 3, sem continuação:
   - unidade do corte: `Seguem no processo os primeiros classificados de cada lista de concorrência, em número igual ao das vagas dessa lista, mais 3 (três) suplentes.` + o empate + C4 (limitado);
   - cadastro: `cadastro de reserva de até 3 (três) classificados por Perfil`.
2. Perfil só de reserva, limitado, alvo fixo 4, excedente 2, sem continuação:
   `Compõem o cadastro de reserva os 6 (seis) primeiros classificados.`; célula `até 6 (seis) classificados`.
3. Perfil só de reserva, ilimitado, alvo fixo 10, continuação admitida:
   `Compõem o cadastro de reserva todos os classificados, sem limite. São chamados primeiro os 10 (dez) primeiros.` + o empate + `Depois, poderão ser chamados outros candidatos, além desses, seguindo a mesma ordem.`
4. Perfil com ampla (2 vagas), PcD (1) e PPI (1), limitado, alvo fixo 3, excedente 0:
   números 1, 2 e 2 → `cadastro de reserva de até 1 (um) classificado na ampla concorrência, 2 (dois) na lista PcD e 2 (dois) na lista PPI`; célula `até 1 (um) AC, 2 (dois) PcD, 2 (dois) PPI`.
