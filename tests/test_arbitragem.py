"""Testes determinísticos. Não medem acurácia linguística dos modelos."""

from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


RAIZ = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("banca", RAIZ / "scripts/validar-avaliacoes.py")
banca = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(banca)

ENTRADA = """# Redação

## Tema

Inclusão digital das pessoas idosas no Brasil

## Texto integral

As pessoas idosas têm direito à participação social. Serviços exclusivamente digitais podem restringir esse direito.

Quando um serviço exige cadastro virtual, quem não possui acesso perde autonomia. Por isso, o atendimento presencial deve ser mantido.

As prefeituras devem oferecer oficinas em bibliotecas, com monitores, para ampliar a autonomia digital dos idosos.

## Metadados

Linhas físicas: desconhecida
Sistema de escrita: manuscrito
Observações de transcrição:

## Textos motivadores (opcional)

"""


def avaliacao(letra, valores=(160, 160, 160, 160, 160), codigo="normal"):
    return {
        "corretor": letra,
        "situacao": {"codigo": codigo},
        "competencias": {f"C{i}": {"nota": n} for i, n in enumerate(valores, 1)} if codigo == "normal" else {},
    }


def completa(letra, entrada):
    a = avaliacao(letra)
    evidencia = {"paragrafo": 1, "trecho": "As pessoas idosas têm direito à participação social.", "analise": "Apresenta ponto de vista relacionado ao tema."}
    a.update(
        entrada_sha256=entrada["entrada_sha256"],
        situacao={"codigo": "normal", "justificativa": "Texto argumentativo pertinente ao tema.", "evidencias": [deepcopy(evidencia)]},
        tema={"atendimento": "integral", "justificativa": "Inclusão digital de idosos no Brasil.", "evidencias": [deepcopy(evidencia)]},
        parecer="Texto com tese e relação de causa e consequência; análise sintética para teste do contrato.",
        acertos=["P2 explica a perda de autonomia causada pela exigência de cadastro."],
        paragrafos=[], problemas=[], repertorios=[],
        intervencao={**dict.fromkeys(("acao", "agente", "meio", "efeito", "detalhamento")), "direitos_humanos": "respeitados", "justificativa": "Oficinas com finalidade de autonomia."},
        prioridades=[{"foco": "Explicitar um mecanismo causal em P2.", "exercicio": "Substituir uma generalização por uma explicação.", "criterio_sucesso": "A relação entre cadastro e restrição fica identificável."}],
        limitacoes=["Linhas físicas desconhecidas e motivadores não fornecidos."],
    )
    for c in a["competencias"].values():
        c.update(justificativa="Nível usado em fixture sintético para testar validação, sem pretensão de correção real.", evidencias=[deepcopy(evidencia)], proximo_nivel="Aprimorar o desempenho conforme o descritor, sem exigir novas linhas.")
    for p in entrada["paragrafos"]:
        a["paragrafos"].append({"paragrafo": p["numero"], "funcao": "Função argumentativa.", "parecer": "Contribui ao projeto de texto.", "evidencias": [{"paragrafo": p["numero"], "trecho": p["texto"], "analise": "Trecho completo do parágrafo para auditoria."}]})
    return a


def manifesto(com_c=False):
    agentes = {}
    for c, inicio, fim in [("A", "10:00", "10:06"), ("B", "10:01", "10:07")] + ([("C", "10:08", "10:12")] if com_c else []):
        agentes[c] = {"id": f"fixture-{c}", "modelo": "fixture-sintetico", "esforco": "xhigh", "contexto_novo": True, "concluido": True, "papel_carregado": "prompt", "inicio": f"2026-11-02T{inicio}:00+00:00", "fim": f"2026-11-02T{fim}:00+00:00", "avaliacao": f"avaliacoes/{c}.json"}
    return {"subagentes_reais": True, "agentes": agentes}


