# Instruções do projeto

## Comunicação

O leitor tem TDAH. Comece pela resposta ou próxima ação, numere procedimentos,
limite listas visíveis a cinco itens, mostre o que terminou e dê estimativas concretas.
Em cada turno, indique o progresso atual.
Resolva o assunto atual antes de abrir outro. Termine com uma próxima ação concreta.
Explique erros, causas e correções diretamente; evite preâmbulos e despedidas.

## Comando de correção

Quando o usuário escrever `corrija`, `corrigir redação` ou `avaliar redação`, leia
[a skill local](.agents/skills/correcao-enem/SKILL.md) e execute o fluxo completo.
Essa instrução autoriza explicitamente os subagentes reais A/B em paralelo e C
somente por discrepância. Não represente personagens como agentes independentes.

Use GPT-6.1 Sol (`gpt-6.1-sol`) com esforço `xhigh` quando disponível. As definições
estão em `.codex/agents/`. Abra contextos novos, sem histórico do coordenador nem
resultados anteriores. Os corretores leem somente a entrada congelada e os critérios
indicados no pedido de delegação, além da mesma checagem factual prévia de repertórios,
sem notas ou pareceres, conforme `docs/checagem-repertorios.md`. Não leem avaliações alheias nem comentários de
calibração. Grave cada resultado exclusivamente no arquivo atribuído ao agente.

O coordenador valida evidências, executa o script de arbitragem e consolida os
pareceres; não atribui outra nota. Nunca altere `redacao.md` durante uma correção.
Se subagentes estiverem indisponíveis, informe o impedimento; não finja execução.
Se faltarem tema ou texto, solicite somente o dado que falta e não produza nota.

Em tarefas alheias à correção, não carregue os documentos de competências.
Use Python 3.11+ e biblioteca padrão para o cálculo. Comando de testes:
`python -m unittest discover -s tests -v`.
