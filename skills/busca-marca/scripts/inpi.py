"""Busca preliminar de marcas no INPI (pePI), pelo acesso anônimo.

Uso:
    python inpi.py buscar "viu sumiu" [--exata] [--classe 9 --classe 42] [--vivos]
                          [--max-paginas 5] [--json]
    python inpi.py detalhe 921829710 [938313193 ...]  (número do processo, 9 dígitos)

Só biblioteca padrão. Uma sessão anônima por execução ("continuar sem login"),
com pausa entre pedidos para não sobrecarregar o pePI.

O que o pePI faz e este script respeita:
- A busca "radical" (padrão) acha a palavra DENTRO de outras ("viu" acha
  "PREVIU", "NAVIUM") e ignora espaços ("esvai" acha "Inglês vai"); a
  "exata" acha só a marca igual. Nenhuma das duas é fonética: "sumiu" não
  acha "çumiu" nem "sumyu".
- Classe com dois dígitos ("09"): o script completa o zero sozinho.
- O filtro de classe aceita uma classe de Nice por vez: com várias, o script
  faz uma busca por classe. Marca antiga (antes de 2000) usa a classe nacional
  brasileira ("38 : 10"); o pePI mapeia parte delas para Nice, mas não todas:
  para não perder nenhuma, rode também sem --classe.
- 100 resultados por página; as seguintes vêm por Action=nextPageMarca&page=N.
"""

import argparse
import html
import http.client
import http.cookiejar
import json
import re
import sys
import time
import urllib.parse
import urllib.request

BASE = "https://busca.inpi.gov.br/pePI"
# User-Agent honesto de robô, nunca de navegador. Conferido ao vivo em
# 2026-11-09: o pePI e o registro.br respondem a ele como ao de navegador.
UA = "busca-marca/1.0 (robo de busca preliminar de marcas; +https://github.com/Vaula-Tecnologia/skills)"
PAUSA = 1.5
POR_PAGINA = 100
CODIFICACAO = "iso-8859-1"
# A ficha (Action=detail) é a página lenta do pePI: em 2026-11-09 levou de
# 25 s a mais de 180 s, enquanto a busca respondia em menos de 2 s. Com 60 s,
# metade das fichas estourava o tempo.
TIMEOUT = 180
# Rede: tempo esgotado, conexão recusada ou caída, erro HTTP ou de TLS.
SEM_RESPOSTA = (OSError, http.client.HTTPException)

# Situações que não bloqueiam mais (a marca morreu). "Indeferido" ainda pode
# estar no prazo de recurso: o relatório deve dizer isso quando aparecer.
MORTA = re.compile(r"extint|arquivad|indeferid|nul[oa]\b|inexistente|cancelad", re.I)
# Marca de alto renome (art. 125 da Lei 9.279/96: proteção em todas as
# classes). O pePI a lista no topo da primeira página, sem número de processo
# ("-") e com "Alto Renome" na coluna da situação, mesmo na busca filtrada
# por classe (visto em 2026-11-09: Havaianas na busca radical "vai", classe
# 09). Até essa data a linha era descartada por não ter processo.
ALTO_RENOME = re.compile(r"alto\s+renome", re.I)


