"""Testes do dominio.py da busca-marca, só com a biblioteca padrão.

Rodar na raiz do repositório: python -m unittest discover -s tests
"""

import sys
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "busca-marca" / "scripts"))

import dominio  # noqa: E402

HOJE = date(2026, 11, 6)


class EstaExpirado(unittest.TestCase):
    def test_data_passada(self):
        self.assertTrue(dominio.esta_expirado("2026-10-02T00:00:00-03:00", HOJE))

    def test_data_futura(self):
        self.assertFalse(dominio.esta_expirado("2029-01-28T00:00:00-03:00", HOJE))

    def test_data_ausente(self):
        for vazio in ("", None):
            self.assertFalse(dominio.esta_expirado(vazio, HOJE))

    def test_vence_hoje_ainda_nao_expirou(self):
        self.assertFalse(dominio.esta_expirado("2026-11-06T00:00:00-03:00", HOJE))

    def test_compara_no_fuso_de_brasilia(self):
        # 02h UTC do dia 6 ainda é dia 5 em Brasília: já passou.
        self.assertTrue(dominio.esta_expirado("2026-11-06T02:00:00Z", HOJE))
        # 03h UTC do dia 6 já é dia 6 em Brasília: vence hoje, não passou.
        self.assertFalse(dominio.esta_expirado("2026-11-06T03:00:00+00:00", HOJE))

    def test_so_a_data(self):
        self.assertTrue(dominio.esta_expirado("2026-11-05", HOJE))

    def test_texto_invalido_nao_vira_expirado(self):
        self.assertFalse(dominio.esta_expirado("sem data", HOJE))

    def test_sem_tzdata_usa_utc_menos_3(self):
        with mock.patch.dict(sys.modules, {"zoneinfo": None}):
            self.assertIs(dominio.fuso_de_brasilia(), dominio.UTC_MENOS_3)
            self.assertTrue(dominio.esta_expirado("2026-11-06T02:00:00Z", HOJE))


class SaidaDoExpirado(unittest.TestCase):
    def test_registrado_expirado_nunca_livre(self):
        item = dominio.montar_item("acessos.com.br", {"status": 2, "expires-at": "2026-10-02T00:00:00-03:00"}, HOJE)
        self.assertTrue(item["expirado"])
        self.assertEqual(item["status"], 2)
        self.assertNotIn("DISPONÍVEL", item["situacao"])
        situacao, observacao = dominio.linha_da_tabela(item)
        self.assertEqual(situacao, "registrado, expirado")
        self.assertEqual(observacao, "expirou em 2026-10-02; em prazo de renovação, pode ser liberado depois")
        self.assertIn("registrado, expirado (expirou em 2026-10-02", dominio.linha_de_texto(item))

    def test_registrado_em_dia(self):
        item = dominio.montar_item("sigilo.com.br", {"status": 2, "expires-at": "2029-01-28T00:00:00-03:00"}, HOJE)
        self.assertFalse(item["expirado"])
        self.assertEqual(dominio.linha_da_tabela(item), ("registrado", "expira em 2029-01-28"))

    def test_livre_nao_tem_expirado(self):
        item = dominio.montar_item("viusumiu.com.br", {"status": 0}, HOJE)
        self.assertFalse(item["expirado"])
        self.assertEqual(dominio.linha_da_tabela(item), ("**livre**", ""))

    def test_expirado_so_vale_para_registrado(self):
        # Em liberação (5) com data passada continua "em liberação".
        item = dominio.montar_item("sigilox.com.br", {"status": 5, "expires-at": "2026-10-02T00:00:00-03:00"}, HOJE)
        self.assertFalse(item["expirado"])
        self.assertEqual(dominio.linha_da_tabela(item)[0], "em liberação")


class UserAgent(unittest.TestCase):
    def test_robo_honesto_igual_ao_do_inpi(self):
        self.assertFalse(dominio.UA.startswith("Mozilla"))
        self.assertIn("busca-marca", dominio.UA)

    def test_consulta_manda_o_user_agent(self):
        resposta = mock.MagicMock()
        resposta.__enter__.return_value.read.return_value = b'{"status": 0}'
        with mock.patch.object(dominio.urllib.request, "urlopen", return_value=resposta) as urlopen:
            self.assertEqual(dominio.consultar("exemplo.com.br"), {"status": 0})
        pedido = urlopen.call_args.args[0]
        self.assertEqual(pedido.get_header("User-agent"), dominio.UA)


if __name__ == "__main__":
    unittest.main()
