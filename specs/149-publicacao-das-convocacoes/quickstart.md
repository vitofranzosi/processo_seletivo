# Quickstart: A publicação das convocações no GPS (149)

## Para a comissão

1. Convoque como sempre, na tela da convocação de cada vaga e lista (titulares num ato só, chamada
   individual, regularização). Nada muda até aqui.
2. Na seção das comunicações pendentes de um Perfil *por publicação*, siga **Publicar no GPS**. Ou,
   da página do Edital, abra `/gestao/editais/<edital>/convocacoes/publicacao`.
3. Confira a prévia: quantas pessoas, de quais vagas e listas, quem ficou de fora e por quê, e o que
   será público. Desmarque as vagas e listas que não entram agora e atualize a prévia. **Nada é
   gravado até o botão.**
4. Escolha a autoridade signatária e, se a publicação convoca alguém, diga onde o Edital admite a
   página do GPS como veículo (por exemplo, *"item 7.2 do Edital"*). Publique.
5. A confirmação leva à página pública e ao documento. O prazo de quem a publicação convocou corre
   do instante dela, e cada candidato já vê a sua convocação.

O Edital manda publicar em outro lugar? Publique lá e use **Publicada fora do GPS?** na mesma seção,
como antes. Depois, se quiser, a publicação do GPS divulga a relação como espelho informativo, sem
mexer no prazo de ninguém.

**Corrigiu uma convocação já publicada?** A correção (`120`) espera publicação própria: a próxima
publicação a leva, marcada *"corrige a convocação divulgada na Nª publicação"*, e a anterior passa a
avisar a correção na página — o documento dela não muda.

## Para quem consulta

A página pública da seleção ganha a seção **Convocações** quando há publicação. Cada uma tem página
própria (`/selecoes/convocacoes/<id>/`), sem login, e o documento oficial
(`…/documento.pdf`). As providências individuais continuam em **Minhas inscrições**.

## Demonstração local

De `backend/`, num banco novo:

```bash
createdb ps148demo
```

```bash
DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps148demo DB_USER=$USER DB_RUNTIME_USER=$USER uv run python manage.py migrate
```

```bash
DJANGO_SETTINGS_MODULE=config.settings.development DB_NAME=ps148demo DB_USER=$USER DB_RUNTIME_USER=$USER DJANGO_ALLOWED_HOSTS=localhost,testserver ARQUIVOS_CANDIDATOS_RAIZ=/tmp/ps148demo uv run python manage.py shell < ../specs/149-publicacao-das-convocacoes/demonstracao/montar.py
```

O script imprime o identificador do Edital. Suba o servidor com `INTERFACE_SELETOR_IDENTIDADE=true`
e entre na gestão como **Gestor** (`carlos`).

## Verificação

```bash
cd backend && make lint check test-pg
```

O `provisionar_papeis` passa a proteger **58** tabelas append-only (eram 55): a segunda passada do
`make preparar` precisa rodar depois da migration `convocacao/0007`.
