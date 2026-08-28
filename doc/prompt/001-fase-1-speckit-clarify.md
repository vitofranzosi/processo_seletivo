No projeto:

`D:\projetos\processo_seletivo_cefor\processo_seletivo.specify`

continue o desenvolvimento utilizando **GitHub Spec Kit**, respeitando integralmente a Constituição v1.0.0 já ratificada em:

`.specify/memory/constitution.md`

## Objetivo

Executar a próxima etapa do Spec Kit para criar a primeira especificação funcional do sistema:

**Processo Seletivo e Editais**

Utilize o fluxo oficial equivalente a:

```text
/speckit.specify
```

A especificação deve descrever **o que o sistema precisa fazer**, e não como será implementado.

Não definir nesta etapa:

* framework;
* linguagem;
* banco de dados;
* tabelas;
* entidades JPA;
* endpoints REST;
* arquitetura física;
* bibliotecas;
* classes;
* infraestrutura;
* código-fonte.

Esses aspectos serão tratados posteriormente nas etapas de planejamento técnico.

---

# 1. Contexto do domínio

O sistema será utilizado pelo **Cefor/IFES** para apoiar a gestão de processos seletivos.

O modelo de domínio deve considerar a seguinte hierarquia conceitual:

```text
Processo Seletivo
 ├── Edital
 │    ├── Perfil de Vaga
 │    ├── Vagas
 │    ├── Cotas / modalidades de concorrência
 │    ├── Cronograma
 │    ├── Regras
 │    └── Retificações
```

Um Processo Seletivo representa uma iniciativa institucional de seleção.

Um Processo Seletivo poderá possuir **um ou vários editais**.

Cada edital poderá possuir características próprias, inclusive cronograma independente.

---

# 2. Decisões de domínio já consolidadas

As decisões abaixo foram levantadas anteriormente e são **requisitos do domínio**, não questões em aberto.

A especificação deve incorporá-las explicitamente.

## 2.1 Processo Seletivo

Um Processo Seletivo poderá possuir múltiplos editais.

Cada edital pertence a um único Processo Seletivo.

O Processo Seletivo deve possuir uma identificação institucional própria.

Deve ser possível acompanhar seu ciclo de vida.

Não assumir que todos os editais do Processo Seletivo precisam estar simultaneamente na mesma etapa.

---

# 3. Editais

Um Processo Seletivo poderá possuir vários editais.

Cada edital deve possuir:

* identificação;
* número;
* ano;
* título;
* descrição quando aplicável;
* vínculo com o Processo Seletivo;
* situação;
* datas relevantes;
* regras próprias;
* cronograma próprio;
* histórico de alterações.

Um mesmo Processo Seletivo poderá possuir editais com cronogramas independentes.

---

# 4. Perfis de vaga

Um mesmo edital poderá abranger **vários perfis de vaga**.

Exemplos conceituais:

```text
Edital
 ├── Professor – Informática
 ├── Professor – Matemática
 └── Tutor – Administração
```

Cada perfil de vaga poderá possuir características próprias, tais como:

* identificação;
* denominação;
* descrição;
* requisitos;
* quantidade de vagas;
* modalidade/localidade quando aplicável;
* informações relevantes para classificação e convocação.

Não assumir que um edital corresponde a apenas uma vaga ou apenas um perfil.

---

# 5. Vagas e cotas

As vagas devem estar vinculadas ao respectivo perfil de vaga.

O sistema deve permitir representar modalidades de concorrência e reservas de vagas.

A aplicação das cotas deverá respeitar **a legislação vigente**.

Portanto, a especificação não deve fixar algoritmos permanentes de arredondamento, distribuição ou ordem de convocação que possam contrariar legislação futura.

Sempre que possível, separar conceitualmente:

```text
Regra normativa
```

de

```text
resultado da aplicação da regra
```

A solução futura deverá permitir evolução das regras de cotas sem exigir redefinição de todo o domínio.

---

# 6. Cadastro de reserva

O Processo Seletivo poderá trabalhar com cadastro de reserva.

A especificação não deve presumir que todo cadastro de reserva possui obrigatoriamente quantidade máxima fixa.

A existência e os limites do cadastro de reserva devem decorrer das regras do respectivo edital/perfil.

---

# 7. Cronograma

Cada edital poderá possuir cronograma próprio.

O cronograma poderá possuir múltiplos eventos ou períodos, por exemplo:

* publicação;
* período de inscrição;
* solicitação de isenção;
* recursos;
* divulgação de resultados;
* convocação;
* outras etapas definidas pelo edital.

A especificação não deve limitar o cronograma apenas aos exemplos acima.

O sistema deverá permitir inclusão de novas etapas sem necessidade de alterar o conceito fundamental de Edital.

Cada evento do cronograma deve permitir, conforme a natureza do evento:

