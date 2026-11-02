# Situações de avaliação

Fonte principal: [cartilha 2026](fontes-oficiais.md), pp. 7–10, 25–27 e 35–38;
complemento operacional: FAQ oficial, “Casos em que a redação poderá ter nota zero”.

## Regras oficiais

Fuga total ao tema e predominância de outro tipo textual produzem zero global:
não são apenas notas baixas em C2. Ausência de texto na folha configura em branco.
Texto insuficiente: até sete linhas manuscritas ou até dez em Braille. Desconsidere
linhas copiadas da proposta/caderno na contagem mínima, quando a cópia e sua
extensão estiverem efetivamente documentadas.

São motivos de anulação descritos pela cartilha: impropérios/desenhos e outras
formas propositais de anulação; parte deliberadamente desconectada; identificação
fora do espaço próprio; texto predominantemente estrangeiro; ilegibilidade que
impeça leitura por dois avaliadores. Para parte desconectada, examine a articulação
argumentativa: citar música, protesto ou religião de modo pertinente não é anulação.
Título é opcional e não recebe avaliação nas competências; pode provocar anulação
se ele próprio contiver característica anulável. Não penalize o título como C1.

**Direitos humanos:** proposta que os viole recebe zero em C5, preservando a
avaliação das outras competências. Isso não é, sozinho, zero global.

**Tangenciamento:** não é fuga total; limita C2, C3 e C5 a no máximo 40. C1 e C4
continuam sendo avaliadas em seus próprios descritores.

## Registro local e limites

Use um código de situação: `normal`, `fuga_tema`, `tipo_textual`, `em_branco`,
`texto_insuficiente` ou `anulada`. O código não é uma nova classificação oficial:
é apenas representação em JSON. Para zero global, registre o motivo e evidências,
deixe `competencias` vazio e não invente cinco avaliações que oficialmente não
foram realizadas. O cálculo usa total zero; a tabela mostra “não avaliada”.

A divergência entre códigos é divergência de situação, inclusive se os totais
coincidirem. Dúvida não resolvida sobre um motivo não é motivo confirmado: registre
a limitação, solicite evidência quando indispensável e não declare anulação.

O programa recusa zero por extensão quando as linhas ou o sistema de escrita são
desconhecidos. Cópia parcial exigiria contagem física autoral confiável: nessa situação
não automatize anulação com as linhas totais. A falta de motivadores limita a
verificação de cópia/dependência; não preencha essa lacuna com suposição.
