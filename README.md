# Banca ENEM

Correção pedagógica de redações pelo Codex no VS Code, com dois subagentes
independentes em paralelo, terceiro por discrepância e cálculo determinístico.
Sem interface ou servidor. Critérios da Cartilha do Participante **2026**, obtida
integralmente do Inep. As notas são simulações, sem garantia de coincidência com o exame.

## Usar em três passos

1. Abra esta pasta no Codex e preencha [redacao.md](redacao.md): tema e texto são
   obrigatórios. Separe parágrafos com uma linha em branco. Informe linhas físicas
   somente se as conhecer; não conte as linhas do editor.
2. Envie apenas **`corrija`** no chat. O [AGENTS.md](AGENTS.md) aciona a
   [skill local](.agents/skills/correcao-enem/SKILL.md), que executa A/B em paralelo,
   valida citações, aciona C quando necessário e consolida o resultado.
3. Leia [resultados/relatorio-final.md](resultados/relatorio-final.md). Cada execução
   preserva entrada, avaliações JSON, registro de agentes e decisão em seu diretório.

Python **3.11+**, Codex com subagentes e acesso a `gpt-6.1-sol` são os requisitos.
Nenhuma dependência Python ou chave de API adicional é exigida pelo script. O
modelo/conta do Codex consome os recursos usuais da assinatura. Estimativa de uma
correção: **3–8 minutos** com A/B; **6–15 minutos** com C, variando com a conta e texto.

As definições em `.codex/agents/` seguem a documentação atual. Novos arquivos de
configuração podem exigir uma nova sessão ou recarga da janela do VS Code para
ser descobertos. Com ferramentas genéricas, a skill carrega o papel pelo prompt,
sempre em contexto novo, e registra essa diferença. Não altera configurações globais.

## Repertório de bolso e integridade factual

A banca exige explicar o que a referência sustenta no argumento. Não basta citar
um autor e repetir o tema; uma referência comum pode ser produtiva quando bem
aplicada. Não há lista de autores proibidos nem desconto fixo por "repertório de bolso".

Antes de A/B, o coordenador confere atribuições específicas em fontes externas e
entrega aos corretores a mesma [checagem factual](docs/checagem-repertorios.md),
sem notas. O relatório distingue confirmação, contradição, não localizado e
incerteza. Autor/obra existente não confirma automaticamente o conteúdo atribuído.
Sem pesquisa disponível, a limitação é explícita e não vira acusação de invenção.
Essa etapa pode aumentar o tempo da correção conforme a quantidade de referências.
É salvaguarda local; não se apresenta como pesquisa obrigatória da banca oficial.

## Conferir a implementação

```powershell
python -m unittest discover -s tests -v
python scripts/validar-avaliacoes.py preparar
```

O segundo comando recusa o modelo vazio até que você o preencha. Ele não corrige
sozinho: a análise é feita pelos subagentes reais do Codex. Os comandos
`consolidar --execucao CAMINHO` e `publicar --execucao CAMINHO` cuidam do cálculo e
da geração do relatório, conforme [o fluxo](docs/fluxo-correcao.md).

## Ler os critérios e a validação

1. [Fontes oficiais e versão consultada](docs/fontes-oficiais.md).
2. [Política de correção contextual](docs/politica-correcao.md).
3. [Arbitragem oficial e limites da banca simulada](docs/arbitragem.md).
4. [Calibração qualitativa com uma redação real](tests/relatorio-calibracao.md).

O coordenador não cria uma quarta nota. Se uma banca for necessária com situações
normais, a estimativa local usa medianas por competência, explicitamente identificadas.
Sem par compatível e com situações diferentes, a nota fica pendente para revisão
humana. Não se decide uma anulação pela média. Independência é de contexto/protocolo,
não isolamento do filesystem. Uma única amostra não demonstra precisão geral do sistema.
