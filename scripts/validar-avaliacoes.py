"""Entrada, auditoria de evidências e arbitragem ENEM, sem dependências externas."""

import argparse
from datetime import datetime, timezone
import hashlib
from itertools import combinations
import json
import os
from pathlib import Path
import re
from statistics import median
import sys
import tempfile


RAIZ = Path(__file__).resolve().parents[1]
COMPETENCIAS = tuple(f"C{i}" for i in range(1, 6))
NIVEIS = {0, 40, 80, 120, 160, 200}
SITUACOES = {"normal", "fuga_tema", "tipo_textual", "em_branco", "texto_insuficiente", "anulada"}


def exigir(condicao, mensagem):
    if not condicao:
        raise ValueError(mensagem)


def texto(valor, campo):
    exigir(isinstance(valor, str) and bool(valor.strip()), f"{campo}: texto obrigatório.")


def lista(valor, campo, minimo=0):
    exigir(isinstance(valor, list) and len(valor) >= minimo, f"{campo}: lista com pelo menos {minimo} item(ns).")


def ler_json(caminho):
    return json.loads(Path(caminho).read_text(encoding="utf-8-sig"))


def gravar(caminho, conteudo):
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=caminho.parent, delete=False) as arq:
            temporario = Path(arq.name)
            arq.write(conteudo)
        os.replace(temporario, caminho)
    finally:
        if temporario is not None and temporario.exists():
            temporario.unlink()


def gravar_json(caminho, valor):
    gravar(caminho, json.dumps(valor, ensure_ascii=False, indent=2) + "\n")


def interpretar_entrada(dados):
    original = dados.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n")
    secoes = {}
    for m in re.finditer(r"^## ([^\n]+)\n(.*?)(?=^## |\Z)", original, re.M | re.S):
        nome = m[1].strip()
        if nome == "Texto":
            nome = "Texto integral"
        exigir(nome not in secoes, f"Seção duplicada: {nome}.")
        secoes[nome] = m[2].strip()
    tema = secoes.get("Tema", "")
    corpo = secoes.get("Texto integral", "")
    texto(tema, "Tema ausente em redacao.md; informe a frase temática")
    texto(corpo, "Texto integral ausente em redacao.md; preencha a redação")
    meta = secoes.get("Metadados", "")
    campos = {}
    for linha in meta.splitlines():
        if ":" in linha:
            chave, valor = linha.split(":", 1)
            exigir(chave.strip() not in campos, f"Metadado duplicado: {chave.strip()}.")
            campos[chave.strip()] = valor.strip()
    linhas = campos.get("Linhas físicas", "").casefold()
    if linhas in {"", "desconhecida", "desconhecido", "não informado", "nao informado"}:
        linhas = None
    else:
        exigir(bool(re.fullmatch(r"\d+", linhas)), "Linhas físicas: use inteiro ou desconhecida; não use estimativas.")
        linhas = int(linhas)
        exigir(linhas > 0, "Linhas físicas: número precisa ser positivo para um texto preenchido.")
    sistema = campos.get("Sistema de escrita", "desconhecido").casefold() or "desconhecido"
    exigir(sistema in {"manuscrito", "braille", "digital", "desconhecido"}, "Sistema de escrita: manuscrito, braille, digital ou desconhecido.")
    paragrafos = [p.strip() for p in re.split(r"\n[ \t]*\n", corpo) if p.strip()]
    return {
        "versao": 1,
        "entrada_sha256": hashlib.sha256(dados).hexdigest(),
        "tema": tema,
        "texto": corpo,
        "paragrafos": [{"numero": i, "texto": p} for i, p in enumerate(paragrafos, 1)],
        "linhas_fisicas": linhas,
        "sistema_escrita": sistema,
        "observacoes_transcricao": campos.get("Observações de transcrição", ""),
        "textos_motivadores": secoes.get("Textos motivadores (opcional)", ""),
    }


def preparar(entrada, saida=None):
    dados = Path(entrada).read_bytes()
    documento = interpretar_entrada(dados)
    if saida is None:
        saida = RAIZ / "resultados" / "execucoes" / datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    saida = Path(saida).resolve()
    saida.mkdir(parents=True, exist_ok=False)
    (saida / "avaliacoes").mkdir()
    (saida / "redacao.md").write_bytes(dados)
    gravar_json(saida / "entrada.json", documento)
    gravar_json(saida / "execucao-agentes.json", {"subagentes_reais": True, "agentes": {}, "requer_checagem_repertorios": True})
    gravar_json(saida / "checagem-repertorios.json", {
        "entrada_sha256": documento["entrada_sha256"], "estado": "pendente",
        "escopo": "", "limitacoes": [], "itens": [],
    })
    return saida