class LimitesTest(unittest.TestCase):
    def test_total_exatamente_100_nao_discrepa(self):
        self.assertFalse(banca.ha_discrepancia(100, [40, 40, 20, 0, 0]))

    def test_total_120_discrepa(self):
        self.assertTrue(banca.ha_discrepancia(120, [40, 40, 40, 0, 0]))

    def test_competencia_80_nao_discrepa(self):
        self.assertFalse(banca.ha_discrepancia(0, [80, 80, 0, 0, 0]))

    def test_competencia_120_com_totais_iguais_discrepa(self):
        self.assertTrue(banca.ha_discrepancia(0, [120, 120, 0, 0, 0]))

    def test_situacao_sozinha_discrepa(self):
        self.assertTrue(banca.ha_discrepancia(0, [0] * 5, True))


class ArbitragemTest(unittest.TestCase):
    def test_media_sem_discrepancia(self):
        r = banca.arbitrar([avaliacao("A"), avaliacao("B", (200, 160, 160, 160, 160))])
        self.assertEqual((r["nota_final"], r["notas_consolidadas"]["C1"], r["par_selecionado"]), (820, 180, ["A", "B"]))

    def test_soma_das_competencias_equivale_media_totais(self):
        r = banca.arbitrar([avaliacao("A"), avaliacao("B", (200, 200, 160, 160, 160))])
        self.assertEqual(sum(r["notas_consolidadas"].values()), r["nota_final"])

    def test_discrepancia_requer_c(self):
        r = banca.arbitrar([avaliacao("A", (40,) * 5), avaliacao("B", (200,) * 5)])
        self.assertEqual(r["estado"], "aguardando_c")
        self.assertIsNone(r["nota_final"])

    def test_c_resolve_com_um_compativel(self):
        r = banca.arbitrar([avaliacao("A", (200,) * 5), avaliacao("B", (80,) * 5), avaliacao("C", (200, 200, 200, 160, 160))])
        self.assertEqual((r["par_selecionado"], r["nota_final"]), (["A", "C"], 960))

    def test_c_compativel_com_ambos_escolhe_mais_proximo(self):
        r = banca.arbitrar([avaliacao("A", (160,) * 5), avaliacao("B", (200, 200, 200, 160, 160)), avaliacao("C", (200, 160, 160, 160, 160))])
        self.assertEqual((r["par_selecionado"], r["nota_final"]), (["A", "C"], 820))

    def test_c_persiste_discrepancia_banca_identificada(self):
        r = banca.arbitrar([avaliacao("A", (40,) * 5), avaliacao("B", (120,) * 5), avaliacao("C", (200,) * 5)])
        self.assertEqual((r["estado"], r["nota_final"]), ("banca_simulada", 600))
        self.assertIsNone(r["par_selecionado"])

    def test_empate_nao_e_resolvido_por_ordem(self):
        a, b, c = avaliacao("A", (160,) * 5), avaliacao("B", (200, 200, 200, 200, 160)), avaliacao("C", (200, 200, 160, 160, 160))
        r = banca.arbitrar([a, b, c])
        self.assertEqual(r["estado"], "banca_simulada")
        self.assertIn("Empate", r["motivo_banca"])
        self.assertIsNone(r["par_selecionado"])

    def test_nao_seleciona_par_incompativel_so_por_total_proximo(self):
        r = banca.arbitrar([avaliacao("A", (200, 80, 160, 160, 160)), avaliacao("B", (80, 200, 160, 160, 160)), avaliacao("C", (80, 200, 160, 160, 160))])
        self.assertEqual(r["par_selecionado"], ["B", "C"])

    def test_c_desnecessario_recusado(self):
        with self.assertRaisesRegex(ValueError, "sem discrepância"):
            banca.arbitrar([avaliacao("A"), avaliacao("B"), avaliacao("C")])

    def test_situacao_resolvida_por_par_concordante(self):
        r = banca.arbitrar([avaliacao("A"), avaliacao("B", codigo="fuga_tema"), avaliacao("C", codigo="fuga_tema")])
        self.assertEqual((r["par_selecionado"], r["nota_final"]), (["B", "C"], 0))
        self.assertIsNone(r["notas_consolidadas"])

    def test_situacoes_distintas_sem_par_ficam_pendentes(self):
        r = banca.arbitrar([avaliacao("A"), avaliacao("B", codigo="fuga_tema"), avaliacao("C", codigo="anulada")])
        self.assertEqual(r["estado"], "banca_simulada_pendente")
        self.assertIsNone(r["nota_final"])

    def test_zero_global_concordante(self):
        r = banca.arbitrar([avaliacao("A", codigo="tipo_textual"), avaliacao("B", codigo="tipo_textual")])
        self.assertEqual(r["nota_final"], 0)
        self.assertIsNone(r["notas_consolidadas"])
        self.assertTrue(all(d is None for d in r["comparacoes"][0]["diferencas_competencias"].values()))