* identificação;
* descrição;
* data;
* período;
* ordem ou sequência lógica;
* situação.

---

# 8. Retificações

Um edital poderá possuir **uma ou várias retificações**.

Uma retificação poderá alterar **qualquer conteúdo do edital**.

Não existem campos do edital considerados permanentemente imutáveis por regra geral de domínio.

Entretanto:

* alterações devem ser rastreáveis;
* o histórico anterior não deve ser perdido;
* deve ser possível identificar qual retificação produziu determinada alteração;
* deve ser possível conhecer a ordem cronológica das retificações;
* o sistema deverá preservar auditabilidade.

A especificação deve diferenciar claramente:

```text
conteúdo vigente
```

de

```text
histórico das versões/retificações
```

Uma retificação não deve apagar o registro histórico do conteúdo anteriormente publicado.

---

# 9. Publicação e histórico

Editais e respectivas retificações são documentos institucionais.

A especificação deverá prever rastreabilidade suficiente para responder futuramente a perguntas como:

```text
Qual era o conteúdo vigente do edital em determinada data?
```

```text
Qual retificação modificou determinado conteúdo?
```

```text
Qual é atualmente a versão vigente?
```

Não definir ainda a técnica de versionamento.

Definir apenas o comportamento esperado.

---

# 10. Estados e ciclo de vida

Identifique, durante a especificação, quais estados de negócio são necessários para:

* Processo Seletivo;
* Edital;
* Retificação;
* cronograma quando aplicável.

Não inventar estados desnecessários.

Os estados devem refletir eventos reais do domínio.

Sempre diferenciar:

```text
estado do Processo Seletivo
```

de

```text
estado de um Edital
```

porque um Processo Seletivo pode possuir vários editais com evolução independente.

---

# 11. Regras temporais

Datas e períodos deverão possuir coerência temporal.

Exemplos de invariantes a considerar:

* início de um período não pode ser posterior ao seu término;
* eventos de cronograma devem pertencer ao contexto correto do edital;
* retificações podem alterar datas futuras ou outras informações do edital;
* uma alteração não deve eliminar o histórico anterior.

Não definir soluções técnicas para controle temporal.

---

# 12. Identidade e numeração

Não presumir que o identificador técnico seja o mesmo identificador utilizado institucionalmente.

A especificação deve separar conceitualmente:

```text
identidade interna
```

de

```text
número/código institucional
```

quando necessário.

---

# 13. Exclusão e preservação histórica

Por se tratar de dados institucionais relacionados a processos seletivos e documentos publicados, a especificação deve considerar preservação histórica.

Evitar requisitos que impliquem exclusão destrutiva de informações já publicadas ou utilizadas.

Quando houver cancelamento, substituição, encerramento ou perda de vigência, privilegiar estados de negócio e histórico.

---

# 14. Auditabilidade

Operações relevantes deverão ser rastreáveis.

Especialmente:

* criação de Processo Seletivo;
* criação de Edital;
* alteração de Edital;
* publicação;
* criação/publicação de retificação;
* alterações de cronograma;
* mudanças de situação relevantes.

Nesta etapa, especificar **o requisito de auditabilidade**, sem escolher biblioteca ou tecnologia.

---

# 15. Escopo inicial da feature

A feature deve concentrar-se na gestão estrutural de:

```text
Processo Seletivo
Edital
Perfil de Vaga
Vagas
Modalidades de concorrência/cotas
Cronograma
Retificações
Histórico
```

Ainda não detalhar completamente módulos posteriores, tais como:

* inscrição de candidatos;
* envio de documentos;
* pagamento;
* análise de inscrições;
* recursos de candidatos;
* provas;
* avaliação;
* classificação;
* resultado final;
* convocação;
* contratação.

Caso esses conceitos precisem ser mencionados, trate-os apenas como dependências futuras ou atores externos ao escopo atual.

---

# 16. Usuários e atores

Identifique os atores necessários para esta feature com base no domínio.

No mínimo, considere conceitualmente:

* usuário responsável pela gestão administrativa do Processo Seletivo;
* usuário autorizado a elaborar/manter edital;
* usuário autorizado a publicar;
* usuário consultando informações públicas.

Não criar uma matriz completa de RBAC nesta etapa, salvo se necessária para descrever os cenários funcionais.

---

# 17. User stories

Crie user stories priorizadas.

Priorize primeiro fluxos que produzam valor independente.

Como referência, avalie histórias semelhantes a:

### P1

Criar e administrar um Processo Seletivo.

### P1

Criar um Edital vinculado ao Processo Seletivo.

### P1

Cadastrar perfis e respectivas vagas de um edital.

### P1

Definir e manter o cronograma independente do edital.

### P1

Publicar o edital.

### P1/P2

Retificar um edital preservando seu histórico.

### P2

