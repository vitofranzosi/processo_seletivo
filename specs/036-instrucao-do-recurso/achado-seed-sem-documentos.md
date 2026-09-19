# Achado — `seed_demo` não sustenta a jornada de documento comprobatório

**Encontrado em** 19/09/2026, percorrendo o cenário 3 do quickstart da `036`.

**É registro, e não escopo da feature seguinte.** A governança do projeto é clara, e esta página
existe para que a próxima pessoa não gaste a sessão redescobrindo o mesmo limite.

## O que aconteceu

O cenário 3 pede que a autoridade instrua o recurso com **o parecer atacado e o documento citado**.
A metade do parecer foi percorrida inteira. A do documento não teve como ser: o certame de
`make seed` **não tem documento nenhum**.

```text
documentos no banco semeado: 0
```

E a tela da candidata diz por quê, com todas as letras: *"Esta inscrição não exigiu documentos."* O
Edital semeado não declara Documento Exigido algum, de modo que não há o que anexar à inscrição.

## Por que não dá para contornar pelo caminho certo

**Documento de inscrição enviada não é criado.** A guarda é do modelo desde a `009` —
`DocumentoSubmetido._recusar_se_enviada` — e vale para o resto: um comando de manutenção, um shell,
um caminho que ninguém escreveu ainda. Ela está certa, e não é ela que deveria mudar.

Montar o cenário pelo canal real exigiria um Edital com **documento exigido**, **resultado
publicado** e **prazo recursal aberto** ao mesmo tempo — isto é, compor, publicar, inscrever com
anexo, avaliar, consolidar, emitir e divulgar um certame inteiro à mão. É percurso de horas para
exercitar a segunda espécie de um ato cuja primeira já foi percorrida.

## O que alcança mais do que a `036`

O limite não é da instrução: é do **cenário semeado**. Qualquer feature que precise percorrer a
jornada do documento comprobatório — conferir o que o candidato entregou, recusar por documento
ilegível, comparar o apresentado com o exigido — esbarra no mesmo lugar. A `seed_demo` semeia
inscrições, avaliações, resultados, sorteio, convocação e matrícula, e **não** semeia o anexo que a
`009` existe para receber.

## O que cobre o que o percurso não cobriu

Quatro casos em `backend/tests/interface/test_instrucao_na_peca.py`:

- quem só julga **alcança** o documento instruído, e o arquivo abre;
- a tela de documentos da inscrição **continua recusando** o mesmo ator;
- instruir **não duplica** arquivo no armazenamento;
- abrir o documento instruído **também não duplica**.

E dois em `backend/tests/integration/recursos/test_alcance_da_instrucao.py`: o ato referencia o
documento original, e não se instrui documento de outra pessoa — nem pela aplicação, nem por
gravação direta.