class ValidacaoTest(unittest.TestCase):
    def setUp(self):
        self.entrada = banca.interpretar_entrada(ENTRADA.encode("utf-8"))
        self.a = completa("A", self.entrada)

    def validar(self):
        return banca.validar_avaliacao(self.a, self.entrada, "A")

    def test_aceita_contrato_completo_sem_citacao_de_autoridade(self):
        self.assertEqual(self.validar()["repertorios"], [])

    def test_notas_invalidas_incluindo_boolean_e_float(self):
        for invalida in [-40, 20, 100, 180, 240, True, 160.0, "160", None]:
            with self.subTest(nota=invalida):
                self.a["competencias"]["C1"]["nota"] = invalida
                with self.assertRaises(ValueError):
                    self.validar()

    def test_total_inventado_recusado(self):
        self.a["total"] = 1000
        with self.assertRaisesRegex(ValueError, "Total"):
            self.validar()

    def test_trecho_inexistente_recusado(self):
        self.a["competencias"]["C1"]["evidencias"][0]["trecho"] = "erro que o autor não escreveu"
        with self.assertRaisesRegex(ValueError, "literalmente"):
            self.validar()

    def test_trecho_em_outro_paragrafo_recusado(self):
        self.a["competencias"]["C1"]["evidencias"][0]["paragrafo"] = 2
        with self.assertRaisesRegex(ValueError, "parágrafo 2"):
            self.validar()

    def test_sha_de_outra_redacao_recusado(self):
        self.a["entrada_sha256"] = "outro"
        with self.assertRaisesRegex(ValueError, "SHA"):
            self.validar()

    def test_tangenciamento_impede_notas_acima_de_40(self):
        self.a["tema"]["atendimento"] = "tangenciamento"
        with self.assertRaisesRegex(ValueError, "Tangenciamento"):
            self.validar()
        for c in ("C2", "C3", "C5"):
            self.a["competencias"][c]["nota"] = 40
        self.validar()

    def test_fuga_nao_e_apenas_c2_zero(self):
        self.a["competencias"]["C2"]["nota"] = 0
        with self.assertRaisesRegex(ValueError, "global"):
            self.validar()

    def test_zero_global_nao_exige_merito_inventado(self):
        self.a["situacao"]["codigo"] = "tipo_textual"
        self.a["competencias"] = {}
        self.a["acertos"] = []
        self.validar()

    def test_direitos_humanos_zero_somente_c5(self):
        self.a["intervencao"].update(direitos_humanos="violados", acao=deepcopy(self.a["situacao"]["evidencias"][0]))
        with self.assertRaisesRegex(ValueError, "zero em C5"):
            self.validar()
        self.a["competencias"]["C5"]["nota"] = 0
        self.validar()
        self.assertEqual(banca.total(self.a), 640)
        self.assertEqual(self.a["situacao"]["codigo"], "normal")

    def test_c5_maxima_nao_pode_ter_elementos_ausentes(self):
        self.a["competencias"]["C5"]["nota"] = 200
        with self.assertRaisesRegex(ValueError, "cinco elementos"):
            self.validar()

    def test_linhas_desconhecidas_nao_autorizam_zero(self):
        self.a["situacao"]["codigo"] = "texto_insuficiente"
        self.a["competencias"] = {}
        with self.assertRaisesRegex(ValueError, "conhecidos"):
            self.validar()

    def test_30_linhas_nao_autorizam_zero_por_extensao(self):
        self.entrada["linhas_fisicas"] = 30
        self.a["situacao"]["codigo"] = "texto_insuficiente"
        self.a["competencias"] = {}
        with self.assertRaisesRegex(ValueError, "não comprovam"):
            self.validar()

    def test_braille_tem_limite_diferente(self):
        self.entrada.update(linhas_fisicas=10, sistema_escrita="braille")
        self.a["situacao"]["codigo"] = "texto_insuficiente"
        self.a["competencias"] = {}
        self.validar()
        self.entrada["sistema_escrita"] = "manuscrito"
        with self.assertRaises(ValueError):
            self.validar()

    def test_todos_os_paragrafos_exigidos(self):
        self.a["paragrafos"].pop()
        with self.assertRaisesRegex(ValueError, "cada parágrafo"):
            self.validar()

    def test_problema_exige_diagnostico_e_impacto(self):
        self.a["problemas"] = [{"tipo": "erro_avaliavel", "competencia": "C1", "paragrafo": 1, "trecho": "As pessoas idosas", "diagnostico": "", "impacto": "", "sugestao": ""}]
        with self.assertRaisesRegex(ValueError, "diagnostico"):
            self.validar()

    def test_melhoria_estilistica_pode_ser_facultativa_sem_desconto(self):
        self.a["problemas"] = [{"tipo": "oportunidade_melhoria", "competencia": "C1", "paragrafo": 1, "trecho": "As pessoas idosas têm direito à participação social.", "diagnostico": "Frase gramaticalmente correta; alternativa apenas estilística.", "impacto": "Não configura desvio nem justifica desconto.", "sugestao": "Manter a formulação é admissível.", "reformulacao": None}]
        self.validar()
        self.assertEqual(banca.total(self.a), 800)

    def test_repertorio_generico_exige_analise_nao_multa_automatica(self):
        self.a["repertorios"] = [{"paragrafo": 1, "trecho": "As pessoas idosas têm direito à participação social.", "referencia": "Direitos sociais", "legitimidade": "Conhecimento cívico sem atribuição a autor.", "pertinencia": "Vinculado à inclusão de idosos.", "produtividade": "O conhecimento é aplicado à restrição de serviços, sem desconto automático por ser comum.", "verificacao": "nao_verificado", "fonte_url": None}]
        self.validar()
        self.assertEqual(banca.total(self.a), 800)
        self.a["repertorios"][0]["produtividade"] = ""
        with self.assertRaises(ValueError):
            self.validar()

    def test_verificacao_inventada_sem_url_recusada(self):
        self.a["repertorios"] = [{"paragrafo": 1, "trecho": "participação social", "referencia": "Direitos", "legitimidade": "Conhecimento cívico", "pertinencia": "Idosos", "produtividade": "Direito contraposto à exclusão", "verificacao": "verificado", "fonte_url": None}]
        with self.assertRaisesRegex(ValueError, "URL"):
            self.validar()


