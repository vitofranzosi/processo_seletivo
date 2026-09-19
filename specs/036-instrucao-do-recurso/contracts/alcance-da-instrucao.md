# Contrato — o alcance da instrução

**O que este contrato prende**: quem passa a ver o quê, por quanto tempo, e o que fica registrado
(`FR-527` a `FR-534`).

É o contrato mais delicado desta série de features, porque é o primeiro que **concede acesso a dado
pessoal**. As três perguntas abaixo são as que toda revisão deve fazer a cada linha nova.

---

## 1. Quem passa a ver

```
sem instrução   quem julga → a peça, e a frase que diz o que falta e a quem pedir
com instrução   quem julga → a peça + o parecer atacado + o documento citado, por referência
sempre          quem preside ou audita → exatamente o que já alcançavam
```

**Ninguém ganha acesso por ter um papel.** O acesso vem do **par (aquele recurso, aquela pessoa que o
julga)**, e nasce de um ato que alguém praticou e assinou.

**Por que isto não é uma permissão disfarçada**: uma permissão vale para a classe — todo recurso, todo
Edital, enquanto durar o papel. O alcance da instrução vale para **uma** peça e morre com ela.

## 2. Por quanto tempo

| Evento | O que acontece com o alcance |
|---|---|
| instrução praticada | abre |
| recurso decidido | **fecha** |
| prazo recursal encerrado | o parecer some do canal do candidato (`FR-524`) |
| instrução praticada de novo | acrescenta; **não** substitui, e **não** reabre o que fechou |

**O fechamento não é limpeza — é regra.** Alcance que sobrevive ao ato que o justificou vira acesso
permanente concedido por um clique, e o clique não fica mais sob escrutínio de ninguém.

## 3. O que fica registrado, e o que **não** pode ficar

| Registra | Não registra |
|---|---|
| que houve instrução | **o texto do parecer** |
| quem instruiu, quando | **o conteúdo do documento** |
| qual recurso foi alcançado | **a fundamentação de quem recorreu** |
| o que foi anexado, **por espécie** | |
| que alguém **exerceu** o acesso | |

**A regra é a que a `018` já pratica**: a trilha responde *houve ato, por quem e quando* — e não *o
que ele dizia*. Copiar conteúdo sensível para a trilha cria uma segunda cópia, num lugar com outro
regime de acesso e outro tempo de retenção.

**E há padrão a seguir para registrar leitura**: a exportação de matrículas já o faz, anotando a
**população e a quantidade** vistas, e não as linhas.

---

## O que este contrato proíbe, em voz alta

1. **Ampliar `recurso:julgar`.** É a `FR-105` da `018` — *"MUST NOT ampliar o acesso a documentos do
   candidato"* — e é a razão de a saída ser um ato.
2. **Copiar o documento para o recurso.** Referência, sempre (`FR-531`).
3. **Guardar quem pode ver.** O alcance é derivado do estado do recurso, não de uma lista.
4. **Oferecer o que não se alcança.** A tela de quem julga hoje é um beco **honesto**: ela guarda os
   destinos e diz o que falta. **Essa garantia é da `033`**, e é a mais fácil de quebrar numa feature
   que existe para acrescentar o que mostrar (`FR-532`).
