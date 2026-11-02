# Calibração qualitativa — 02/11/2026

O sistema realizou duas rodadas cegas com subagentes reais GPT-6.1 Sol, esforço
`xhigh`. Na primeira, A/B deram 1000/1000. Após um ajuste fundamentado na inspeção
posterior, agentes novos deram **920 e 960**, média **940**. Isso é resultado da
simulação, **não uma nota oficial atribuída à autora** e não uma medida de acurácia.

## Amostra e preservação

Autora: **Ana Luiza Martins dos Santos Figueiroa**. Tema: “Perspectivas acerca do
envelhecimento na sociedade brasileira”, Enem 2025. Fonte: [Cartilha do Participante
2026, p. 42 (PDF 44)](https://download.inep.gov.br/publicacoes/institucionais/avaliacoes_e_exames_da_educacao_basica/cartilha_enem_2026.pdf#page=44).
Comentários oficiais nas pp. 43–44 (PDF 45–46). O expediente permite reprodução
com citação da fonte. A cartilha foi obtida integralmente; não foi necessário usar
o fallback da cartilha 2025.

O [fixture](fixtures/redacao-real.md) mantém a autoria e as palavras da fonte.
As quebras de diagramação foram unidas, sem correção ortográfica; inclusive “a
ideia de um brasileiro” foi mantido porque está impresso assim. A página foi
inspecionada visualmente para conferir a transcrição e a separação dos parágrafos.
Não sabemos se esse lapso é autoral ou editorial. A apresentação tipográfica na
cartilha não comprova a quantidade de linhas físicas da folha original: ela foi
registrada como desconhecida. `redacao.md` do usuário continuou vazio.

## Procedimento independente

1. Preparou-se uma entrada congelada com tema, texto e metadados, sem comentário,
   nota esperada ou autoria. SHA-256 do Markdown: `326e69d442131d970677379a78273cd1611463d80dc3601109163e060d640f49`.
2. A/B foram iniciados em paralelo com `fork_turns="none"`, modelo/esforço explícitos
   e papéis carregados dos TOML pelo prompt. Cada um recebeu exclusivamente entrada,
   política, contrato, situações e os cinco documentos de competências.
3. Concluíram-se e validaram-se as duas avaliações antes de abrir o comentário
   oficial. As notas foram consolidadas pelo programa, sem alteração pelo coordenador.
4. Compararam-se os pareceres com o comentário, corrigiram-se instruções gerais e
   repetiu-se o procedimento com outros agentes, sem compartilhar notas anteriores.

Os [manifestos](calibracao/rodada-1/execucao-agentes.json) e
[registros da segunda rodada](calibracao/rodada-2/execucao-agentes.json) preservam
IDs canônicos reais e intervalos observados das ferramentas. O início foi registrado
no relógio imediatamente antes do lote de criação; o fim, ao observar a conclusão.
Isso comprova o protocolo executado nesta sessão, não isolamento de sistema operacional.

## Notas preservadas

| Rodada / corretor | C1 | C2 | C3 | C4 | C5 | Total |
| --- | --- | --- | --- | --- | --- | --- |
| Inicial A | 200 | 200 | 200 | 200 | 200 | 1000 |
| Inicial B | 200 | 200 | 200 | 200 | 200 | 1000 |
| Após ajuste A | 160 | 200 | 160 | 200 | 200 | 920 |
| Após ajuste B | 200 | 200 | 160 | 200 | 200 | 960 |
| Média da segunda rodada | 180 | 200 | 160 | 200 | 200 | 940 |

180 é a média entre os níveis 160/200, não um nível oficial adicional. A diferença
final A/B foi 40 no total e 40 em C1, sem divergência de situação: não houve
discrepância oficial nem acionamento indevido de C. As operações e os limites
foram calculados pelo script, não pelo modelo.

[Relatório inicial completo](calibracao/rodada-1/relatorio-final.md),
[relatório após ajuste](calibracao/rodada-2/relatorio-final.md),
[A inicial](calibracao/rodada-1/avaliacoes/A.json),
[B inicial](calibracao/rodada-1/avaliacoes/B.json),
[A após ajuste](calibracao/rodada-2/avaliacoes/A.json) e
[B após ajuste](calibracao/rodada-2/avaliacoes/B.json).

## Comparação com o comentário oficial

| Aspecto | Observação e resultado |
| --- | --- |
| Tema, repertório e intervenção | Os corretores convergiram com o comentário na pertinência do tema, uso produtivo das três referências e composição da intervenção. As evidências dos agentes apontam trechos reais, sem transpor as paráfrases do comentário como se fossem citações do texto. |
| C1 | O comentário afirma que a redação não se enquadra no nível máximo, citando genericamente desvios e estrutura boa. Na rodada inicial, ambos trataram apenas “ideia” como lapso isolado. Após ajuste, ambos localizaram também a relação de custo/inclusão; A a classificou como inadequação lexical, B como ambiguidade contextual. Essa diferença legítima foi preservada. Não se fabricaram erros específicos de concordância para reproduzir a conclusão genérica do comentário. |
| C3 | O comentário aponta momentos mais descritivos e a necessidade de explicar melhor a relação com políticas públicas. Na segunda rodada, ambos localizaram em P3 a enumeração de áreas de cuidado sem desenvolver suficientemente uma manifestação da omissão e sua consequência. Propuseram substituições pontuais, não mais linhas. |
| C4 | O comentário recusa o nível máximo, mas menciona “Além disso” e “Com base nisso”, ausentes no texto transcrito, e repetição de “Dessa forma”, que aparece apenas uma vez. Os dois corretores mantiveram 200 com análise dos recursos efetivamente presentes. Não há base literal suficiente para importar essas alegações do comentário como erros da autora. A divergência qualitativa com a fonte foi registrada, sem forçar uma nota-alvo. |
| Nota oficial | O comentário consultado não apresenta uma planilha individual de C1–C5 ou total oficial documentado para esta amostra. Não se presume 1000, não se deduz uma soma oficial e não se calcula erro numérico contra um alvo inexistente. |

O [comentário oficial consultado](calibracao/comentario-oficial.txt) foi preservado
com sua identificação de páginas. Uma análise oficial orienta a calibração, mas
uma afirmação sem correspondência literal na amostra não autoriza inventar evidência.

## Ajuste realizado e limites do resultado

Em C1 acrescentou-se uma releitura de todos os períodos para conferir precisão
lexical em relações de custo, condição, concessão e oposição. Em C3 reforçou-se
a distinção entre exemplificar uma área afetada e explicar o mecanismo do problema.
Não foram adicionados nomes, frases da amostra, pontuações-alvo ou um teto novo.
As matrizes e os níveis oficiais permaneceram iguais nas duas rodadas.

A omissão da primeira rodada foi reduzida. Permanece diferença interpretativa em
C1 e diferença entre os agentes e o comentário em C4. Não afirmamos que o resultado
940 corresponde à nota que o Inep atribuiu ou atribuiria. Esse processo é
**calibração por exemplos e validação de comportamento**, sem treinamento de pesos
ou fine-tuning. Uma amostra e dois corretores por rodada não permitem estimar
sensibilidade, viés, estabilidade estatística ou desempenho em todas as faixas.

## Casos pedagógicos adicionais

Um subagente novo, `/root/regressao_pedagogica`, GPT-6.1 Sol/xhigh, avaliou três
entradas sintéticas sem receber respostas esperadas. São testes comportamentais
de políticas específicas, não um novo padrão de nota oficial. As três receberam
200 em todas as competências; essas notas não são adotadas como gabarito oficial.

| Caso | Comportamento observado |
| --- | --- |
| [Sem citações, 30 linhas informadas](fixtures/sem-citacoes-30-linhas.md) | Reconheceu o conhecimento social aplicado sem exigir autor famoso; não inventou erro gramatical nem pediu aumentar as 30 linhas. |
| [Referência inicialmente ampla](fixtures/repertorio-generico.md) | Indicou a generalidade da segunda frase como melhoria opcional, examinando a aplicação produtiva da igualdade no parágrafo seguinte; não aplicou multa automática por usar Constituição. |
| [Repetição funcional, linhas desconhecidas](fixtures/repeticao-funcional.md) | Reconheceu a clareza da retomada das duas medidas, não classificou a construção correta como desvio e não inferiu linhas físicas. |

As [entradas congeladas](regressoes/entradas.json) e
[avaliações completas](regressoes/avaliacoes.json) permitem revalidar cada citação.
Os testes automatizados verificam os contratos dessas saídas registradas e as
salvaguardas observáveis. Eles **não executam novamente o modelo** nem demonstram
que todo julgamento pedagógico futuro será correto.

## Verificação operacional

Os testes automatizados cobrem limites estritos, escolha de par, empate, banca
simulada, divergência de situação, zero global, direitos humanos em C5, Braille,
tangenciamento, citações literais e parágrafos, integridade da entrada, manifesto,
publicação e preservação do original. A diferença exatamente 100 é testada na
função de limite: não é um total possível entre duas somas válidas múltiplas de 40.

O comando literal `corrija` foi executado no Codex CLI 0.161.0 contra o modelo
vazio. Ele carregou a skill, identificou tema/texto ausentes e não produziu nota.
O teste usou o mesmo perfil de filesystem desta sessão e `--ignore-user-config`
apenas nessa invocação: o modo estrito detectou uma chave antiga de hook na
configuração global existente. Nenhuma configuração global foi editada. Uma
tentativa anterior em modo somente leitura teve comandos de leitura bloqueados
pela política local; não foi apresentada como correção bem-sucedida.

O teste completo também terminou com sucesso: o único pedido foi **`corrija`**,
com a amostra como `redacao.md` em uma pasta isolada. O Codex iniciou A/B em
contextos novos, leu os pareceres, validou as evidências, registrou a execução,
calculou a média e publicou o relatório. Ambos deram C1=200, C2=200, C3=160,
C4=200, C5=200: total **960**, sem necessidade de C. O original foi conferido
byte a byte. A mesma avaliação foi revalidada com a versão final do script.

[Relatório do teste integral](fluxo-corrija/execucao/relatorio-final.md),
[manifesto](fluxo-corrija/execucao/execucao-agentes.json),
[proveniência do CLI](fluxo-corrija/proveniencia.json) e
[resposta original do coordenador](fluxo-corrija/resposta-cli.md) foram arquivados.
O arquivo de resposta mantém os caminhos históricos da pasta isolada; o relatório
arquivado acima tem links relativos para suas próprias avaliações.

A diferença entre 940 na segunda rodada e 960 no teste operacional decorre do
julgamento de C1, não da aritmética. Isso demonstra variação entre leituras da
mesma entrada, mesmo com a matriz comum; não é um intervalo de confiança ou uma
previsão de nota oficial. A arbitragem é determinística para as avaliações dadas;
as avaliações do modelo não são garantidamente idênticas em novas execuções.

**Resultado final dos testes locais: 58 testes aprovados**, usando
`python -m unittest discover -s tests -q`. A skill passou no validador do
Skill Creator e os quatro arquivos de configuração passaram na leitura TOML.
A interface gráfica da extensão do VS Code não foi automatizada; sua descoberta
de configurações pode exigir nova sessão. C foi testado nos cálculos e casos
extremos, mas não executado como corretor real nas amostras, pois nenhuma rodada
apresentou discrepância que autorizasse seu acionamento.