def carregar_entrada(execucao):
    congelada = ler_json(execucao / "entrada.json")
    recalculada = interpretar_entrada((execucao / "redacao.md").read_bytes())
    exigir(congelada == recalculada, "Entrada congelada foi alterada ou não corresponde à cópia da redação.")
    return congelada


def validar_trecho(item, entrada, campo, analise=False):
    exigir(isinstance(item, dict), f"{campo}: objeto obrigatório.")
    numero = item.get("paragrafo")
    exigir(type(numero) is int and 1 <= numero <= len(entrada["paragrafos"]), f"{campo}: parágrafo inválido.")
    trecho = item.get("trecho")
    texto(trecho, f"{campo}.trecho")
    exigir(trecho in entrada["paragrafos"][numero - 1]["texto"], f"{campo}: trecho não existe literalmente no parágrafo {numero}: {trecho!r}.")
    if analise:
        texto(item.get("analise"), f"{campo}.analise")


def validar_evidencias(itens, entrada, campo, minimo=1):
    lista(itens, campo, minimo)
    for i, item in enumerate(itens):
        validar_trecho(item, entrada, f"{campo}[{i}]", analise=True)


def validar_checagem(checagem, entrada):
    exigir(isinstance(checagem, dict), "Checagem de repertórios deve ser objeto JSON.")
    exigir(checagem.get("entrada_sha256") == entrada["entrada_sha256"], "Checagem: SHA da entrada diferente.")
    exigir(checagem.get("estado") in {"concluida", "limitada"}, "Checagem de repertórios pendente; conclua a pesquisa ou declare a limitação.")
    texto(checagem.get("escopo"), "checagem.escopo")
    lista(checagem.get("limitacoes"), "checagem.limitacoes", 1 if checagem["estado"] == "limitada" else 0)
    for limite in checagem["limitacoes"]:
        texto(limite, "checagem.limitacoes[]")
    lista(checagem.get("itens"), "checagem.itens")
    for item in checagem["itens"]:
        validar_trecho(item, entrada, "checagem.itens[]")
        for campo in ("alegacao", "justificativa"):
            texto(item.get(campo), f"checagem.{campo}")
        exigir(item.get("resultado") in {"confirmado", "contradito", "nao_localizado", "inconclusivo", "nao_verificado"}, "Resultado de checagem inválido.")
        consultado = item["resultado"] != "nao_verificado"
        lista(item.get("consultas"), "checagem.consultas", int(consultado))
        for consulta in item["consultas"]:
            texto(consulta, "checagem.consultas[]")
        lista(item.get("fontes"), "checagem.fontes", int(item["resultado"] in {"confirmado", "contradito"}))
        exigir(consultado or not item["fontes"], "Checagem não verificada não pode alegar fontes consultadas.")
        exigir(consultado or checagem["estado"] == "limitada", "Checagem não verificada exige estado limitada.")
        for fonte in item["fontes"]:
            exigir(isinstance(fonte, dict), "checagem.fontes[]: objeto obrigatório.")
            exigir(isinstance(fonte.get("url"), str) and fonte["url"].startswith(("https://", "http://")), "Checagem exige URL da fonte consultada.")
            for campo in ("evidencia", "localizacao"):
                texto(fonte.get(campo), f"checagem.fonte.{campo}")
    return checagem


def notas(avaliacao):
    if avaliacao["situacao"]["codigo"] != "normal":
        return dict.fromkeys(COMPETENCIAS, 0)
    return {c: avaliacao["competencias"][c]["nota"] for c in COMPETENCIAS}


def total(avaliacao):
    return sum(notas(avaliacao).values())


