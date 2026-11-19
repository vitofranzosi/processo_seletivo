# Proposta resumida — CPF coincidente e identidade do candidato

**Data:** 2026-11-18
**Situação:** proposta para discussão; ainda não é uma decisão de produto nem uma especificação.

## Decisão recomendada

Manter, por enquanto, o acesso do candidato por e-mail, sem depender do Gov.br e sem transformar o
CPF em credencial de entrada.

O CPF deve continuar sendo tratado como um dado declarado e um sinal de possível coincidência, não
como prova automática de que duas contas pertencem à mesma pessoa.

Inscrições com o mesmo CPF podem ser enviadas, evitando que um terceiro bloqueie preventivamente um
candidato legítimo. Entretanto, a coincidência precisa ser resolvida antes que possa gerar vantagem
no certame.

## Fluxo proposto para coincidências

1. O sistema detecta inscrições com o mesmo CPF no recorte em que a duplicidade pode afetar o
   resultado.
2. A coincidência entra em uma fila de pendências da comissão.
3. A comissão compara as inscrições e registra uma decisão motivada:
   - mesma pessoa;
   - pessoas distintas;
   - CPF informado incorretamente;
   - possível uso indevido.
4. Os candidatos envolvidos são comunicados sem exposição dos dados da outra conta.
5. Quando a decisão prejudicar uma inscrição, deve existir prazo e canal de contestação.
6. A decisão e eventual revisão são preservadas no histórico; nada é apagado ou alterado
   silenciosamente.

Se ficar comprovado que as inscrições são da mesma pessoa, aplica-se a regra definida previamente
no Edital para determinar qual permanece vigente. Uma possibilidade é considerar a última inscrição
enviada dentro do prazo, mas essa regra não deve ser implícita nem adotada sem fundamento normativo.

## Travas necessárias

Enquanto houver coincidência relevante sem decisão, o sistema deve impedir, apenas no recorte
afetado:

- a consolidação da relação de habilitados;
- o sorteio;
- a publicação da classificação ou do resultado que utilize aquelas inscrições;
- a convocação que possa conceder vantagem duplicada à mesma pessoa.

A mensagem de bloqueio deve informar a quantidade de pendências e levar a comissão diretamente à
fila de resolução. Recortes sem pendência continuam normalmente.

## Histórico distribuído entre contas

Para permitir que uma pessoa consulte inscrições feitas com e-mails diferentes, propõem-se duas
etapas posteriores:

### União voluntária

Quando a pessoa ainda controla os dois e-mails, ela comprova o acesso às duas contas por códigos e
solicita sua associação. O histórico passa a ser exibido de forma consolidada, sem transferir ou
reescrever as inscrições originais.

### Recuperação institucional

Quando a pessoa não controla mais o e-mail antigo, ela solicita a recuperação pela conta atual e
apresenta as evidências definidas pela instituição. Uma autoridade com permissão específica analisa
o pedido, comunica as credenciais envolvidas e registra uma decisão motivada após um prazo de
segurança.

A aprovação cria um vínculo entre as contas. Ela não apaga a conta antiga, não altera o autor
original das inscrições e não reescreve o histórico. Uma decisão equivocada é corrigida por novo
ato, mantendo a trilha anterior.

## Ordem recomendada de entrega

1. **Proteção do certame:** fila da comissão, decisão, comunicação, contestação e travas.
2. **Substituição de inscrição:** se houver previsão no Edital, permitir que uma nova inscrição da
   mesma pessoa suceda a anterior dentro do prazo.
3. **União voluntária de contas:** consolidar o histórico quando há controle dos dois e-mails.
4. **Recuperação institucional:** tratar a perda do e-mail antigo com análise humana e segurança
   reforçada.

## Síntese

A proposta equilibra baixa fricção para o candidato e proteção do processo seletivo: ninguém é
impedido de se inscrever apenas porque outra conta declarou o mesmo CPF, mas uma coincidência não
resolvida não pode avançar até produzir duas chances, classificações ou convocações para a mesma
pessoa.

O Gov.br pode permanecer fora do escopo inicial. A prioridade deve ser fechar o fluxo institucional
de detecção, decisão, comunicação, contestação e bloqueio; depois, evoluir para a consolidação segura
do histórico entre contas.
