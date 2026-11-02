# Fontes oficiais e versão dos critérios

Pesquisa realizada em **02/11/2026**, data de São Paulo. Este é um retrato das
fontes consultadas; o sistema não afirma acompanhar automaticamente futuras erratas.

## Fonte principal: Cartilha do Participante 2026

[Página oficial correta](https://www.gov.br/inep/pt-br/centrais-de-conteudo/acervo-linha-editorial/publicacoes-institucionais/avaliacoes-e-exames-da-educacao-basica/a-redacao-do-enem-2026-cartilha-do-a-participante)
e [PDF integral](https://download.inep.gov.br/publicacoes/institucionais/avaliacoes_e_exames_da_educacao_basica/cartilha_enem_2026.pdf).
Publicação: setembro de 2026. Acesso integral realizado por download local; o
visualizador de pesquisa retornou 502 para o PDF, mas o download HTTPS funcionou.
O endereço originalmente fornecido usa `educacao_basica` no caminho da página e
retorna 404; a página correta usa `educacao-basica`.

Cópia verificável: [cartilha-enem-2026.pdf](fontes/cartilha-enem-2026.pdf), 82 páginas.
SHA-256: `5708d8df9a3b0046cbf3d835e023f9eb89be08d295cb01ce5afeac77496211ad`.
As páginas citadas nos documentos são as **impressas**; neste PDF, some 2 para
obter a página do visualizador. Os descritores foram extraídos do PDF, normalizando
somente espaços e quebras de diagramação. A publicação permite reprodução total
ou parcial mediante citação da fonte (expediente, PDF p. 4).

| Regra/conteúdo | Páginas impressas | Aplicação no projeto |
| --- | --- | --- |
| Dupla leitura independente e matriz | 5–6 | Perfis A/B e cinco competências |
| Soma, média, discrepância >100/>80 e terceiro/banca | 6–7 | Script e arbitragem |
| Zero global, cópia, partes desconectadas, título e adaptações | 7–10 | Situações e política |
| C1 e seus seis níveis | 12–14 | competencia-1.md |
| C2, repertório de bolso e seis níveis | 14–27, sobretudo 16 e 27 | competencia-2.md |
| Tangenciamento: teto 40 em C2/C3/C5 | 25 | Validação cruzada das notas |
| C3 e seis níveis | 28–31 | competencia-3.md |
| C4 e seis níveis, uso funcional dos conectivos | 31–34 | competencia-4.md |
| C5, ação versus constatação, direitos humanos e seis níveis | 35–38 | competencia-5.md |
| Amostra do Enem 2025 e comentários | 41–75 | Calibração qualitativa cega |

## Complemento operacional: FAQ do Inep

[Perguntas frequentes do Enem](https://www.gov.br/inep/pt-br/acesso-a-informacao/perguntas-frequentes/exame-nacional-do-ensino-medio-enem),
seções “Cálculo da nota da redação” e “Casos em que a redação poderá ter nota zero”.
Página corrente consultada em 2026, não um manual anual de 2026. Fundamenta
divergência de situação, seleção do par compatível, equidistância do terceiro e
encaminhamento à banca. A cartilha resume a terceira leitura; a FAQ detalha os casos.
Não há desempate oficial por escolher automaticamente a maior ou a menor nota.

## Manuais complementares por competência

Localizados pelo [índice oficial de documentos](https://www.gov.br/inep/pt-br/areas-de-atuacao/avaliacao-e-exames-educacionais/enem/outros-documentos).
Foram baixados para consulta técnica. Os arquivos estão em diretório **2020**;
isso não prova ano de edição interno. Há referências de aplicação de 2019 em
C2–C5; por isso não os rotulamos como matriz nova de 2026. Não são necessários
para executar o sistema nem prevalecem sobre a cartilha atual.

| Arquivo oficial | Uso complementar | SHA-256 do download |
| --- | --- | --- |
| [Competência 1](https://download.inep.gov.br/educacao_basica/enem/downloads/2020/Competencia_1.pdf) | Categorias de desvios e estrutura sintática | 3e7f30eae71bab5fa8b3716d51c7b6b94d5855b8eb4bf072367766d1943bea5b |
| [Competência 2](https://download.inep.gov.br/educacao_basica/enem/downloads/2020/Competencia_2.pdf) | Tema, estrutura e repertório | 62b9d4f3b766455d04c4f2032703c7094bf63a1f2ff99222429635e920c90e5c |
| [Competência 3](https://download.inep.gov.br/educacao_basica/enem/downloads/2020/Competencia_3.pdf) | Projeto e desenvolvimento das ideias | d8af8f30f1141aee5b3b9fc380bad2b953993a74992575df2776749dad2399c6 |
| [Competência 4](https://download.inep.gov.br/educacao_basica/enem/downloads/2020/Competencia_4.pdf) | Coesão e inadequações | 83281f7ebab10f7f00c1f5cbaf9d14ff7b47e8c208b1597b81befe443c5bba55 |
| [Competência 5](https://download.inep.gov.br/educacao_basica/enem/downloads/2020/Competencia_5.pdf) | Composição e validade dos elementos interventivos | 362b401f8628716c38bf0d282b926441a1968da03df1ec4cb512750f5b54742e |

Regras particulares dos manuais antigos não confirmadas na edição atual não são
promovidas a novas regras oficiais de 2026. Por exemplo, não se cria desconto
automático por uma forma verbal isolada sem análise da proposta no contexto.

## Referência complementar de 2025

[Cartilha 2025 indicada no pedido](https://download.inep.gov.br/publicacoes/institucionais/avaliacoes_e_exames_da_educacao_basica/a_redacao_no_enem_2025_cartilha_do_participante.pdf).
O acesso retornou erro de rede; não alegamos leitura integral dessa URL nem usamos
suas amostras. A cartilha de 2026 foi obtida integralmente e tornou desnecessário
o fallback para Ana Clara Pereira. A amostra escolhida é de **Ana Luiza Martins dos
Santos Figueiroa**, Enem 2025, p. 42; comentário oficial nas pp. 43–44.
Nenhuma nota oficial é presumida por a redação estar publicada na cartilha.

## Configuração do Codex

[OpenAI: subagentes e agentes personalizados](https://learn.chatgpt.com/docs/agent-configuration/subagents)
e [referência de configuração](https://learn.chatgpt.com/docs/config-file/config-reference),
consultadas na mesma data. Fundamentam arquivos TOML autônomos com `name`,
`description` e `developer_instructions`, seleção de modelo/esforço por papel e
configuração de projeto em `.codex/`. [Modelo GPT-6.1 Sol](https://developers.openai.com/api/docs/models/gpt-6.1-sol)
fundamenta o identificador `gpt-6.1-sol` e esforço `xhigh`, condicionados ao acesso
efetivo da conta. A configuração global do usuário não foi alterada.

## Regras oficiais versus escolhas locais

São oficiais os descritores, os seis níveis, as condições verificadas de zero,
os limites de discrepância, a média e o encaminhamento à banca. São escolhas
pedagógicas locais o formato JSON, as seções A–J, a seleção de três prioridades,
as salvaguardas de feedback e a estimativa por medianas em banca simulada.
Limitações técnicas não são apresentadas como regras do Inep.