class Sessao:
    def __init__(self) -> None:
        self.cookies = http.cookiejar.CookieJar()
        self.abridor = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookies))
        self.abridor.addheaders = [("User-Agent", UA)]
        self._pedir(f"{BASE}/servlet/LoginController?action=login")
        self._pedir(f"{BASE}/jsp/marcas/Pesquisa_classe_basica.jsp")

    def _pedir(self, url: str, dados: dict | None = None, referer: str | None = None) -> str:
        corpo = urllib.parse.urlencode(dados, encoding=CODIFICACAO).encode("ascii") if dados else None
        pedido = urllib.request.Request(url, data=corpo)
        if referer:
            pedido.add_header("Referer", referer)
        with self.abridor.open(pedido, timeout=TIMEOUT) as resposta:
            texto = resposta.read().decode(CODIFICACAO, errors="replace")
        time.sleep(PAUSA)
        return texto

    def buscar(self, marca: str, exata: bool, classe: str) -> str:
        dados = {
            "buscaExata": "sim" if exata else "nao",
            "txt": "Pesquisa Exata" if exata else "Pesquisa Radical",
            "marca": marca,
            "classeInter": classe,
            "registerPerPage": str(POR_PAGINA),
            "botao": "pesquisar",
            "Action": "searchMarca",
            "tipoPesquisa": "BY_MARCA_CLASSIF_BASICA",
        }
        return self._pedir(
            f"{BASE}/servlet/MarcasServletController",
            dados,
            referer=f"{BASE}/jsp/marcas/Pesquisa_classe_basica.jsp",
        )

    def pagina(self, n: int) -> str:
        return self._pedir(f"{BASE}/servlet/MarcasServletController?Action=nextPageMarca&page={n}")

    def detalhe(self, processo: str) -> str:
        """A ficha só abre na sessão que já achou o processo numa busca
        (direto pelo CodPedido dá "Pedido inexistente"): busca pelo número antes."""
        lista = self._pedir(
            f"{BASE}/servlet/MarcasServletController",
            {
                "NumPedido": processo,
                "NumGRU": "",
                "NumProtocolo": "",
                "NumInscricaoInternacional": "",
                "botao": "pesquisar",
                "Action": "searchMarca",
                "tipoPesquisa": "BY_NUM_PROC",
            },
            referer=f"{BASE}/jsp/marcas/Pesquisa_num_processo.jsp",
        )
        cod = re.search(r"CodPedido=(\d+)", lista)
        if not cod:
            raise RuntimeError(f"processo {processo} não encontrado no pePI")
        return self._pedir(f"{BASE}/servlet/MarcasServletController?Action=detail&CodPedido={cod.group(1)}")


def _texto(fragmento: str) -> str:
    sem_tags = re.sub(r"<[^>]+>", " ", fragmento)
    return re.sub(r"\s+", " ", html.unescape(sem_tags)).strip()


def total_de(pagina: str) -> int:
    if "Nenhum resultado foi encontrado" in pagina:
        return 0
    achado = re.search(r"Foram encontrados\s+(\d+)", _texto(pagina))
    if not achado:
        # Página inesperada (sessão caiu, formulário mudou): melhor parar do
        # que dizer "nenhuma marca" sem ter buscado.
        raise RuntimeError("resposta do pePI sem contagem de resultados; o formulário pode ter mudado")
    return int(achado.group(1))


def linhas_de(pagina: str) -> list[dict]:
    resultado = []
    for linha in re.findall(r"<tr[^>]*>(.*?)</tr>", pagina, re.S):
        celulas = re.findall(r"<td[^>]*>(.*?)</td>", linha, re.S)
        if len(celulas) < 8:
            continue
        numero = _texto(celulas[0])
        situacao = _texto(celulas[5])
        # A linha de alto renome não tem processo, mas não pode sumir: é a
        # marca de proteção mais ampla que a busca acha.
        alto_renome = numero in ("-", "") and bool(ALTO_RENOME.search(situacao))
        if not alto_renome and not re.fullmatch(r"\d{9}", numero):
            continue
        cod = re.search(r"CodPedido=(\d+)", celulas[0])
        apresentacao = re.search(r'alt="([^"]+)"', celulas[2])
        deposito = _texto(celulas[1])
        resultado.append(
            {
                "processo": "" if alto_renome else numero,
                "cod": cod.group(1) if cod else "",
                "deposito": "" if deposito == "-" else deposito,
                "apresentacao": apresentacao.group(1).replace("Marca ", "") if apresentacao else "",
                "marca": _texto(celulas[3]),
                "situacao": situacao,
                "viva": not MORTA.search(situacao),
                "alto_renome": alto_renome,
                "titular": _texto(celulas[6]),
                "classe": _texto(celulas[7]),
            }
        )
    return resultado


