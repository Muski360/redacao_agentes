---
name: correcao-enem
description: Corrigir uma redação do ENEM com avaliadores independentes, critérios do Inep e arbitragem determinística quando o usuário pedir corrija, corrigir redação ou avaliar redação.
---

# Correção ENEM

Execute no projeto que contém `redacao.md`; caminhos relativos abaixo partem da
raiz do projeto, três diretórios acima da pasta desta skill. Não altere o original.

1. Leia `redacao.md` e execute `python scripts/validar-avaliacoes.py preparar`.
   Se faltar tema ou texto, peça a informação ausente e não atribua nota. Use o
   diretório de execução retornado pelo comando; ele contém a entrada congelada.
2. Leia [o fluxo](../../../docs/fluxo-correcao.md), [a política](../../../docs/politica-correcao.md),
   [o contrato JSON](../../../docs/contrato-avaliacao.md) e os critérios ali indicados.
   Confira a versão das fontes; não invente atualização oficial.
3. Inicie subagentes reais A e B simultâneos e sem histórico compartilhado, usando
   `.codex/agents/corretor-a.toml` e `corretor-b.toml`. Envie apenas caminhos da
   entrada congelada, critérios e arquivo exclusivo de saída. Registre os IDs reais.
4. Espere ambos terminarem. Execute `consolidar --execucao CAMINHO`. Se o script
   retornar `aguardando_c`, inicie C em contexto novo com `corretor-c.toml`, somente
   entrada e critérios. Valide novamente. Não forneça notas A/B a C.
5. Execute `publicar --execucao CAMINHO` depois de registrar a execução real e conferir
   o relatório. Apresente nota, três prioridades e links dos arquivos. Caso haja
   pendência de situação, apresente a pendência sem inventar uma nota final.

O coordenador não corrige como quarto avaliador. O script calcula tudo. Sem
subagentes disponíveis, pare com explicação explícita. Consulte
[arbitragem](../../../docs/arbitragem.md) para a simulação de banca e suas limitações.
