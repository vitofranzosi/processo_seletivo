# Estudo: verificação da autodeclaração, com vídeo opcional (2026-11-13)

**Pergunta.** O GPS pode ter um módulo opcional de verificação da autodeclaração de pretos e pardos,
com gravação assíncrona de vídeo pelo candidato, que reduza o esforço das entrevistas sem perder a
avaliação humana, a segurança jurídica e as garantias do candidato?

**Resposta curta.** O vídeo pode vir, mas **não primeiro**, e não sem autorização.

1. **O GPS não tem heteroidentificação.** Ela acontece fora do sistema, por videoconferência na RNP
   ou presencialmente, e o GPS só recebe a autodeclaração como documento. Um módulo de vídeo
   construído agora seria a estrutura paralela que o pedido proíbe: pareceres que nenhum Resultado
   de Etapa lê, decisões que nenhuma lista obedece.
2. **Nenhuma norma do Ifes autoriza o vídeo assíncrono.**
   - A Res. CS 61/2019 prevê entrevista presencial e gravada.
   - O Ato 12/2020 abriu a videoconferência, em caráter excepcional e preso à pandemia.
   - O Ato 15/2021, "a alteração de 2021", mexe só na composição da CLVA.
   - O Ofício MEC 3/2025 pede, fora do presencial, entrevista **síncrona**.
3. **Por isso, duas camadas.**
   - **Camada A**: o rito que o Ifes já pratica, dentro do GPS: Etapa só para quem declarou a
     Modalidade, pareceres às cegas, deliberação pela regra do Edital, "fica na ampla", recurso à
     CPVA. Ela não depende de norma nova, e já reduz trabalho: listas, resultados, avisos e
     publicação deixam de ser planilha.
   - **Camada B**: o vídeo como **opção do candidato que só confirma**, no modelo da UFC. Quem não é
     confirmado pelo vídeo vai à entrevista ao vivo e não perde nada. Fica atrás de uma chave
     recusada em produção até haver ato do Conselho Superior, protocolo da CPVA e Edital que o
     cite.

**O que o estudo não fez.** Não ativou nada, não processou vídeo real e não tocou Edital publicado.

> **A prova de conceito (13/11, depois do aceite).** Está em [poc/](poc/README.md): uma página
> estática, sob a mesma CSP do GPS, com imagem de teste sintética e nada saindo do aparelho.
> Percorre gravação guiada, revisão, regravação, envio em partes com retomada e SHA-256, comprovante,
> Mesa com abertura registrada, parecer às cegas e as três regras. Foram 17 verificações no Chromium
> do painel, e seis achados. Os três que mudam a entrega 5:
> - a exceção de CSP é **uma linha**, `media-src 'self' blob:`, e se provou necessária e
>   suficiente;
> - o MP4 no topo da lista **unifica** o formato entre Chrome e Safari;
> - a interrupção por tela oculta é estrita e precisa de medida em celular real.
>
> Falta a matriz com câmera real em quatro navegadores, o critério de saída da entrega 0. Ela pede
> aparelho e uma pessoa gravando a si mesma, e não um candidato.

## Entregas

1. [Diagnóstico técnico e normativo](01-diagnostico.md):
   - o que o GPS tem, com arquivo e linha;
   - as normas do Ifes e as federais, com fonte;
   - pretos e pardos × indígenas;
   - o que pede norma e o que é infraestrutura;
   - UFC × IFPE × Ifes;
   - as 13 pendências P-0 a P-12.
2. [Proposta de experiência](02-experiencia.md): as três jornadas e a linguagem.
   [Wireframes](wireframes.html) das telas reais, em quatro abas: candidato no celular, comissão,
   operador e recurso.
3. [Especificação funcional enxuta](03-especificacao.md): regras R-1 a R-24, estados, o que
   reaproveita e o que é novo, e o que fica fora de propósito.
4. [Plano de entregas](04-plano-de-entregas.md): 0 a 8, cada uma verificável, com os riscos
   técnicos já visíveis no código.
5. [Prova de conceito](poc/README.md): construída e verificada no Chromium com imagem sintética;
   a matriz com câmera real está aberta.

## Pontos de integração

Nenhuma área nova. A verificação entra onde cada pessoa já trabalha.

| Peça do GPS | Papel na verificação |
|---|---|
| `EtapaAvaliacao` decisória (012) | a própria Etapa de verificação; ganha **alcance por Modalidade** (L-2) e **efeito por lista** |
| `AlocacaoEtapa` | a CLVA é a alocação dos membros à Etapa |
| `Avaliacao` e consolidação | parecer por membro; ganha a **regra de combinação** decisória |
| Ocorrência | ausência |
| Recurso, julgador, impedimento, instrução (018) | recurso à CPVA, com o vídeo aberto por instrução |
| `situacao_da_inscricao` | o degrau "falta um passo seu" no acompanhamento |
| `andamento.py`, Centro, Minhas atividades (136, 160) | uma natureza: "verificação da autodeclaração" |
| `ArmazenamentoPrivado`, `portal/arquivos.py`, trilha | o vídeo guardado, entregue e registrado; ganha formato de vídeo, `Range` e envio em partes |
| Avisos complementares (066) | e-mail do resultado e do encaminhamento |
| `DocumentoExigido` e conferência (115) | indígenas: análise documental, **sem nada novo** |
| `_exigir` em `production.py` | a chave `VERIFICACAO_POR_VIDEO`, recusada em produção |

## Decisões pendentes

Do usuário e das instâncias do Ifes. O detalhe e os fatos de cada uma estão no
[diagnóstico, §7](01-diagnostico.md#7-lacunas-e-dúvidas-normativas).

**Para começar a camada A:**
- **P-1**: aceitar a L-2, a Etapa por Modalidade. Decide a família "heteroidentificação" da DP-10.
- **P-2**: o "não confirmada" fica na ampla ou elimina? A recomendação é declarar no Edital, com
  padrão "fica na ampla".
- **P-3**: qual das três leituras de deliberação vale. Pede consulta à CPVA sobre o art. 15, III, b.

**Para a camada B existir fora do desenvolvimento:**
- **P-0**: o ato que autoriza o vídeo. Alteração da Res. 61 pelo CS, protocolo da CPVA e Edital.
- **P-7**: menor de idade. A recomendação é o vídeo indisponível para ele.
- **P-8**: o roteiro. Documento no vídeo, CPF não falado, Libras.
- **P-10**: a guarda do vídeo. Nenhuma tabela a define; pede consulta ao arquivo institucional e ao
  encarregado de dados.

**Que podem esperar:** P-4 (composição), P-5 (recurso colegiado e síncrono), P-6 (ausência), P-9
(sigilo) e P-11 (exposição na lista pública).

**Achado fora do escopo:** **P-12**. A videoconferência que os Editais usam hoje se apoia no Ato
12/2020, condicionado à suspensão das aulas presenciais, e a homologação dele não foi localizada. O
Edital 28/2026 ainda a justifica pela pandemia. Registrado para a CPVA, e não tratado aqui.

## Próximo passo proposto

1. **Fechar a entrega 0**: preencher a [matriz](poc/README.md#matriz-de-navegadores) com câmera
   real no Chrome, no Firefox, no Android e no iOS.
2. Com P-1 a P-3 decididas, a camada A vira specs pelo `/speckit-specify`, uma por sessão. Ela vale
   mesmo que o vídeo nunca seja autorizado.