def buscar(args: argparse.Namespace) -> None:
    sessao = Sessao()
    saida = []
    # O pePI quer a classe com dois dígitos: "9" acha só parte da classe 9
    # (medido em 2026-11-06: "vai" deu 191 processos com "9" e 331 com "09").
    for classe in [c.strip().zfill(2) for c in args.classe] if args.classe else [""]:
        primeira = sessao.buscar(args.marca, args.exata, classe)
        total = total_de(primeira)
        marcas = linhas_de(primeira)
        paginas = -(-total // POR_PAGINA)
        lidas = min(paginas, args.max_paginas)
        for n in range(2, lidas + 1):
            marcas += linhas_de(sessao.pagina(n))
        if args.vivos:
            marcas = [m for m in marcas if m["viva"]]
        saida.append(
            {
                "termo": args.marca,
                "tipo": "exata" if args.exata else "radical",
                "classe": classe or "todas",
                "total": total,
                "paginas_lidas": lidas,
                "paginas_total": paginas,
                "marcas": marcas,
            }
        )

    if args.json:
        print(json.dumps(saida, ensure_ascii=False, indent=2))
        return
    for bloco in saida:
        cab = f"=== '{bloco['termo']}' ({bloco['tipo']}), classe {bloco['classe']}: {bloco['total']} processo(s)"
        if bloco["paginas_lidas"] < bloco["paginas_total"]:
            cab += f" (li {bloco['paginas_lidas']} de {bloco['paginas_total']} páginas; filtre por classe ou aumente --max-paginas)"
        print(cab)
        if args.vivos:
            print("    (só as vivas)")
        for m in bloco["marcas"]:
            if m["alto_renome"]:
                print(f"  ALTO RENOME (sem processo; protegida em todas as classes, art. 125) | {m['marca']}")
                continue
            print(
                f"  {m['processo']} | {m['deposito']} | {m['marca']} | {m['situacao']}"
                f" | {m['titular']} | {m['classe']} | {m['apresentacao']}"
            )
        if not bloco["marcas"]:
            print("  (nenhuma)")


def trecho_da_ficha(pagina: str) -> str:
    texto = _texto(re.sub(r"<script.*?</script>", " ", pagina, flags=re.S))
    inicio = texto.find("Nº do Processo")
    fim = texto.find("Representante Legal", inicio)
    return texto[inicio:fim if fim > inicio else inicio + 3000] if inicio >= 0 else texto[:3000]


def detalhe(args: argparse.Namespace) -> None:
    """Uma ficha que não vem não derruba as outras: segue para o próximo
    processo e tenta as que faltaram mais uma vez no fim. Em 2026-11-09 a
    ficha que estourou 180 s veio em 1 s na segunda tentativa."""
    sessao = Sessao()
    pendentes = list(args.processo)
    for tentativa in (1, 2):
        sem_resposta = []
        for processo in pendentes:
            print(f"=== Processo {processo}" + (" (segunda tentativa)" if tentativa == 2 else ""))
            try:
                pagina = sessao.detalhe(processo)
            except RuntimeError as erro:
                print(f"  {erro}\n")
                continue
            except SEM_RESPOSTA as erro:
                print(f"  pePI sem resposta ({erro.__class__.__name__}: {erro})")
                print("  tento de novo no fim\n" if tentativa == 1 else "")
                sem_resposta.append(processo)
                continue
            print(trecho_da_ficha(pagina))
            print()
        pendentes = sem_resposta
        if not pendentes:
            return
    print(
        f"FICHAS NÃO LIDAS: {' '.join(pendentes)}. O pePI não respondeu duas vezes."
        f" Rode `detalhe {' '.join(pendentes)}` daqui a alguns minutos;"
        " sem a ficha, não classifique o risco dessas marcas."
    )
    sys.exit(1)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Busca preliminar de marcas no INPI (pePI).")
    sub = parser.add_subparsers(dest="comando", required=True)

    b = sub.add_parser("buscar", help="busca por marca (radical por padrão)")
    b.add_argument("marca")
    b.add_argument("--exata", action="store_true", help="só a marca igual (padrão: radical)")
    b.add_argument("--classe", action="append", help="classe de Nice; repita para várias")
    b.add_argument("--vivos", action="store_true", help="esconde extintas, arquivadas, indeferidas e nulas")
    b.add_argument("--max-paginas", type=int, default=5, help="páginas de 100 por busca (padrão 5)")
    b.add_argument("--json", action="store_true")
    b.set_defaults(func=buscar)

    d = sub.add_parser("detalhe", help="ficha do processo: especificação, titular, situação")
    d.add_argument("processo", nargs="+", help="número do processo (9 dígitos, primeira coluna da busca)")
    d.set_defaults(func=detalhe)

    args = parser.parse_args()
    try:
        args.func(args)
    except SEM_RESPOSTA as erro:
        # Login ou busca sem resposta: não há resultado parcial que valha.
        print(
            f"pePI sem resposta ({erro.__class__.__name__}: {erro}). Tente de novo daqui a"
            " alguns minutos; isto não quer dizer \"nenhuma marca\".",
            file=sys.stderr,
        )
        sys.exit(1)


if __name__ == "__main__":
    main()
