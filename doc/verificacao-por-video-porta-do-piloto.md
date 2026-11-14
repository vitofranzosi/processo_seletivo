# A porta do piloto da verificação por vídeo (166, FR-7153)

**O que é.** A spec `166` entregou a camada B do estudo da verificação da autodeclaração
(`doc/estudo-verificacao-da-autodeclaracao-2026-11-13/`, PR #541): o vídeo gravado pelo candidato,
opcional, que **só confirma**. Ela roda só em desenvolvimento, atrás da chave `VERIFICACAO_POR_VIDEO`,
e as settings de produção **recusam subir** com a chave ligada (`config/settings/production.py`).

**Esta página descreve a porta, e não a abre.** Nenhum dos passos abaixo foi dado, e a P-0 continua
aberta.

## Por que a porta está fechada

Nenhuma norma do Ifes autoriza hoje o vídeo assíncrono:

- a Res. CS 61/2019 prevê entrevista presencial e gravada;
- o Ato 12/2020 abriu a videoconferência, em caráter excepcional e preso à pandemia;
- o Ofício MEC 3/2025 pede, fora do presencial, entrevista **síncrona**.

## Os passos, nesta ordem

1. **O ato do Conselho Superior** que altere a Res. CS 61/2019 para admitir o vídeo como meio
   opcional que só confirma (P-0). É da instituição, e não do sistema.
2. **O protocolo da CPVA**, com:
   - o roteiro (P-8): o documento no vídeo, o CPF não falado, a Libras ou o cartão escrito;
   - o menor de idade (P-7): a recomendação do estudo é o vídeo indisponível, que é o que o sistema
     faz hoje pela declaração do candidato;
   - a guarda do vídeo (P-10): o prazo de retenção e o marco da contagem, com o arquivo institucional
     e o encarregado de dados.
3. **A matriz de navegadores com câmera real** (SC-2377, critério de saída da entrega 0 do estudo):
   Chrome e Firefox no computador, Chrome no Android e Safari no iOS, gravados por **uma pessoa da
   equipe gravando a si mesma**, e nunca por um candidato. O que não for viável vira restrição escrita
   do piloto.
4. **O Edital que cite o protocolo**, com a Etapa decisória colegiada, de alcance declarado e
   período, marcando "Admite vídeo gravado pelo candidato".
5. **Só então, um PR revisado** que:
   - troque a recusa de `production.py` por uma liberação **para aquele Edital**, e não para todos
     (por exemplo, uma lista de identidades de Edital, recusando qualquer outra);
   - defina `VERIFICACAO_POR_VIDEO_RETENCAO_DIAS` com o prazo decidido na P-10;
   - registre, aqui, o ato, o protocolo e o Edital, com datas.

O merge desse PR é do usuário, como todo merge deste repositório.

## O que a chave libera, e o que não libera

| Libera | Não libera |
|---|---|
| a página de gravação e as rotas de envio no portal | nenhuma análise automática do vídeo (FR-7150) |
| o campo "Admite vídeo" na composição | o vídeo como único caminho (FR-7108) |
| a publicação de Edital que admite o vídeo | o Resultado desfavorável pelo vídeo (FR-7139) |

**A chave não fecha a Mesa** (achado I1 da spec): desligada depois de vídeos recebidos, a comissão
continua os assistindo e deliberando, e a R-11 continua valendo.

## O que fica de fora mesmo com a porta aberta

Está registrado na spec, em *Out of Scope* e *Achados*:

- a orientação da entrega 4: o degrau no acompanhamento, a natureza no Centro e o aviso por e-mail;
- a agenda individual da entrevista ao vivo;
- o vídeo na instrução do recurso.