def validar_avaliacao(avaliacao, entrada, corretor):
    exigir(isinstance(avaliacao, dict), f"{corretor}: avaliação precisa ser objeto JSON.")
    exigir(avaliacao.get("corretor") == corretor, f"Identidade incorreta; esperado {corretor}.")
    exigir(avaliacao.get("entrada_sha256") == entrada["entrada_sha256"], f"{corretor}: SHA da entrada divergente.")
    situacao = avaliacao.get("situacao")
    exigir(isinstance(situacao, dict), f"{corretor}.situacao: objeto obrigatório.")
    codigo = situacao.get("codigo")
    exigir(codigo in SITUACOES, f"{corretor}: situação desconhecida.")
    texto(situacao.get("justificativa"), "situacao.justificativa")
    validar_evidencias(situacao.get("evidencias"), entrada, "situacao.evidencias", 0 if codigo == "em_branco" else 1)
    if codigo == "em_branco":
        exigir(not entrada["texto"].strip(), "Texto preenchido não pode ser classificado como em branco.")
    if codigo == "texto_insuficiente":
        limite = {"manuscrito": 7, "braille": 10}.get(entrada["sistema_escrita"])
        exigir(limite is not None and entrada["linhas_fisicas"] is not None, "Zero por extensão exige linhas físicas e sistema de escrita conhecidos.")
        exigir(entrada["linhas_fisicas"] <= limite, "Linhas totais não comprovam texto insuficiente; não estime linhas autorais/copiadas.")
    tema = avaliacao.get("tema")
    exigir(isinstance(tema, dict), "tema: objeto obrigatório.")
    atendimento = tema.get("atendimento")
    exigir(atendimento in {"integral", "tangenciamento", "fuga", "nao_avaliavel"}, "tema.atendimento inválido.")
    texto(tema.get("justificativa"), "tema.justificativa")
    validar_evidencias(tema.get("evidencias"), entrada, "tema.evidencias", 0 if codigo == "em_branco" else 1)
    exigir((atendimento == "fuga") == (codigo == "fuga_tema"), "Fuga exige situação global fuga_tema, e vice-versa.")
    exigir(atendimento != "nao_avaliavel" or codigo != "normal", "Texto normal exige análise temática.")
    competencias = avaliacao.get("competencias")
    exigir(isinstance(competencias, dict), "competencias: objeto obrigatório.")
    if codigo == "normal":
        exigir(set(competencias) == set(COMPETENCIAS), "Avaliação normal exige exatamente C1–C5.")
        for c in COMPETENCIAS:
            item = competencias[c]
            exigir(isinstance(item, dict), f"{c}: objeto obrigatório.")
            exigir(type(item.get("nota")) is int and item["nota"] in NIVEIS, f"{c}: nota fora de 0,40,80,120,160,200.")
            texto(item.get("justificativa"), f"{c}.justificativa")
            texto(item.get("proximo_nivel"), f"{c}.proximo_nivel")
            validar_evidencias(item.get("evidencias"), entrada, f"{c}.evidencias")
        exigir(competencias["C2"]["nota"] != 0, "C2 zero configura situação global; não mantenha situação normal.")
        if atendimento == "tangenciamento":
            exigir(all(competencias[c]["nota"] <= 40 for c in ("C2", "C3", "C5")), "Tangenciamento limita C2, C3 e C5 a 40.")
    else:
        exigir(not competencias, "Zero global: competências não avaliadas devem ficar em objeto vazio.")
    if "total" in avaliacao:
        exigir(type(avaliacao["total"]) is int and avaliacao["total"] == total(avaliacao), "Total declarado não confere com a soma determinística.")
    texto(avaliacao.get("parecer"), "parecer")
    lista(avaliacao.get("acertos"), "acertos", 1 if codigo == "normal" else 0)
    for acerto in avaliacao["acertos"]:
        texto(acerto, "acertos[]")
    lista(avaliacao.get("paragrafos"), "paragrafos")
    encontrados = []
    for p in avaliacao["paragrafos"]:
        exigir(isinstance(p, dict), "paragrafos[]: objeto obrigatório.")
        texto(p.get("funcao"), "paragrafo.funcao")
        texto(p.get("parecer"), "paragrafo.parecer")
        validar_evidencias(p.get("evidencias"), entrada, "paragrafo.evidencias")
        numero = p.get("paragrafo")
        exigir(type(numero) is int and all(e["paragrafo"] == numero for e in p["evidencias"]), "Evidência de análise de parágrafo aponta para outro parágrafo.")
        encontrados.append(numero)
    exigir(sorted(encontrados) == list(range(1, len(entrada["paragrafos"]) + 1)), "É preciso analisar cada parágrafo exatamente uma vez.")
    lista(avaliacao.get("problemas"), "problemas")
    for i, item in enumerate(avaliacao["problemas"]):
        campo = f"problemas[{i}]"
        validar_trecho(item, entrada, campo)
        exigir(item.get("tipo") in {"erro_avaliavel", "oportunidade_melhoria", "ambiguidade"}, f"{campo}.tipo inválido.")
        exigir(item.get("competencia") in COMPETENCIAS, f"{campo}.competencia inválida.")
        for chave in ("diagnostico", "impacto", "sugestao"):
            texto(item.get(chave), f"{campo}.{chave}")
        if item.get("reformulacao") is not None:
            texto(item["reformulacao"], f"{campo}.reformulacao")
    lista(avaliacao.get("repertorios"), "repertorios")
    for item in avaliacao["repertorios"]:
        validar_trecho(item, entrada, "repertorios[]")
        for chave in ("referencia", "legitimidade", "pertinencia", "produtividade"):
            texto(item.get(chave), f"repertorio.{chave}")
        exigir(item.get("verificacao") in {"verificado", "nao_verificado"}, "repertorio.verificacao inválido.")
        fonte = item.get("fonte_url")
        if item["verificacao"] == "verificado":
            exigir(isinstance(fonte, str) and fonte.startswith(("https://", "http://")), "Repertório verificado exige URL; a consulta real deve ser auditada pelo coordenador.")
        else:
            exigir(fonte is None, "Não atribua fonte de verificação a repertório não verificado.")
    intervencao = avaliacao.get("intervencao")
    exigir(isinstance(intervencao, dict), "intervencao: objeto obrigatório.")
    for chave in ("acao", "agente", "meio", "efeito", "detalhamento"):
        exigir(chave in intervencao, f"intervencao.{chave} obrigatório, ainda que null.")
        if intervencao[chave] is not None:
            validar_trecho(intervencao[chave], entrada, f"intervencao.{chave}", analise=True)
    exigir(intervencao.get("direitos_humanos") in {"respeitados", "violados", "nao_avaliavel"}, "intervencao.direitos_humanos inválido.")
    texto(intervencao.get("justificativa"), "intervencao.justificativa")
    if codigo == "normal" and intervencao["direitos_humanos"] == "violados":
        exigir(competencias["C5"]["nota"] == 0 and intervencao["acao"] is not None, "Violação de direitos humanos exige evidência e zero em C5.")
    if codigo == "normal" and competencias["C5"]["nota"] == 200:
        exigir(all(intervencao[c] is not None for c in ("acao", "agente", "meio", "efeito", "detalhamento")) and intervencao["direitos_humanos"] == "respeitados", "C5 no nível 200 exige evidências dos cinco elementos e respeito aos direitos humanos.")
    lista(avaliacao.get("prioridades"), "prioridades", 1)
    exigir(len(avaliacao["prioridades"]) <= 3, "Registre no máximo três prioridades.")
    for item in avaliacao["prioridades"]:
        exigir(isinstance(item, dict), "prioridades[]: objeto obrigatório.")
        for chave in ("foco", "exercicio", "criterio_sucesso"):
            texto(item.get(chave), f"prioridade.{chave}")
    lista(avaliacao.get("limitacoes"), "limitacoes")
    for item in avaliacao["limitacoes"]:
        texto(item, "limitacoes[]")
    return avaliacao


