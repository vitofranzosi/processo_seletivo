# Quickstart: Conferência com o documento à vista

## Testes

```bash
cd backend
make lint check
DB_NAME=ps_157 make test-pg
```

Só esta feature, durante o trabalho:

```bash
cd backend
PYTEST_ADDOPTS="tests/interface/test_conferencia_com_o_documento_a_vista.py tests/interface/test_mesa_visualizador.py tests/integration/avisos -q" DB_NAME=ps_157 make test-pg PYTEST_WORKERS=0
node --test tests/javascript/visualizador.test.js
```

## Percurso no navegador

Banco próprio (`DB_NAME` único), `INTERFACE_SELETOR_IDENTIDADE=true`, `AVISOS_AOS_CANDIDATOS=true`.
O cenário é o C09 da `134` (`CENARIOS_DE_TREINAMENTO=true manage.py carregar_cenarios_de_treinamento --banco <banco>`),
levado até a convocação com documentos enviados, como no estudo (passos B e C2).

**Tela larga (1440 × 900)**, como a presidência, em *Documentos da convocação* de Alice:

1. Entrar na página: nenhum arquivo é pedido (aba de rede), e o aviso *"Você ainda não abriu a
   versão 1"* está junto das opções.
2. *"Abrir"* no diploma: o painel aparece à esquerda, a barra diz o documento, a versão e Alice, o
   foco está no título do painel; o cartão do diploma está à vista; o aviso vira *"aberto por você"*.
3. Marcar *Conforme* e registrar: o cartão, o resumo e a situação mudam sem recarga; o painel
   continua; a confirmação oferece *"Abrir"* o comprovante.
4. *"Abrir"* pela confirmação, conferir o comprovante: a confirmação oferece a próxima pessoa.
5. Em Bernardo, registrar *Pendente* no "diploma": a confirmação diz que nenhum aviso foi pedido;
   conferido o outro documento, oferece *"Pedir aviso para Bernardo"*; pedir; a situação diz
   *"Aviso solicitado em …; aguardando envio."*; rodar `manage.py despachar_avisos` e recarregar:
   *"Aviso enviado em …: aceito pelo servidor de correio."*
6. Tentar *Conforme* sem abrir num documento de Cecília: a recusa no cartão diz como prosseguir, e o
   que foi marcado continua.
7. **Sem prévia**: no Firefox, desligar `pdfjs.disabled = true` (ou no Chrome, *"Baixar PDFs"*):
   *"Abrir"* mostra a alternativa no painel, sem moldura; abrir em aba própria e voltar: a marca é
   relida.
8. **Recusa no painel**: num documento cujo arquivo foi trocado no disco (resumo diverge), *"Abrir"*:
   a frase da recusa aparece no painel, e não a página de bloqueio do navegador.

**390 × 844**, a mesma pessoa:

9. *"Abrir"*: o arquivo abre fora da página. Digitar um motivo antes. Voltar: o motivo continua, o
   cartão diz *"aberto por você"*, o link *"Voltar à conferência do Diploma de graduação"* tem o foco.
10. Recarregar a página com um motivo digitado e um arquivo aberto fora: o motivo é restaurado, com a
    frase da restauração; nada foi registrado.
11. Nenhuma rolagem horizontal a 390 px e a 320 px.

**Mesa** (como avaliador, 1440 e 390): a recusa por integridade no painel; *"Baixar"* na barra; a 390
px, abrir, voltar, a nota e o parecer continuam, o retorno à linha do documento; concluir a avaliação
sem abrir documento, aceita.

**Sem script** (desligar o JavaScript): abrir em aba própria, registrar com recarga, como hoje.

**Teclado e leitor de tela** (SC-2149, SC-2159): o percurso 2 a 4 só com Tab, Enter e Espaço, com o
VoiceOver ligado; anotar o que é anunciado em cada passo.