class EntradaEFluxoTest(unittest.TestCase):
    def test_modelo_vazio_nao_vira_redacao_zero(self):
        with self.assertRaisesRegex(ValueError, "Tema ausente"):
            banca.interpretar_entrada((RAIZ / "redacao.md").read_bytes())

    def test_tema_ausente_nao_e_inventado(self):
        with self.assertRaisesRegex(ValueError, "Tema ausente"):
            banca.interpretar_entrada(ENTRADA.replace("Inclusão digital das pessoas idosas no Brasil", "").encode())

    def test_linhas_fisicas_desconhecidas_independem_de_wrap(self):
        entrada = banca.interpretar_entrada(ENTRADA.replace("Quando um serviço", "Quando\num serviço").encode())
        self.assertIsNone(entrada["linhas_fisicas"])
        self.assertEqual(len(entrada["paragrafos"]), 3)

    def test_estimativa_de_linhas_recusada(self):
        with self.assertRaisesRegex(ValueError, "não use estimativas"):
            banca.interpretar_entrada(ENTRADA.replace("desconhecida", "cerca de 30").encode())

    def test_metadata_fora_da_redacao(self):
        entrada = banca.interpretar_entrada(ENTRADA.encode())
        self.assertNotIn("Linhas físicas", entrada["texto"])

    def test_secoes_duplicadas_recusadas(self):
        with self.assertRaisesRegex(ValueError, "duplicada"):
            banca.interpretar_entrada((ENTRADA + "\n## Tema\nOutro tema\n").encode())

    def test_cli_exibe_erro_em_utf8_mesmo_com_console_ascii(self):
        with tempfile.TemporaryDirectory() as pasta:
            entrada = Path(pasta) / "texto.md"
            entrada.write_text("## Tema\n\n## Texto integral\nTeste.\n", encoding="utf-8")
            ambiente = dict(os.environ, PYTHONIOENCODING="ascii")
            r = subprocess.run([sys.executable, str(RAIZ / "scripts/validar-avaliacoes.py"), "preparar", "--entrada", str(entrada)], capture_output=True, env=ambiente)
            self.assertEqual(r.returncode, 2)
            self.assertIn("frase temática", r.stderr.decode("utf-8"))

    def test_fluxo_preserva_original_e_publica_apenas_com_manifesto(self):
        with tempfile.TemporaryDirectory() as pasta:
            base = Path(pasta)
            original = base / "redacao.md"
            original.write_text(ENTRADA, encoding="utf-8")
            antes = original.read_bytes()
            execucao = banca.preparar(original, base / "execucao")
            entrada = banca.carregar_entrada(execucao)
            for c in ("A", "B"):
                banca.gravar_json(execucao / f"avaliacoes/{c}.json", completa(c, entrada))
            self.assertEqual(banca.consolidar(execucao)["nota_final"], 800)
            with self.assertRaisesRegex(ValueError, "Manifesto"):
                banca.consolidar(execucao, publicar=True)
            banca.gravar_json(execucao / "execucao-agentes.json", manifesto())
            for i in range(1, 6):
                destino = base / f"docs/competencia-{i}.md"
                destino.parent.mkdir(exist_ok=True)
                destino.write_bytes((RAIZ / f"docs/competencia-{i}.md").read_bytes())
            with patch.object(banca, "RAIZ", base):
                banca.consolidar(execucao, publicar=True)
            relatorio = (base / "resultados/relatorio-final.md").read_text(encoding="utf-8")
            self.assertIn("800/1000", relatorio)
            for letra in "ABCDEFGHIJ":
                self.assertIn(f"## {letra}.", relatorio)
            self.assertEqual(original.read_bytes(), antes)
            self.assertEqual((execucao / "redacao.md").read_bytes(), antes)

    def test_entrada_congelada_alterada_recusada(self):
        with tempfile.TemporaryDirectory() as pasta:
            base = Path(pasta)
            original = base / "texto.md"
            original.write_text(ENTRADA, encoding="utf-8")
            execucao = banca.preparar(original, base / "run")
            (execucao / "redacao.md").write_text(ENTRADA + "alteração", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "alterada"):
                banca.carregar_entrada(execucao)

    def test_execucao_existente_nao_e_sobrescrita(self):
        with tempfile.TemporaryDirectory() as pasta:
            original = Path(pasta) / "texto.md"
            original.write_text(ENTRADA, encoding="utf-8")
            destino = Path(pasta) / "run"
            banca.preparar(original, destino)
            with self.assertRaises(FileExistsError):
                banca.preparar(original, destino)

    def test_relatorio_30_linhas_nao_manda_ampliar(self):
        entrada = banca.interpretar_entrada(ENTRADA.replace("desconhecida", "30").encode())
        avaliacoes = [completa(c, entrada) for c in ("A", "B")]
        r = banca.arbitrar(avaliacoes)
        s = banca.renderizar(entrada, avaliacoes, r, Path("run"), Path("run/relatorio.md"))
        self.assertIn("Linhas físicas: 30", s)
        self.assertNotIn("escreva mais linhas", s.casefold())

    def test_matriz_tem_apenas_os_seis_niveis_oficiais(self):
        self.assertTrue(all(set(niveis) == banca.NIVEIS for niveis in banca.descritores().values()))

    def test_relatorio_zero_global_nao_inventa_niveis_por_competencia(self):
        entrada = banca.interpretar_entrada(ENTRADA.encode())
        avaliacoes = [completa(c, entrada) for c in ("A", "B")]
        for a in avaliacoes:
            a["situacao"]["codigo"] = "tipo_textual"
            a["competencias"] = {}
        r = banca.arbitrar(avaliacoes)
        relatorio = banca.renderizar(entrada, avaliacoes, r, Path("run"), Path("run/relatorio.md"))
        self.assertIn("não avaliada", relatorio)
        self.assertNotIn("nível 0", relatorio)
        self.assertIn("0/1000", relatorio)