def ha_discrepancia(diferenca_total, diferencas_competencias, divergencia_situacao=False):
    return diferenca_total > 100 or any(d > 80 for d in diferencas_competencias) or divergencia_situacao


def comparar(a, b):
    na, nb = notas(a), notas(b)
    normais = a["situacao"]["codigo"] == b["situacao"]["codigo"] == "normal"
    diferencas = {c: abs(na[c] - nb[c]) if normais else None for c in COMPETENCIAS}
    diferenca_total = abs(total(a) - total(b))
    situacao = a["situacao"]["codigo"] != b["situacao"]["codigo"]
    return {
        "par": [a["corretor"], b["corretor"]],
        "diferenca_total": diferenca_total,
        "diferencas_competencias": diferencas,
        "divergencia_situacao": situacao,
        "discrepancia": ha_discrepancia(diferenca_total, [d for d in diferencas.values() if d is not None], situacao),
    }


def arbitrar(avaliacoes):
    exigir([a["corretor"] for a in avaliacoes] in [["A", "B"], ["A", "B", "C"]], "Arbitragem exige A/B e, somente quando necessário, C.")
    comparacoes = [comparar(a, b) for a, b in combinations(avaliacoes, 2)]
    resultado = {
        "estado": None,
        "par_selecionado": None,
        "nota_final": None,
        "notas_consolidadas": None,
        "metodo": None,
        "comparacoes": comparacoes,
        "individuais": {a["corretor"]: {"situacao": a["situacao"]["codigo"], "notas": notas(a) if a["situacao"]["codigo"] == "normal" else None, "total": total(a)} for a in avaliacoes},
    }
    if not comparacoes[0]["discrepancia"]:
        exigir(len(avaliacoes) == 2, "C não pode ser acionado sem discrepância A/B.")
        candidatos = comparacoes
    elif len(avaliacoes) == 2:
        resultado.update(estado="aguardando_c", metodo="Terceira avaliação independente necessária.")
        return resultado
    else:
        candidatos = [p for p in comparacoes[1:] if not p["discrepancia"]]
    if candidatos:
        distancia = min(p["diferenca_total"] for p in candidatos)
        candidatos = [p for p in candidatos if p["diferenca_total"] == distancia]
    if len(candidatos) == 1:
        par = candidatos[0]["par"]
        selecionados = [a for a in avaliacoes if a["corretor"] in par]
        normais = all(a["situacao"]["codigo"] == "normal" for a in selecionados)
        resultado.update(
            estado="concluida", par_selecionado=par,
            nota_final=sum(total(a) for a in selecionados) / 2,
            notas_consolidadas={c: sum(notas(a)[c] for a in selecionados) / 2 for c in COMPETENCIAS} if normais else None,
            metodo="Média aritmética do par compatível selecionado segundo as regras documentadas do Inep.",
        )
    elif all(a["situacao"]["codigo"] == "normal" for a in avaliacoes):
        consolidadas = {c: median(notas(a)[c] for a in avaliacoes) for c in COMPETENCIAS}
        resultado.update(estado="banca_simulada", nota_final=sum(consolidadas.values()), notas_consolidadas=consolidadas,
                         metodo="Estimativa pedagógica local: soma das medianas por competência. Não reproduz a deliberação de banca oficial.")
    else:
        resultado.update(estado="banca_simulada_pendente", metodo="Situações divergentes sem par compatível: revisão humana da evidência necessária; nenhuma nota foi inventada.")
    if len(candidatos) != 1:
        resultado["motivo_banca"] = "Empate entre pares compatíveis equidistantes." if candidatos else "C incompatível com A e com B."
    return resultado


