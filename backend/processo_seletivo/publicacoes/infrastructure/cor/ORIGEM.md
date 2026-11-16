# Origem do perfil de cor dos documentos em PDF/A

Todo documento que o GPS compõe em PDF/A (178, FR-8156) declara como condição de saída o espaço
**sRGB**, com o perfil ICC deste diretório embutido no arquivo. É a peça que a ISO 19005-2 cobra de
quem desenha em `DeviceRGB` ou `DeviceGray` — o brasão, as cores dos relatórios, o cinza das molduras.

## De onde veio

| | |
|---|---|
| Autor e titular | International Color Consortium (ICC) |
| Perfil | `sRGB2014.icc` — sRGB IEC 61966-2.1, versão de fevereiro de 2015 do ponto preto |
| Página | <https://registry.color.org/rgb-registry/srgbprofiles> |
| Endereço do arquivo | <https://registry.color.org/rgb-registry/profiles/sRGB2014.icc> |
| SHA-256 | `384b832de3412066743b52a75ee906b6fb9fb8d9e09e936fc2c43223815c6e0a` |
| Bytes | 3024 |
| Cabeçalho | ICC v2.0, classe `mntr` (monitor), espaço `RGB `, PCS `XYZ ` |
| Copyright no arquivo (`cprt`) | *Copyright International Color Consortium, 2015* |
| Baixado em | 16/11/2026, na implementação da `178` |

O teste `tests/unit/publicacoes/test_conformidade_pdfa.py` confere o resumo.

## A licença, verificada na fonte

A página de licenciamento da biblioteca de perfis do ICC
(<https://registry.color.org/profile-library/#license>) diz que, onde o ICC é o titular — e o
`cprt` do arquivo diz que é —, valem estes termos, transcritos em `LICENSE`:

> *This profile is made available by the International Color Consortium, and may be copied,
> distributed, embedded, made, used, and sold without restriction. Altered versions of this profile
> shall have the original identification and copyright information removed and shall not be
> misrepresented as the original profile.*

O GPS embute o perfil **inalterado**, que é o que a licença permite sem condição.

## Por que este perfil

- **É o sRGB de referência**, do próprio consórcio que mantém o formato ICC: um documento de vinte
  anos atrás não deve depender de um perfil de terceiro que deixou de existir.
- **É ICC v2.** A ISO 19005-2 aceita v2 e v4, e o v2 é o que todo leitor e todo validador entende. O
  `sRGB_v4_ICC_preference.icc` da mesma página é de outra natureza (intenção perceptual, 60 KB).
- **Licença explícita para redistribuição**, o que o perfil da prova de conceito, que veio com o
  Ghostscript, não tinha escrito.

## Para trocar

Só com outro perfil sRGB de licença explícita, registrado aqui com origem e resumo. Os bytes de todo
documento composto depois mudam; os gravados antes não.