Consultar versão vigente e histórico de retificações.

Não copie mecanicamente essa lista se o Spec Kit indicar decomposição melhor.

---

# 18. Critérios de aceitação

Para cada user story, produzir cenários verificáveis no formato adequado do Spec Kit.

Dar preferência a cenários observáveis, como:

```text
Given
When
Then
```

ou estrutura equivalente utilizada pelo template.

Os critérios devem permitir que futuramente testes funcionais sejam derivados diretamente da especificação.

Evitar critérios vagos como:

```text
O sistema deve funcionar corretamente.
```

Preferir comportamentos verificáveis.

---

# 19. Casos extremos

A especificação deverá considerar explicitamente edge cases relevantes, incluindo:

* Processo Seletivo sem edital;
* Processo Seletivo com vários editais;
* edital com um único perfil;
* edital com múltiplos perfis;
* edital sem vagas imediatas e somente cadastro reserva, se permitido pelas regras;
* cronogramas diferentes entre editais do mesmo Processo Seletivo;
* retificação que altera cronograma;
* retificação que altera quantidade de vagas;
* retificação que altera perfil de vaga;
* múltiplas retificações sequenciais;
* tentativa de consultar histórico;
* tentativa de modificar informações já publicadas sem mecanismo formal de alteração;
* inconsistências de datas;
* edital cancelado;
* Processo Seletivo encerrado com editais históricos.

Inclua outros edge cases identificados durante a especificação.

---

# 20. Requirements

Gerar requisitos funcionais numerados e verificáveis.

Exemplo de formato:

```text
FR-001
FR-002
FR-003
...
```

Cada requisito deve:

* expressar uma obrigação clara do sistema;
* possuir comportamento verificável;
* evitar decisão prematura de implementação;
* respeitar a Constituição do projeto;
* estar relacionado ao escopo desta feature.

---

# 21. Entidades conceituais

Caso o template do Spec Kit solicite entidades-chave, descreva-as apenas em nível conceitual.

Exemplo:

```text
Processo Seletivo
Edital
Perfil de Vaga
Vaga
Modalidade de Concorrência
Evento de Cronograma
Retificação
```

Não definir:

* tabelas;
* tipos SQL;
* chaves estrangeiras físicas;
* anotações JPA;
* classes Java;
* cardinalidades de banco.

Relacionamentos conceituais podem ser descritos.

---

# 22. Success Criteria

Definir critérios mensuráveis de sucesso para esta feature.

Eles devem ser independentes de tecnologia.

Exemplos de categorias:

* completude do cadastro;
* rastreabilidade;
* consistência;
* capacidade de consulta;
* preservação histórica;
* tratamento de múltiplos editais;
* tratamento de múltiplos perfis.

Evitar métricas artificiais que não tenham fundamento no domínio.

---

# 23. Assumptions

Registrar apenas premissas realmente necessárias.

Não transformar decisões já estabelecidas em assumptions.

As decisões consolidadas neste prompt devem ser tratadas como requisitos conhecidos.

---

# 24. Ambiguidades

Se durante o `/speckit.specify` forem encontradas ambiguidades relevantes:

1. tente resolvê-las primeiro usando as decisões de domínio já fornecidas;
2. não invente regra jurídica ou institucional;
3. registre somente dúvidas que realmente impeçam uma especificação consistente;
4. limite as perguntas aos pontos de alto impacto.

Evite perguntas sobre detalhes que podem ser adiados para `/speckit.plan`.

---

# 25. Constituição

Antes de concluir, valide a especificação contra:

```text
.specify/memory/constitution.md
```

Nenhum requisito pode contradizer os princípios constitucionais.

Caso encontre conflito entre este prompt e a Constituição:

1. não altere silenciosamente a Constituição;
2. identifique o conflito;
3. preserve a Constituição;
4. informe o problema no relatório final.

---

# 26. Saída esperada

Ao final:

1. informar o branch/feature criado pelo Spec Kit;
2. informar o caminho do arquivo `spec.md`;
3. apresentar resumo das user stories;
4. informar quantidade de requisitos funcionais;
5. informar os principais edge cases registrados;
6. informar assumptions eventualmente utilizadas;
7. informar se existem `[NEEDS CLARIFICATION]`;
8. confirmar validação contra a Constituição v1.0.0;
9. informar se a especificação está pronta para a próxima etapa;
10. não implementar código.

Apresente o resultado final em formato semelhante a:

```text
Status: CONCLUÍDO
Feature:
Branch:
Spec:
User stories:
Requisitos funcionais:
Edge cases:
Clarificações pendentes:
Validação constitucional:
Próximo passo recomendado:
```

Se a especificação estiver completa, o próximo passo esperado deverá ser a etapa de clarificação/revisão prevista pelo Spec Kit antes da elaboração do plano técnico.