def validar_manifesto(manifesto, avaliacoes):
    exigir(isinstance(manifesto, dict) and manifesto.get("subagentes_reais") is True, "Manifesto deve declarar execução real de subagentes.")
    agentes = manifesto.get("agentes")
    exigir(isinstance(agentes, dict) and set(agentes) == {a["corretor"] for a in avaliacoes}, "Manifesto deve conter exatamente os corretores executados.")
    intervalos, ids = {}, []
    for letra, agente in agentes.items():
        exigir(isinstance(agente, dict), "Registro de agente inválido.")
        for campo in ("id", "modelo", "esforco"):
            texto(agente.get(campo), f"agentes.{letra}.{campo}")
        exigir(agente.get("contexto_novo") is True and agente.get("concluido") is True, f"{letra}: contexto novo e conclusão precisam ser confirmados.")
        exigir(agente.get("papel_carregado") in {"nativo", "prompt"}, "Informe como o papel foi carregado.")
        exigir(agente.get("avaliacao") == f"avaliacoes/{letra}.json", f"{letra}: caminho de avaliação inesperado.")
        datas = []
        for campo in ("inicio", "fim"):
            texto(agente.get(campo), f"{letra}.{campo}")
            data = datetime.fromisoformat(agente[campo].replace("Z", "+00:00"))
            exigir(data.utcoffset() is not None, f"{letra}: horário deve incluir fuso.")
            datas.append(data)
        exigir(datas[0] < datas[1], f"{letra}: intervalo de execução inválido.")
        intervalos[letra] = datas
        ids.append(agente["id"])
    exigir(len(ids) == len(set(ids)), "IDs dos subagentes devem ser distintos.")
    exigir(max(intervalos[c][0] for c in ("A", "B")) < min(intervalos[c][1] for c in ("A", "B")), "A/B não foram executados em paralelo.")
    if "C" in intervalos:
        exigir(intervalos["C"][0] >= max(intervalos[c][1] for c in ("A", "B")), "C começou antes do término de A/B.")


def descritores():
    matriz = {}
    for i, c in enumerate(COMPETENCIAS, 1):
        linhas = (RAIZ / f"docs/competencia-{i}.md").read_text(encoding="utf-8").splitlines()
        matriz[c] = {int(m[1]): m[2].strip() for linha in linhas if (m := re.match(r"\| (\d+) \| (.*?) \|$", linha))}
        exigir(set(matriz[c]) == NIVEIS, f"Matriz oficial incompleta em {c}.")
    return matriz


def numero(valor):
    return "pendente" if valor is None else f"{valor:g}"


def evidencias_md(itens):
    return "\n\n".join(f'P{e["paragrafo"]}: “{e["trecho"]}” — {e["analise"]}' for e in itens)