class ManifestoTest(unittest.TestCase):
    def test_intervalos_e_ids_distintos_aceitos(self):
        banca.validar_manifesto(manifesto(True), [avaliacao(c) for c in "ABC"])

    def test_avaliacao_sequencial_recusada(self):
        m = manifesto()
        m["agentes"]["B"]["inicio"] = "2026-11-02T10:06:00+00:00"
        with self.assertRaisesRegex(ValueError, "paralelo"):
            banca.validar_manifesto(m, [avaliacao(c) for c in "AB"])

    def test_mesmo_agente_nao_e_dupla_independente(self):
        m = manifesto()
        m["agentes"]["B"]["id"] = m["agentes"]["A"]["id"]
        with self.assertRaisesRegex(ValueError, "distintos"):
            banca.validar_manifesto(m, [avaliacao(c) for c in "AB"])

    def test_c_antecipado_recusado(self):
        m = manifesto(True)
        m["agentes"]["C"]["inicio"] = "2026-11-02T10:05:00+00:00"
        with self.assertRaisesRegex(ValueError, "antes"):
            banca.validar_manifesto(m, [avaliacao(c) for c in "ABC"])

    def test_contexto_herdado_recusado(self):
        m = manifesto()
        m["agentes"]["A"]["contexto_novo"] = False
        with self.assertRaisesRegex(ValueError, "contexto novo"):
            banca.validar_manifesto(m, [avaliacao(c) for c in "AB"])


