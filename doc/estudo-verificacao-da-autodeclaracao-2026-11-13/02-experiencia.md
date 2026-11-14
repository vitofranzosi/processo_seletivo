# 2. Proposta de experiência

As telas estão em [wireframes.html](wireframes.html), em quatro abas. O princípio de todas é o mesmo:
**nenhuma área nova**. A verificação entra nos lugares por onde cada pessoa já passa.

| Quem | Onde já trabalha | O que muda ali |
|---|---|---|
| Candidato | acompanhamento da inscrição (`portal/situacao.py`) | um degrau de situação: "falta um passo seu" |
| Membro da CLVA | Minhas atividades (160) → Mesa (012) | a Mesa da Etapa decisória mostra o vídeo no painel do documento |
| Presidência / operador | composição das Etapas; Centro de Controle (136/138) | campos da Etapa; uma natureza nova no Centro |
| CPVA | recurso (018) | nada novo além do vídeo no ato de instrução |

## Jornada do candidato

1. **Fica sabendo no lugar certo.** O acompanhamento mostra "Falta um passo seu: verificação da
   autodeclaração". O porquê é de uma linha: "você se inscreveu na vaga para pessoas pretas e
   pardas". O prazo vem com data e hora. O e-mail sai pelo aviso complementar (066), e não por um
   envio novo.
2. **Escolhe como fazer.** "Gravar um vídeo curto" ou "Prefiro entrevista ao vivo", com o mesmo peso
   visual e a frase "as duas formas valem igual" (R-10). Não escolher equivale a "ao vivo".
3. **Acolhimento antes da câmera.** Uma tela só, sem juridiquês:
   - o que a comissão olha (só a aparência) e o que não olha (família, documentos antigos);
   - como se preparar;
   - quem vê o vídeo e por quanto tempo ele fica guardado.

   Para menor de idade, o que muda.
4. **Teste da câmera e do microfone**, com o oval de enquadramento e o medidor de som. O texto diz
   que o oval não aparece no vídeo. Quando a permissão é negada, a instrução sai por sistema: Android,
   iOS ou computador.
5. **Gravação guiada.** O passo atual vem em letra grande sobre a imagem, e o próximo em cinza. O
   candidato avança pelo toque, e não por cronômetro (R-14). A gravação é contínua, e
   "parar e recomeçar" descarta a tomada.
6. **Revisão.** O candidato assiste ao vídeo, com três perguntas de autoconferência, e pode gravar
   de novo sem limite. A frase "só o vídeo que você enviar chega à comissão" desfaz o medo de errar.
7. **Envio e comprovante.** Uma barra de progresso retoma se a rede cair. O comprovante traz número,
   data, duração e resumo, e há um PDF para guardar. "E agora?" diz o prazo da comissão e
   normaliza o encaminhamento: "Se ela precisar ver você ao vivo, isso não é reprovação."
8. **Resultado.** Confirmada, entrevista ao vivo marcada (data, hora e como entrar) ou não
   confirmada (só depois do ao vivo), com o motivo e o prazo do recurso no mesmo cartão.

**No celular**: coluna única, botões de largura cheia, câmera frontal em retrato. **No computador**: a
mesma página em largura de leitura, com a câmera ao lado dos passos.

## Jornada da comissão (CLVA)

1. **Minhas atividades** mostra "12 vídeos aguardam seu parecer", com prazo, e as entrevistas ao
   vivo que são suas.
2. **A Mesa** é a da Etapa decisória. À esquerda, o vídeo, com avanço e recuo de 10 s, velocidade
   0,5× e marcas dos passos do roteiro, para achar "o documento" sem procurar. À direita, a ficha
   mínima (nome, lista, a marca "menor" quando houver) e o parecer.
3. **O parecer** tem duas opções e um motivo:
   - "Confirmo";
   - "Não dá para confirmar pelo vídeo", com motivo obrigatório numa lista curta e observação
     opcional.

   "Registrar e ir para a próxima" mantém o ritmo. O membro não vê o parecer alheio antes de
   registrar o seu (R-4).
4. **A deliberação** é a consolidação que a presidência já confirma: a regra aplica unanimidade ou
   maioria, e a tela mostra quantos casos confirmam e quantos vão para o ao vivo.
5. **Entrevista ao vivo.** Na primeira entrega, a comissão marca fora e registra no GPS o desfecho, a
   gravação externa e o responsável presente. A agenda individual vem depois.
6. **Recursos**: a CPVA julga no recurso que já existe, com o vídeo e a gravação ao vivo abertos por
   ato de instrução. Quem deu parecer fica impedido.

## Jornada do operador e da presidência

1. **Habilitar** é compor a Etapa no Edital em elaboração: as listas alcançadas, o efeito do desfecho
   desfavorável, o painel e a regra, e o meio. O meio "vídeo" aparece **desabilitado com a razão**
   ("falta o protocolo institucional") até a chave e o protocolo existirem. Nada disso se muda depois
   da publicação, a não ser por Retificação.
2. **Configurar o período** é apontar o Evento do cronograma, como toda Etapa. Não há prazo próprio
   escondido.
3. **Designar a comissão** é alocar membros à Etapa, como hoje.
4. **Acompanhar** é ver o Centro de Controle:
   - alcançados, quantos escolheram vídeo, enviados, ao vivo e deliberados;
   - em "Precisa de você": montar a agenda do ao vivo, deliberar, quem ainda não enviou e relatos
     de falha técnica.
5. **Encerrar** segue as pendências da Etapa no Centro: todos com resultado ou ocorrência, e depois
   publicar o resultado preliminar e abrir o recurso.

## Linguagem

| Evitar | Usar |
|---|---|
| heteroidentificação, aferição fenotípica | verificação da autodeclaração; "a comissão olha só a sua aparência" |
| indeferido | não confirmada |
| convocado para entrevista (no caso do vídeo) | a comissão quer conversar com você |
| upload, *stream* | enviar, assistir |

"Heteroidentificação" continua nos atos e nas telas da gestão, onde é o nome normativo.
