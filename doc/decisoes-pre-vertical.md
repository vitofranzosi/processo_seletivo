# Decisões pré-vertical

**Tomadas em 04/09/2026**, antes de abrir a spec da 015. As quatro travavam alguma coisa: duas
impedem a classificação de existir, uma impede executar os Editais em vista, e a quarta decide o
tamanho do primeiro vertical.

Nenhuma delas é feature. São contratos que as specs 014–019 vão consumir, e estão aqui para que
nenhuma delas os invente por conta própria.

## D-1 · Resultado de Etapa sem Avaliação

**A decisão:** `ResultadoEtapa.avaliacao` passa a ser **anulável**, e a linha ganha `origem`:

```
origem = AVALIACAO   →  avaliacao NOT NULL      (o que existe hoje)
origem = OCORRENCIA  →  avaliacao NULL          (ato administrativo da presidência)
```

**O que a força.** Os Editais produzem desfecho para quem não foi avaliado, e não é caso de borda:
*"o candidato que faltar à etapa de Entrevista estará automaticamente desclassificado"* (14, 6.3);
eliminação a qualquer tempo por descumprimento de pré-requisito (76, 5.3); não comparecimento ao
procedimento de verificação (35/57). Hoje a FK é `OneToOne` não-anulável — **um Resultado não pode
existir sem uma Avaliação**, e o invariante I-1 do briefing da 013 diz o contrário do que a
implementação faz.

**Por que não uma entidade própria de Ocorrência.** Ela seria mais expressiva, e criaria estrutura
antes da regra que a consome: há um consumidor só, e ele cabe num discriminador. Quando houver
ocorrência que precise de ciclo de vida próprio — contestada, revista, anulada —, a entidade nasce
com o caso que a justifica.

**Por que não registrar a ausência como conclusão decisória.** Seria barato e afirmaria que alguém
avaliou quem não compareceu. Contradiz P-006 da 012 — *avaliar não é decidir* — e mente sobre a
autoria: a ausência é constatada pela presidência, não julgada por avaliador.

**O que vai junto, e não pode ser esquecido.** A constraint `ck_resultado_completo_por_forma` hoje
alterna entre pontuada e decisória. Uma Ocorrência não tem forma nenhuma — não pontua e não
registra sentido —, então a constraint ganha um terceiro ramo, pelo mesmo caminho que a conclusão
da 012 percorreu. E o ato precisa de autor, motivo e trilha, como `resultado:consolidar` já tem: a
D-002 da 013 protege a entrada consumida, e aqui a entrada é a constatação em si.

## D-2 · Fatos do candidato que as regras consomem

**A decisão:** o **Edital declara** quais fatos exige do candidato; a inscrição os coleta e os
**congela nela**.

**O que a força.** A 015 não fecha sem isso. Os desempates reais pedem idade (14, 173, 46), tempo
de experiência em meses (14, 173), curso específico (14) e notas por disciplina (46) — e a
inscrição coleta nome, CPF, e-mail e telefone.

**Por que não é o construtor de formulários que a 009 recusou.** A recusa de lá era de
configuração de tela. Isto é **conteúdo normativo**: o fato entra porque uma regra publicada o
consome, viaja no snapshot, é retificável e responde pela mesma cadeia de vigência que peso e nota
mínima. Um Edital que não declara fato nenhum continua sem campo nenhum.

**A propriedade que importa não é coletar, é congelar.** O valor que entra na classificação tem de
ser o do momento da inscrição. Sem isso, editar o perfil depois mudaria classificação histórica —
e a Constituição exige que o estado vigente em qualquer instante relevante seja reproduzível. É a
mesma razão pela qual a Inscrição já guarda `versao_aceita`.

**O escopo mínimo:** os tipos que os Editais lidos de fato usam — data e número inteiro. Terceiro
tipo entra quando aparecer o Edital que o exija.

## D-3 · Quantas inscrições um candidato pode ter num Edital

**A decisão:** um campo publicado no Edital — `maxInscricoesPorCandidato`, anulável, onde ausência
significa **sem limite**, que é o comportamento de hoje.

**O que a força.** A restrição atual é `(identidade, edital, perfil)`: várias inscrições por
Edital, uma por Perfil. Os Editais 14 (item 7.8) e 57 exigem **uma por Edital**, e hoje isso não é
expressável.

**Por que não `unique(identidade, edital)` no banco.** Seria simples e contradiria a Constituição,
que admite Inscrições distintas para mais de um Perfil *"salvo restrição expressa do Edital"*. A
regra é do certame, não da natureza da Inscrição.

**Por que um campo, e não uma política de vários eixos.** Opções por inscrição e exclusividade
parcial entre Perfis generalizam antes da evidência — e "opções por inscrição" pressupõe algo que
o modelo não tem: a Inscrição carrega **um** `profile_id`. Quando aparecer Edital com primeira e
segunda opção, o segundo campo nasce com ele.

A constraint existente permanece: ela impede a duplicata por Perfil; o campo novo limita o total.

## D-4 · Barema fica fora do primeiro vertical

**A decisão:** o primeiro vertical roda com **apuração externa** — a banca calcula no Anexo IV e
registra o total, que é o que a Mesa já sabe receber.

**O que isso custa, dito por extenso.** A promessa de eliminar apuração paralela fora do sistema
**não se cumpre** nesse Edital: a lógica avaliativa crítica continua num anexo. Não é limitação
funcional — o processo roda e o resultado é correto —, é limitação de alcance do produto, e vale
saber que ela foi escolhida e não esquecida.

**Por que assim.** Barema é spec inteira — critérios, pontuação por item, limites por item, tela
de elaboração própria e autopontuação vinculante (173) —, serve a uma família só, e o §21 da 012
já a recusou como conteúdo que *"merece spec própria"*. Colocá-la na frente do backbone atrasaria
o que serve às duas famílias por algo que serve a uma.

## Consequências operacionais

**D-2 e D-3 acrescentam campo publicado ao Edital.** As duas passam pelo conteúdo canônico e sobem
`SCHEMA_VERSION` — hoje em 6. Feitas juntas, é **uma** elevação; feitas em specs separadas, são
duas, cada uma com seu caminho de leitura das versões anteriores. Vale planejá-las na mesma leva.

**D-1 não toca conteúdo publicado.** É esquema e regra de domínio, sem reflexo no snapshot.

**Onde cada uma é consumida:**

| Decisão | Consumida por |
|---|---|
| D-1 · desfecho não avaliativo | extensão da 013, antes da 014 |
| D-2 · fatos declarados | **015** — e a coleta é território da 009 |
| D-3 · cardinalidade | submissão da inscrição; precondição de executar 14, 57 e 46 |
| D-4 · barema fora | nada; é o que **não** entra |
