# Pontuação e arbitragem

## Regras oficiais verificadas

Fontes: cartilha 2026, pp. 6–7; [FAQ do Inep](https://www.gov.br/inep/pt-br/acesso-a-informacao/perguntas-frequentes/exame-nacional-do-ensino-medio-enem),
seção “Cálculo da nota da redação”, consultada em 02/11/2026.

Cada corretor escolhe 0, 40, 80, 120, 160 ou 200 para cada competência avaliada.
O total é a soma. Discrepância: diferença total **>100**, diferença em qualquer
competência **>80**, ou divergência de situação. A média não tem de ser um nível da
matriz: por exemplo, 160 e 200 produzem 180, não um novo descritor oficial.

Sem discrepância A/B, use a média dos totais. Com discrepância, peça C de forma
independente. Se C for compatível apenas com um dos dois, selecione esse par.
Se for compatível com ambos, selecione o par de totais mais próximos. Se C estiver
equidistante e não houver escolha inequívoca, há encaminhamento a banca. Se C for
incompatível com ambos, também há banca. A banca oficial é composta por três
avaliadores e atribui a nota final, descartando as anteriores.

O script preserva a comparação dos três pares e considera compatibilidade numérica
e de situação. C só pode existir após discrepância A/B. Nenhum desempate por nome
do corretor, ordem de arquivo, preferência por rigor ou média dos três é oficial.

**Limite matemático:** totais individuais válidos são múltiplos de 40; portanto,
uma diferença total exatamente 100 é impossível nesse domínio. A função de limite
é testada separadamente com 100; a validação continua recusando totais inválidos.

## Banca simulada: decisão local, não regra do Inep

O coordenador não produz uma quarta leitura nem uma quarta nota subjetiva.
Quando todas as situações são `normal`, mas persiste discrepância ou empate,
o script produz uma **estimativa pedagógica por mediana de cada competência**
das três avaliações. A soma dessas cinco medianas é explicitamente identificada
como resultado da banca simulada. Não é média oficial nem reprodução da deliberação
de uma banca humana. O relatório mantém todas as notas, o motivo do encaminhamento,
o método e `par_selecionado: null`. Essa estimativa pode coincidir ou não com uma
das notas e não comprova que a avaliação mediana é correta.

Quando há situações diferentes e nenhum par compatível, o resultado é
`banca_simulada_pendente`, sem nota final: números não decidem se houve fuga ou
anulação. O relatório pede revisão humana do motivo e da evidência; não inventa
consenso ou zero global. Uma execução com essa pendência é um diagnóstico auditável,
não uma correção final resolvida. O coordenador não remove a pendência por conta própria.

O par compatível pode resolver a divergência de situação quando duas avaliações
independentes efetivamente concordam. Isso é registrado; a avaliação descartada
continua disponível para auditoria.
