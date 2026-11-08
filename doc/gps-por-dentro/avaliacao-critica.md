# Avaliação crítica

Inspeção em 08/11/2026, base `da566ff2`. As melhorias são propostas para decisão posterior.
Nenhuma foi transformada em nova spec de produto. A spec 133 registra somente a POC solicitada.

## Dificuldades tratadas pelo material

| Problema | Como a POC o torna observável | Limite da conclusão |
|---|---|---|
| Marco parece outro nome de etapa | Prova produz Resultado; botão separado produz ordem do marco; entrevista alimenta outro marco | A distinção foi implementada e conferida; compreensão humana não foi medida |
| Corte parece quantidade de vagas | Quatro por lista alcançam cinco pessoas para entrevista, com três vagas finais | O caso é específico, não a configuração padrão de todo edital |
| “Fora da faixa” parece fora de tudo | Elisa tem sua chegada explicada pela PcD, mesmo fora da ampla | Na produção a visão continua fragmentada por recorte |
| Classificação parece distribuição | A mesma ordem alimenta janelas diferentes; Carla sai da sequência PcD, sem mover vaga | A concomitância dinâmica continua exigindo cuidado além deste caso |
| Ocupação parece matrícula | Lugares são preenchidos antes de emitir qualquer chamada, com aviso explícito | O termo “ocupada” continua no produto; o guia não o redefine |
| Publicar parece emitir / corrigir parece editar | Resultado sucessor, ordem obsoleta, sucessora e divulgação aparecem como operações distintas | A passagem de tempo é condensada e declarada; não é reprodução jurídica de um certame |
| Arquivo parece aprovado | Versão incompleta → pendência → reapresentação → abertura → conforme → aceite | A POC não testa upload, armazenamento ou autorização real |
| Chamar suplente parece preencher | Déficit continua 1 após convocar Davi e vira zero com aceite | A cobertura por chamada em aberto é explicada; não há fila arbitrariamente editável |

## Dificuldades que exigem aperfeiçoamento da interface do GPS

| Prioridade sugerida | Oportunidade | Justificativa e evidência |
|---|---|---|
| Alta | Explicitar “por lista” na regra de corte fixo e na revisão | Uma escolha válida pode levar mais pessoas à etapa que o operador imagina; estudo de 07/11 e ACH-02 |
| Alta | Alinhar a linguagem de empate estrito ao efeito efetivo e à fronteira da faixa | Hoje uma opção parece cortar quando recusa a emissão. O material sozinho não resolve a divergência entre norma/documento/motor; ACH-01 |
| Alta, após decisão de domínio | Informar e controlar efeitos cruzados entre listas | Estudo de concorrência de 07/11 reproduz dupla ocupação/retorno. Não basta melhorar um rótulo; decidir regra institucional primeiro |
| Média | Explicar por pessoa a pontuação, o desempate e a origem de sua ocupação | O simulador já tem trajetória de desempate; telas reais priorizam posição/contagens. Explicação junto ao número reduziria necessidade de guia externo |
| Média | Exibir a união das faixas na etapa governada e por onde cada um chega | A tela de um recorte não mostra o destino global da pessoa. A POC consegue explicar por manter as duas listas lado a lado |
| Média | Adaptar termos de corte ao seu papel intermediário ou terminal | Subtítulo de progressão para etapa seguinte pode ensinar destino inexistente; ACH-06 |
| Baixa | Ligar ajuda contextual do produto a demonstrações versionadas | Evita procurar termos na dúvida, desde que base e hipóteses estejam claras. Não integrar sem teste com operadores |

Não se atribui aqui urgência institucional nem capacidade de entrega. “Alta” indica potencial de erro
de compreensão/decisão, não aprovação de escopo. O achado de concorrência é de comportamento, não
uma dificuldade a ser resolvida apenas por documentação.

## Complexidade inerente e necessária

- Há identidades distintas: pessoa, inscrição, perfil, etapa, marco e lista. Fundi-las simplificaria a
  aparência e mudaria o significado. A mesma pessoa pode participar de várias ordens.
- Nota local, habilitação, posição, faixa e ocupação respondem perguntas diferentes. Suprimir um ato
  para encurtar o percurso apagaria sua origem e sua responsabilidade.
- Recursos e Retificação precisam preservar histórico. O material pode reiniciar; o produto não pode
  reescrever publicações nem deixar que uma animação sugira essa possibilidade.
- Reservas precisam manter quantidade, participantes e movimentos separados. Concomitância não é
  reversão; titular não é suplente; déficit não é ausência de convocação.
- Formalização pode depender de setor e sistema externo. Nenhuma tela de “sucesso” deve provar um
  fato que o GPS não observou.

## O que ainda falta aprender sobre a POC

A clareza visual foi inspecionada e os cenários conferidos, mas nenhum operador participou nesta
sessão. Não é possível afirmar “o operador entendeu” com base em screenshots ou testes de código.

Proposta de próximo teste, sem abrir spec: 3 a 5 operadores, 20–30 minutos por pessoa, sem explicação
prévia. Usar as sete perguntas de `validacao.md`; pedir que apontem as pessoas e os atos que justificam
a resposta. Registrar acertos com justificativa, hesitações, palavras que induziram erro e necessidade
de voltar. Revisar primeiro a demonstração que produza mais interpretação equivocada; não adicionar
mais conteúdo para compensar automaticamente.

A POC cobre formas pontuada e decisória no texto, com demonstrações de notas e sorteio. Não há
simulação completa da etapa decisória, reclassificação, regularização, reversão, faixa seguinte,
múltiplas reservas ou cancelamento por inércia. Esses limites estão declarados; não são regras
alternativas nem funcionalidades prometidas pelo guia.
