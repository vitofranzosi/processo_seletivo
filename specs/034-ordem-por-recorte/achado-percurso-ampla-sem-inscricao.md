# Achado do percurso — o Perfil que não declara a ampla não recebe inscrição de não-cotista

**Encontrado em 18/09/2026**, montando à mão o Edital 34/2026 do [quickstart](quickstart.md) pela
interface administrativa e pelo portal do candidato.

**Registro, e não escopo.** É anterior à `034` e não tem relação com a emissão da ordem por recorte:
a `034` ordena quem está inscrito, e este defeito impede alguém de **se inscrever**. Governança é de
quem prioriza o backlog.

---

## O que acontece

Um Perfil que declara Modalidades de Concorrência e **não** aponta qual delas é a ampla concorrência
publica normalmente. A Revisão adverte, e a advertência é sobre o **quadro**:

> O Perfil 'TUTOR-EAD' declara 2 Modalidade(s) e não declara qual delas é a da ampla concorrência.
> Enquanto não declarar, todas contam como lista reservada e o quadro precisa de linha para cada uma
> — inclusive para a que serve de ampla concorrência, cuja quantidade mora na linha geral.

No **portal do candidato**, porém, o campo `Modalidade` da inscrição é `required` e as únicas opções
são as Modalidades declaradas. Não há opção de concorrer sem autodeclaração: quem não é PcD nem PPI
**não consegue enviar a inscrição**. A recusa é do navegador — *"Selecione um item da lista"* —, e
portanto não chega ao servidor nem à trilha.

## Por que importa

O recorte da ampla concorrência é o `NULL`, e ele é o universo de **todo mundo**. Um Edital nesse
estado publica vagas na linha geral que ninguém pode disputar sem se declarar cotista — e a linha
geral é justamente a maior: no cenário montado, **7 das 10 vagas**.

## O que a advertência diz, e o que ela não diz

Ela nomeia a consequência **aritmética** — "todas contam como lista reservada, e o quadro precisa de
linha para cada uma" — e é verdadeira. O que ela não nomeia é a consequência **no portal**: quem lê
*"todas contam como lista reservada"* entende uma regra de soma do quadro, e não *"nenhum candidato
de ampla concorrência conseguirá se inscrever"*.

É a mesma forma de defeito que a `032` chamou de **nomear o sintoma e não a causa**, invertida: aqui
a mensagem nomeia a causa e cala a consequência que dói.

## O caminho que existe

Declarar uma Modalidade como a ampla concorrência resolve — é o caso normal do acervo, e é a
grafia-armadilha que a `FR-503` trata. **Não foi possível fazê-lo por Retificação** no percurso: a
tela de Retificação altera e remove Modalidades, mas não **acrescenta** — e o Perfil do cenário não
tinha uma Modalidade sobrando para apontar.

## O que o percurso fez em vez disso

Seguiu com seis inscrições cotistas — duas em PcD e quatro em PPI. O cenário continua exercitando os
três recortes e as três ordens, porque a ampla é o universo inteiro e os seis estão nela. O que ele
**não** exercita é a metade *"quem não se autodeclarou aparece só na ampla"*, que fica prendida por
`tests/unit/classificacao/test_universo_do_recorte.py::test_quem_nao_se_autodeclarou_aparece_so_na_ampla`.

---

# O segundo achado: a Retificação não acrescenta Modalidade

**Medido em 18/09/2026**, na tela `/retificar` do Edital 34/2026, varrendo os botões que ela
oferece.

A Retificação acrescenta **Perfil**, **linha do quadro de vagas**, **Evento** e **Anexo**. Não
acrescenta **Modalidade de Concorrência** — cada Modalidade existente traz "Remover do Edital", e
não há "Acrescentar Modalidade".

**A consequência é aritmética e visível:** dá para acrescentar a linha do quadro de um recorte
novo, e não dá para criar a Modalidade a que essa linha se referiria. O recorte novo, portanto, não
nasce por Retificação.

**E os campos da regra de corte também não aparecem:** `cutTargetKind`, `cutGovernedStage`,
`cutSurplusCount` e `cutContinuation` não são retificáveis; só `cutTieOutcome` é. Corrigir a Etapa
que o corte governa, num Edital publicado, não tem caminho pela interface.

## O que isso custou ao `quickstart`

- **O cenário 5.2** — *"retifique acrescentando uma quarta Modalidade"* — **é inexequível pela
  interface**. O percurso exercitou a metade que a interface alcança, e ela é a metade que a
  `FR-494a` protege: uma Retificação **do quadro**, publicada **depois** das três ordens emitidas.
  O resultado está no registro do cenário 5 da [rastreabilidade](rastreabilidade.md).
- **A convocação para vaga inicial** do cenário 2 dependia de trocar a Etapa governada do corte, e
  não houve como.

**Nenhum dos dois é da `034`**, e os dois ficam como registro para quem prioriza o backlog.