def renderizar(entrada, avaliacoes, resultado, execucao, destino, checagem=None):
    matriz = descritores()
    relativo = os.path.relpath(execucao, Path(destino).parent).replace("\\", "/")
    def link(arquivo):
        return f"{relativo}/{arquivo}"
    saida = ["# Relatório da Banca ENEM", "Simulação pedagógica. Não é correção oficial nem prevê a nota real do Inep.",
             "## A. Resultado geral", f'**Nota final: {numero(resultado["nota_final"])}/1000. Estado: {resultado["estado"]}.**',
             f'**Tema:** {entrada["tema"]}',
             f'Linhas físicas: {entrada["linhas_fisicas"] if entrada["linhas_fisicas"] is not None else "desconhecidas"}. Sistema: {entrada["sistema_escrita"]}.',
             f'Observações de transcrição: {entrada["observacoes_transcricao"] or "não informadas"}.', resultado["metodo"]]
    letras = [a["corretor"] for a in avaliacoes]
    saida.append("| Competência | " + " | ".join(letras) + " | Consolidada |\n| --- | " + " | ".join("---" for _ in letras) + " | --- |")
    for c in COMPETENCIAS:
        valores = [str(notas(a)[c]) if a["situacao"]["codigo"] == "normal" else "não avaliada" for a in avaliacoes]
        consolidada = resultado["notas_consolidadas"]
        saida[-1] += "\n| " + c + " | " + " | ".join(valores) + " | " + (numero(consolidada[c]) if consolidada is not None else "não avaliada / pendente") + " |"
    saida[-1] += "\n| **Total** | " + " | ".join(str(total(a)) for a in avaliacoes) + " | " + numero(resultado["nota_final"]) + " |"
    saida.append("Notas consolidadas intermediárias são médias, não níveis oficiais adicionais. Situação global de zero não corresponde a cinco competências avaliadas com zero.")
    saida.append(f'Par selecionado: {", ".join(resultado["par_selecionado"]) if resultado["par_selecionado"] else "nenhum"}.')
    if "motivo_banca" in resultado:
        saida.append("**Banca simulada:** " + resultado["motivo_banca"] + " " + resultado["metodo"])
    saida.append("## B. Parecer geral da banca")
    for a in avaliacoes:
        saida += [f'### Corretor {a["corretor"]}', a["parecer"], "Acertos: " + " ".join(a["acertos"])]
    saida.append("## C. Análise por competência")
    for c in COMPETENCIAS:
        saida.append(f"### {c}")
        for a in avaliacoes:
            if a["situacao"]["codigo"] != "normal":
                saida.append(f'{a["corretor"]}: não avaliada, situação {a["situacao"]["codigo"]}.')
                continue
            item = a["competencias"][c]
            saida += [f'**{a["corretor"]}: nível {item["nota"]}.** Descritor oficial: {matriz[c][item["nota"]]}',
                      item["justificativa"], evidencias_md(item["evidencias"]), "Próximo nível: " + item["proximo_nivel"]]
            if c == "C5":
                proposta = a["intervencao"]
                saida.append(f'**Composição da intervenção ({a["corretor"]}):** {proposta["justificativa"]} Direitos humanos: {proposta["direitos_humanos"]}.')
                for campo in ("acao", "agente", "meio", "efeito", "detalhamento"):
                    elemento = proposta[campo]
                    saida.append(f'{campo}: ' + (evidencias_md([elemento]) if elemento else "não identificado"))
    saida.append("## D. Correção por parágrafo")
    for p in entrada["paragrafos"]:
        saida.append(f'### Parágrafo {p["numero"]}')
        for a in avaliacoes:
            item = next(x for x in a["paragrafos"] if x["paragrafo"] == p["numero"])
            saida += [f'**{a["corretor"]} — {item["funcao"]}:** {item["parecer"]}', evidencias_md(item["evidencias"])]
    saida.append("## E. Problemas localizados")
    for a in avaliacoes:
        if not a["problemas"]:
            saida.append(f'{a["corretor"]}: nenhum problema localizado registrado.')
        for item in a["problemas"]:
            saida += [f'### {a["corretor"]} · P{item["paragrafo"]} · {item["competencia"]} · {item["tipo"]}',
                      f'Original: “{item["trecho"]}”', "Diagnóstico: " + item["diagnostico"], "Impacto: " + item["impacto"], "Sugestão: " + item["sugestao"]]
    saida.append("## F. O que eu poderia ter escrito melhor")
    saida.append("Alternativas dos avaliadores, preservando a intenção do autor. Não são trechos do original nem notas novas; não há recomendação automática de aumentar a extensão.")
    for a in avaliacoes:
        for item in a["problemas"]:
            if item.get("reformulacao"):
                saida += [f'**{a["corretor"]}, P{item["paragrafo"]}:** “{item["trecho"]}”', "Alternativa: “" + item["reformulacao"] + "”"]
    if all(not any(p.get("reformulacao") for p in a["problemas"]) for a in avaliacoes):
        saida.append("Não foram propostas reformulações pontuais.")
    saida.append("## G. Repertório sociocultural")
    if checagem is not None:
        saida += [f'**Checagem factual prévia: {checagem["estado"]}.** {checagem["escopo"]}',
                  "Checagem externa é uma salvaguarda local, separada do julgamento de legitimidade, pertinência e produtividade. Não localizado não significa falso; confirmação factual não garante uso produtivo."]
        for item in checagem["itens"]:
            saida += [f'**P{item["paragrafo"]} · {item["resultado"]}:** “{item["trecho"]}”',
                      "Alegação examinada: " + item["alegacao"], item["justificativa"],
                      "Consultas realizadas: " + ("; ".join(item["consultas"]) or "nenhuma")]
            for fonte in item["fontes"]:
                saida.append(f'[Fonte consultada]({fonte["url"]}) · {fonte["localizacao"]}. Evidência: {fonte["evidencia"]}')
        saida += ["Limitação da checagem: " + limite for limite in checagem["limitacoes"]]
        saida.append(f'[Registro da checagem]({link("checagem-repertorios.json")}). O validador confere a estrutura, não autentica a consulta nem a veracidade das fontes.')
    else:
        saida.append("Execução legada sem registro de checagem factual prévia; nenhuma confirmação externa é presumida.")
    for a in avaliacoes:
        if not a["repertorios"]:
            saida.append(f'{a["corretor"]}: nenhum repertório específico identificado; não se exige citação de autoridade.')
        for item in a["repertorios"]:
            saida += [f'### {a["corretor"]} · P{item["paragrafo"]} · {item["referencia"]}', f'“{item["trecho"]}”',
                      "Legitimidade: " + item["legitimidade"], "Pertinência: " + item["pertinencia"], "Produtividade e integração: " + item["produtividade"],
                      "Verificação externa: " + item["verificacao"] + (f' ([fonte]({item["fonte_url"]})).' if item.get("fonte_url") else "; nenhuma consulta externa alegada.")]
    saida.append("## H. Plano de evolução")
    prioridades = []
    for a in avaliacoes:
        for item in a["prioridades"]:
            if not any(p[1]["foco"].casefold() == item["foco"].casefold() for p in prioridades):
                prioridades.append((a["corretor"], item))
    for i, (letra, item) in enumerate(prioridades[:3], 1):
        saida.append(f'{i}. **{item["foco"]}** ({letra}). Exercício: {item["exercicio"]} Critério de sucesso: {item["criterio_sucesso"]}')
    saida.append("As três prioridades reproduzem a ordem proposta por A, completada por B/C quando necessário; não representam um novo julgamento de nota do coordenador.")
    saida.append("## I. Auditoria de avaliação")
    for comp in resultado["comparacoes"]:
        saida.append(f'{"/".join(comp["par"])}: diferença total {comp["diferenca_total"]}; por competência ' + ", ".join(f'{c}={d if d is not None else "não avaliada"}' for c, d in comp["diferencas_competencias"].items()) + f'; divergência de situação: {comp["divergencia_situacao"]}; discrepância: {comp["discrepancia"]}.')
    diferencas = [d for comp in resultado["comparacoes"] for d in comp["diferencas_competencias"].values() if d is not None]
    if diferencas:
        maior = max(diferencas)
        saida.append("Maior divergência por competência: " + str(maior) + " ponto(s). " + ("Nenhuma divergência numérica nas competências avaliadas." if maior == 0 else "; ".join("/".join(comp["par"]) + ": " + ", ".join(c for c, d in comp["diferencas_competencias"].items() if d == maior) for comp in resultado["comparacoes"] if maior in comp["diferencas_competencias"].values()) + "."))
    else:
        saida.append("Diferenças por competência não calculadas em pares com zero global; total e situação continuam comparados.")
    for a in avaliacoes:
        saida += [f'**Situação {a["corretor"]}: {a["situacao"]["codigo"]}.** {a["situacao"]["justificativa"]}', evidencias_md(a["situacao"]["evidencias"]), f'Limitações {a["corretor"]}: ' + (" ".join(a["limitacoes"]) or "nenhuma limitação adicional registrada")]
    if entrada["linhas_fisicas"] is None:
        saida.append("Número de linhas físicas desconhecido: nenhuma contagem foi inferida do Markdown.")
    if not entrada["textos_motivadores"]:
        saida.append("Textos motivadores não fornecidos: cópia e dependência deles não foram verificadas.")
    saida += ["Independência de contexto é protocolar; os subagentes compartilham filesystem. Validação literal não prova que o diagnóstico linguístico é correto.",
              f'SHA-256 da entrada: `{entrada["entrada_sha256"]}`.',
              f'[Entrada preservada]({link("redacao.md")}) · [Decisão estruturada]({link("arbitragem.json")}) · [Registro dos agentes]({link("execucao-agentes.json")})',
              " · ".join(f'[Corretor {a["corretor"]}]({link("avaliacoes/" + a["corretor"] + ".json")})' for a in avaliacoes),
              "Critérios: [Cartilha do Participante 2026](https://download.inep.gov.br/publicacoes/institucionais/avaliacoes_e_exames_da_educacao_basica/cartilha_enem_2026.pdf), pp. 6–7, 12–38; [FAQ do Inep](https://www.gov.br/inep/pt-br/acesso-a-informacao/perguntas-frequentes/exame-nacional-do-ensino-medio-enem), cálculo da nota.",
              "## J. Versão aprimorada opcional", "Reescrita integral não solicitada nesta execução. As alternativas pontuais estão na seção F; a redação original foi preservada. Uma versão revisada, se solicitada, deve ser entregue em arquivo separado e identificada como colaboração do revisor."]
    return "\n\n".join(s for s in saida if s) + "\n"