class ComportamentoRegistradoTest(unittest.TestCase):
    """Revalida saídas reais preservadas; não chama nem reavalia o modelo."""

    def setUp(self):
        self.entradas = {x["id"]: x["entrada"] for x in banca.ler_json(RAIZ / "tests/regressoes/entradas.json")}
        self.avaliacoes = {x["id"]: x["avaliacao"] for x in banca.ler_json(RAIZ / "tests/regressoes/avaliacoes.json")}

    def test_todas_as_evidencias_das_saidas_reais_sao_literais(self):
        self.assertEqual(set(self.entradas), set(self.avaliacoes))
        for caso, a in self.avaliacoes.items():
            with self.subTest(caso=caso):
                banca.validar_avaliacao(a, self.entradas[caso], "A")

    def test_texto_sem_citacoes_nao_recebe_exigencia_de_citacao(self):
        a = self.avaliacoes["sem-citacoes-30-linhas"]
        self.assertEqual(self.entradas["sem-citacoes-30-linhas"]["linhas_fisicas"], 30)
        self.assertFalse(a["problemas"])
        self.assertTrue(a["repertorios"])

    def test_referencia_ampla_aplicada_depois_nao_vira_erro_automatico(self):
        a = self.avaliacoes["repertorio-generico"]
        self.assertTrue(a["repertorios"])
        self.assertTrue(all(p["tipo"] == "oportunidade_melhoria" for p in a["problemas"]))

    def test_construcao_correta_e_repeticao_funcional_nao_viram_desvios(self):
        a = self.avaliacoes["repeticao-funcional"]
        self.assertIsNone(self.entradas["repeticao-funcional"]["linhas_fisicas"])
        self.assertFalse(a["problemas"])


if __name__ == "__main__":
    unittest.main()
