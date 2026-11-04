# Contrato dos arquivos de avaliação

Cada corretor grava um objeto JSON UTF-8 no próprio caminho informado pelo
coordenador. Não use cercas Markdown. Não calcule a nota total: o programa soma.
Campos obrigatórios e tipos aparecem abaixo. Campos textuais não podem estar vazios.

```json
{
  "corretor": "A",
  "entrada_sha256": "copiar de entrada.json",
  "checagem_sha256": "SHA-256 do arquivo factual recebido, informado pelo coordenador",
  "situacao": {
    "codigo": "normal",
    "justificativa": "Por que esta situação corresponde ao texto.",
    "evidencias": [{"paragrafo": 1, "trecho": "trecho literal", "analise": "Relação com a situação."}]
  },
  "tema": {
    "atendimento": "integral",
    "justificativa": "Relação do texto com os elementos da frase temática.",
    "evidencias": [{"paragrafo": 1, "trecho": "trecho literal", "analise": "Relação temática."}]
  },
  "competencias": {
    "C1": {
      "nota": 160,
      "justificativa": "Conjunto de evidências que sustenta o nível oficial.",
      "evidencias": [{"paragrafo": 1, "trecho": "trecho literal", "analise": "O que demonstra."}],
      "proximo_nivel": "Mudança concreta que falta; em 200, informar que não há nível superior."
    }
  },
  "parecer": "Qualidade geral, méritos e limites coerentes com a matriz.",
  "acertos": ["Mérito demonstrado e sua localização."],
  "paragrafos": [{
    "paragrafo": 1,
    "funcao": "Função realmente cumprida na estrutura do texto.",
    "parecer": "Diagnóstico contextualizado.",
    "evidencias": [{"paragrafo": 1, "trecho": "trecho literal", "analise": "Justificativa."}]
  }],
  "problemas": [{
    "tipo": "erro_avaliavel",
    "paragrafo": 1,
    "trecho": "trecho literal",
    "competencia": "C1",
    "diagnostico": "Regra ou descritor e falha comprovada.",
    "impacto": "Consequência real para o texto.",
    "sugestao": "Mudança concreta, preferindo substituir a ampliar.",
    "reformulacao": "Alternativa facultativa; pode ser null."
  }],
  "repertorios": [{
    "paragrafo": 1,
    "trecho": "trecho literal",
    "referencia": "Identificação do conhecimento utilizado.",
    "legitimidade": "Análise fundamentada, com incertezas explicitadas.",
    "pertinencia": "Relação com o recorte temático.",
    "produtividade": "Contribuição efetiva ao argumento ou ligação que falta.",
    "verificacao": "nao_verificado",
    "fonte_url": null
  }],
  "intervencao": {
    "acao": {"paragrafo": 1, "trecho": "trecho literal", "analise": "Ação propositiva."},
    "agente": null,
    "meio": null,
    "efeito": null,
    "detalhamento": null,
    "direitos_humanos": "respeitados",
    "justificativa": "Composição, vínculo ao problema e limites."
  },
  "prioridades": [{
    "foco": "Problema prioritário localizado ou habilidade a consolidar.",
    "exercicio": "Atividade específica.",
    "criterio_sucesso": "Como reconhecer que melhorou."
  }],
  "limitacoes": ["Linhas físicas desconhecidas, se for o caso."]
}
```

O exemplo mostra apenas C1; uma avaliação `normal` precisa de **C1, C2, C3, C4 e
C5**, todas completas, com notas inteiras em {0,40,80,120,160,200}. C2 zero exige
situação global correspondente. Não copie os trechos de exemplo: use a entrada.
O SHA identifica o arquivo de entrada congelado, não a versão atual de `redacao.md`.

`situacao.codigo`: `normal`, `fuga_tema`, `tipo_textual`, `em_branco`,
`texto_insuficiente` ou `anulada`, conforme [situações](situacoes-avaliacao.md).
Em zero global, `competencias` fica `{}`; o script registra total zero e competências
não avaliadas. As demais análises permanecem possíveis como diagnóstico pedagógico,
sem gerar cinco notas fictícias. Evidências podem ficar vazias somente para
`em_branco`, cuja entrada deve estar efetivamente vazia.

`acertos` deve identificar méritos reais. Pode ficar vazio em zero global quando
não houver mérito demonstrável; nunca invente um acerto para completar o contrato.

`tema.atendimento`: `integral`, `tangenciamento`, `fuga` ou `nao_avaliavel`.
`fuga` exige `fuga_tema`; `nao_avaliavel` só cabe em situação de zero global que
impeça essa análise, não para contornar tema ausente. Tangenciamento em situação
normal obriga notas até 40 em C2/C3/C5.

`problemas.tipo`: `erro_avaliavel`, `oportunidade_melhoria` ou `ambiguidade`.
Só `erro_avaliavel` fundamenta uma falha demonstrada. A lista pode estar vazia:
não invente erro para preenchê-la. A lista de repertórios também pode estar vazia;
ausência de citação não é automaticamente ausência de conhecimento mobilizado.
`verificacao` aceita `nao_verificado` ou `verificado`; o segundo exige URL e
checagem conclusiva no registro factual comum, com parágrafo e trecho idênticos e
a URL correspondente. Verificado não é sinônimo de verdadeiro: o resultado factual
pode ser `confirmado` ou `contradito`. Nos resultados não localizado, inconclusivo
ou não verificado, use `nao_verificado` e explicite o limite em `legitimidade`.
O registro é produzido pelo coordenador antes da delegação; o agente não pesquisa
a redação nem cria fontes. Durante calibração cega, não busque a amostra.

`checagem_sha256` é obrigatório quando a execução contém o registro factual. Copie
o hash informado e leia esse arquivo antes de avaliar. A consolidação confirma o
hash de todos os agentes; não altere o registro nem escreva um hash novo para
contornar a divergência. Execuções legadas sem registro não exigem esse campo.
Siga a [política](politica-correcao.md) para distinguir uso ornamental, desconhecido
e contradição factual; nenhum rótulo gera desconto fixo ou anulação automática.

`intervencao.direitos_humanos`: `respeitados`, `violados` ou `nao_avaliavel`.
`violados` exige evidência da proposta e zero em C5 em situação normal. Elementos
inexistentes são `null`. Não complete os elementos por inferência ou juntando
propostas diferentes. A nota se justifica pelo descritor, não só por contagem.

Inclua todos os parágrafos reais uma única vez, numerados a partir de 1. Cada
evidência deve ser um trecho literal, com espaços, pontuação e acentos preservados,
contido **no parágrafo indicado**; citar palavras de outro parágrafo é inválido.
Escolha trechos contínuos curtos, evitando atravessar uma quebra de linha quando
não for necessário. Reformulações não são evidências e não precisam existir no original.

`prioridades`: de uma a três; se o texto já atende ao nível máximo, proponha prática
de consolidação e identifique-a como tal. `limitacoes` pode estar vazia, exceto
quando linhas ou motivadores forem desconhecidos/ausentes; declare esses limites.
Não inclua identidade de subagente ou horário inventado no JSON. O coordenador
registra IDs, modelo efetivo e execução real separadamente em `execucao-agentes.json`.
