# Execução pelo Codex

## Preparar a entrada

Na raiz do projeto, `python scripts/validar-avaliacoes.py preparar` lê `redacao.md`,
recusa tema/texto vazios e imprime o caminho da execução. Opcionalmente,
`--entrada tests/fixtures/redacao-real.md --saida CAMINHO_NOVO` permite um teste
sem substituir o original. Cada execução tem diretório novo com `redacao.md`,
`entrada.json`, `avaliacoes/` e `execucao-agentes.json`. Não sobrescreva uma execução.

O programa só reconhece as seções do modelo. Metadados ficam fora do texto avaliado.
Parágrafos são separados por linhas em branco; quebras dentro de um parágrafo são
preservadas. Números de parágrafo são referências digitais, não linhas físicas.
O campo de linhas aceita inteiro ou `desconhecida`. Não estime um valor ausente.
Informe `manuscrito`, `braille` ou `desconhecido` no sistema de escrita.

## Delegação independente

Leia a política, o contrato, as cinco competências e as situações de avaliação.
Inicie A e B **antes de esperar qualquer resultado**. Com ferramentas que expõem
tipos personalizados, selecione `corretor_a` e `corretor_b`. Se a ferramenta só
expuser criação genérica de subagente, abra contexto sem herdar a conversa
(`fork_turns="none"`, quando houver), leia o TOML do papel e inclua suas
`developer_instructions` no pedido. Nesse caso, configure explicitamente
`gpt-6.1-sol`/`xhigh` e registre que o papel foi carregado pelo prompt, não por
seleção nativa do tipo. Se o modelo não estiver acessível, registre o modelo
realmente usado e a limitação; não altere a configuração global para testar alternativas.

Cada pedido contém somente: papel, caminho absoluto de `entrada.json`, caminhos
absolutos dos oito documentos (cinco competências, política, contrato e situações),
caminho exclusivo de saída
`avaliacoes/A.json` ou `B.json`, e ordem para não ler nenhum resultado alheio.
Não envie histórico, nota-alvo, nome “redação nota mil”, comentário oficial, resposta
esperada ou conteúdo de outra avaliação. A origem bibliográfica do fixture pode
ficar na cópia Markdown; o avaliador recebe apenas `entrada.json`, que não a inclui.

A independência é de contexto e de instruções. Os agentes compartilham filesystem
e provedor: não alegue isolamento de sistema operacional ou cegamento garantido
por permissões. Não abrir os PDFs completos ou resultados é parte do protocolo.
Se a ferramenta só conseguir herdar notas já vistas, use nova sessão independente
ou declare a impossibilidade; não faça uma terceira leitura contaminada.

Registre no manifesto `execucao-agentes.json` um item por corretor, com `id`,
`modelo`, `esforco`, `contexto_novo: true`, `inicio`, `fim` (ISO com fuso),
`papel_carregado` (`nativo` ou `prompt`) e `avaliacao` (caminho relativo).
Use os dados reais das ferramentas e relógio; não delegue esse registro ao corretor.
Depois de terminado, marque `concluido: true`. Requerem-se IDs distintos e
intervalos sobrepostos para A/B; C começa somente após o fim de ambos.

## Validar e arbitrar

Execute `python scripts/validar-avaliacoes.py consolidar --execucao CAMINHO`.
Erro de contrato, nota inválida, trecho inexistente ou SHA diferente interrompe a
consolidação com erro explícito; peça reparo ao próprio autor, informando somente
o erro. Isso não autoriza orientar nota ou mostrar dados alheios. Preserve o arquivo
anterior como `A-invalida-1.json` antes do reparo quando já houver resultado real.

Se o estado for `aguardando_c`, inicie somente então C em contexto novo, com
entrada/critérios e `avaliacoes/C.json`. Não envie sequer qual competência divergiu.
Registre C, espere a conclusão e reexecute o mesmo comando. O script impede uso
de C sem discrepância. A decisão segue [arbitragem](arbitragem.md).

## Publicar o relatório local

A consolidação cria `arbitragem.json` e `relatorio-final.md` **dentro da execução**.
Confira evidências e classificações dos próprios pareceres sem reatribuir notas.
Em seguida execute `python scripts/validar-avaliacoes.py publicar --execucao CAMINHO`.
Esse comando valida novamente entrada, avaliações, manifesto e decisão, e publica
uma cópia em `resultados/relatorio-final.md`, com links para a execução imutável.
Resultados de testes ficam em seus diretórios e não são publicados como correção
da entrada vazia do usuário. O manifesto exige subagentes reais declarados; o
programa verifica consistência estrutural/temporal, mas não autentica a ferramenta.

No chat, apresente nota e método, três prioridades, limitação relevante e link do
relatório. Em `banca_simulada_pendente`, informe que não há nota final segura.
Reescrita completa é opcional e só deve ser criada em arquivo separado quando
solicitada. Alternativas pontuais já aparecem no relatório. Nunca altere o original.