def consolidar(execucao, publicar=False):
    execucao = Path(execucao).resolve()
    entrada = carregar_entrada(execucao)
    avaliacoes = [validar_avaliacao(ler_json(execucao / f"avaliacoes/{c}.json"), entrada, c) for c in ("A", "B")]
    caminho_c = execucao / "avaliacoes/C.json"
    if caminho_c.exists():
        avaliacoes.append(validar_avaliacao(ler_json(caminho_c), entrada, "C"))
    caminho_checagem = execucao / "checagem-repertorios.json"
    caminho_manifesto = execucao / "execucao-agentes.json"
    manifesto = ler_json(caminho_manifesto) if caminho_manifesto.exists() else {}
    checagem = None
    if caminho_checagem.exists():
        checagem = validar_checagem(ler_json(caminho_checagem), entrada)
        checagem_sha = hashlib.sha256(caminho_checagem.read_bytes()).hexdigest()
        for avaliacao in avaliacoes:
            exigir(avaliacao.get("checagem_sha256") == checagem_sha, "Corretor deve registrar o SHA da checagem factual recebida; não altere a checagem depois da delegação.")
            for item in avaliacao["repertorios"]:
                if item["verificacao"] == "verificado":
                    exigir(any(c["paragrafo"] == item["paragrafo"] and c["trecho"] == item["trecho"]
                               and c["resultado"] in {"confirmado", "contradito"}
                               and item["fonte_url"] in [f["url"] for f in c["fontes"]]
                               for c in checagem["itens"]), "Repertório verificado sem checagem conclusiva correspondente ao trecho e à fonte.")
    else:
        exigir(not manifesto.get("requer_checagem_repertorios"), "Registro de checagem de repertórios ausente nesta execução.")
    resultado = arbitrar(avaliacoes)
    resultado["entrada_sha256"] = entrada["entrada_sha256"]
    if publicar:
        exigir(resultado["estado"] != "aguardando_c", "Não é possível publicar antes da terceira avaliação necessária.")
        validar_manifesto(manifesto, avaliacoes)
    gravar_json(execucao / "arbitragem.json", resultado)
    if resultado["estado"] != "aguardando_c":
        destino = execucao / "relatorio-final.md"
        gravar(destino, renderizar(entrada, avaliacoes, resultado, execucao, destino, checagem))
        if publicar:
            destino = RAIZ / "resultados/relatorio-final.md"
            gravar(destino, renderizar(entrada, avaliacoes, resultado, execucao, destino, checagem))
    return resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="comando", required=True)
    entrada = sub.add_parser("preparar")
    entrada.add_argument("--entrada", type=Path, default=RAIZ / "redacao.md")
    entrada.add_argument("--saida", type=Path)
    for comando in ("checar-repertorios", "consolidar", "publicar"):
        p = sub.add_parser(comando)
        p.add_argument("--execucao", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.comando == "preparar":
            print(json.dumps({"estado": "entrada_preparada", "execucao": str(preparar(args.entrada, args.saida))}, ensure_ascii=False))
        elif args.comando == "checar-repertorios":
            entrada = carregar_entrada(args.execucao)
            caminho = args.execucao / "checagem-repertorios.json"
            checagem = validar_checagem(ler_json(caminho), entrada)
            print(json.dumps({"estado": checagem["estado"], "checagem_sha256": hashlib.sha256(caminho.read_bytes()).hexdigest()}, ensure_ascii=False))
        else:
            print(json.dumps(consolidar(args.execucao, args.comando == "publicar"), ensure_ascii=False, indent=2))
        return 0
    except (ValueError, OSError, TypeError, KeyError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    sys.exit(main())
