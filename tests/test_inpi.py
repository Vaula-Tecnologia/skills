"""Testes do inpi.py da busca-marca, só com a biblioteca padrão e sem rede.

Rodar na raiz do repositório: python -m unittest discover -s tests
"""

import argparse
import contextlib
import io
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "skills" / "busca-marca" / "scripts"))

import inpi  # noqa: E402


def ficha(processo: str) -> str:
    return f"<html><td>Nº do Processo: {processo} Marca: TESTE</td><td>Representante Legal</td></html>"


class SessaoFalsa:
    """Cada processo tem uma fila de respostas: texto da ficha ou exceção."""

    respostas: dict = {}

    def __init__(self) -> None:
        self.pedidos = []

    def detalhe(self, processo: str) -> str:
        self.pedidos.append(processo)
        resposta = self.respostas[processo].pop(0)
        if isinstance(resposta, BaseException):
            raise resposta
        return resposta


def rodar_detalhe(respostas: dict, processos: list[str]) -> tuple[str, int]:
    SessaoFalsa.respostas = respostas
    saida = io.StringIO()
    codigo = 0
    with mock.patch.object(inpi, "Sessao", SessaoFalsa), contextlib.redirect_stdout(saida):
        try:
            inpi.detalhe(argparse.Namespace(processo=processos))
        except SystemExit as fim:
            codigo = fim.code
    return saida.getvalue(), codigo


class DetalheComPePILento(unittest.TestCase):
    def test_timeout_nao_derruba_as_outras_e_tenta_de_novo_no_fim(self):
        texto, codigo = rodar_detalhe(
            {
                "918372194": [TimeoutError("The read operation timed out"), ficha("918372194")],
                "916940357": [ficha("916940357")],
            },
            ["918372194", "916940357"],
        )
        self.assertEqual(codigo, 0)
        self.assertIn("Nº do Processo: 916940357", texto)
        self.assertIn("tento de novo no fim", texto)
        self.assertIn("=== Processo 918372194 (segunda tentativa)", texto)
        self.assertIn("Nº do Processo: 918372194", texto)
        self.assertNotIn("FICHAS NÃO LIDAS", texto)
        # A segunda tentativa vem depois da ficha que respondeu.
        self.assertLess(texto.index("Nº do Processo: 916940357"), texto.index("(segunda tentativa)"))

    def test_sem_resposta_duas_vezes_lista_e_sai_com_1(self):
        texto, codigo = rodar_detalhe(
            {
                "918372194": [TimeoutError(), TimeoutError()],
                "929074122": [ficha("929074122")],
            },
            ["918372194", "929074122"],
        )
        self.assertEqual(codigo, 1)
        self.assertIn("Nº do Processo: 929074122", texto)
        self.assertIn("FICHAS NÃO LIDAS: 918372194.", texto)
        self.assertIn("não classifique o risco", texto)

    def test_outros_erros_de_rede_tambem_seguem(self):
        texto, codigo = rodar_detalhe(
            {"911489088": [ConnectionResetError(), inpi.http.client.RemoteDisconnected(), ]},
            ["911489088"],
        )
        self.assertEqual(codigo, 1)
        self.assertIn("ConnectionResetError", texto)
        self.assertIn("RemoteDisconnected", texto)

    def test_processo_inexistente_nao_tenta_de_novo(self):
        texto, codigo = rodar_detalhe(
            {"123456789": [RuntimeError("processo 123456789 não encontrado no pePI")]},
            ["123456789"],
        )
        self.assertEqual(codigo, 0)
        self.assertIn("não encontrado", texto)
        self.assertNotIn("segunda tentativa", texto)

    def test_trecho_vai_do_processo_ao_representante(self):
        self.assertEqual(inpi.trecho_da_ficha(ficha("916940357")).strip(), "Nº do Processo: 916940357 Marca: TESTE")


class Timeout(unittest.TestCase):
    def test_limite_cobre_a_ficha_lenta(self):
        self.assertGreaterEqual(inpi.TIMEOUT, 180)

    def test_pedir_usa_o_limite_do_modulo(self):
        sessao = object.__new__(inpi.Sessao)
        sessao.abridor = mock.MagicMock()
        sessao.abridor.open.return_value.__enter__.return_value.read.return_value = b"ok"
        with mock.patch.object(inpi, "TIMEOUT", 7), mock.patch.object(inpi.time, "sleep"):
            self.assertEqual(sessao._pedir("https://exemplo"), "ok")
        self.assertEqual(sessao.abridor.open.call_args.kwargs["timeout"], 7)


if __name__ == "__main__":
    unittest.main()
