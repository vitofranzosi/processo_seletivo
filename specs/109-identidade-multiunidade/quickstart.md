# Quickstart: ver a identidade de cada unidade (109)

O cenário demonstrável da spec, pelo canal de cada ator. **Num banco descartável**: o passo 1
registra um campus fictício, e nada se exclui do registro — a unidade não sai mais daquele banco.
Nunca no banco de desenvolvimento compartilhado, nunca em produção.

## 0. O banco descartável

```bash
cd backend
cp .env.example .env   # e troque DB_NAME e POSTGRES_DB por um nome só deste ensaio, ex.: ps_109_ensaio
make preparar
make seed
```

A linha das Unidades deve dizer `Unidades: 1 criadas, 0 alteradas, 0 sem mudança` — o Cefor, como
sempre —, e o `seed` publica os Editais de demonstração do Cefor.

## 1. A TI: o campus entra pelo registro

O comando de sempre lê outro arquivo com `--arquivo`, e o ensaio não precisa tocar no
`unidades.json` versionado. Copie-o para fora do repositório e acrescente o campus à cópia:

```bash
cp processo_seletivo/unidades/unidades.json /tmp/unidades-ensaio.json
```

```json
"campus-a": {
  "sigla": "Campus A",
  "nome": "Campus A",
  "cabecalho": ["Campus A"],
  "local": "Serra (ES)",
  "ativa": true,
  "atendimento": "atendimento@campus-a.example"
}
```

```bash
set -a; . ./.env; set +a
uv run python manage.py sincronizar_unidades --arquivo /tmp/unidades-ensaio.json
```

Ele diz `1 criadas, 0 alteradas, 1 sem mudança` — o campus novo e o Cefor intacto.
Nenhuma linha de código mudou, e o arquivo versionado também não. O banco do ensaio fica com o
campus, e por isso é descartável.

## 2. A operadora do Cefor: a gestão como sempre

Com `INTERFACE_SELETOR_IDENTIDADE=true`, `make runserver`, entre em `/gestao/` pelo seletor de
demonstração. O título termina em "— Cefor/Ifes" e a barra diz "Gestão de Processos Seletivos ·
Cefor/Ifes": o seletor identifica sempre no Cefor, e a unidade ativa é ele.

## 3. O candidato: a moldura da implantação e a do ato

Em `/selecoes/`:

- **com o campus ativo**, a vitrine diz "— Ifes" no título e "Ifes · Gestão de Processos Seletivos"
  na marca: são duas unidades ativas, e a vitrine não escolhe uma;
- a página de uma seleção do Cefor diz "— Cefor/Ifes": é a unidade que o ato gravou;
- de volta ao banco só com o Cefor (ou com `"ativa": false` no campus e o comando de novo), a
  vitrine volta a "— Cefor/Ifes".

O mesmo vale para a página de acesso à gestão e para um endereço que não abre.

## O que os testes cobrem, e este roteiro não

O campus fictício publicando, o PDF dele, as mensagens com o canal do campus e a troca de sigla sem
efeito no publicado estão em `tests/unidades/test_identificacao_multiunidade.py` — publicar no campus
pelo navegador exigiria cadastrar autoridade e atores dele, que o seletor de demonstração não
oferece.
