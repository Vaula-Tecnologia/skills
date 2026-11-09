---
name: busca-marca
description: Busca preliminar de marca no INPI (base pePI, acesso anônimo) e de domínio .br no registro.br, com leitura do risco de conflito. Use sempre que o usuário quiser saber se um nome de produto, empresa ou serviço "está livre", "pode ser registrado", "já existe no INPI", "tem marca parecida", ou quando estiver comparando nomes já escolhidos, e também quando pedir para consultar um processo de marca pelo número. Para criar nomes novos com .com.br livre, a skill é a cria-nome, que depois passa os finalistas para esta. Não substitui o parecer de um advogado de marcas, e o relatório diz isso.
---

# Busca de marca e domínio

Responde a pergunta "posso usar este nome?" em duas frentes:

- **INPI (pePI)**: há marca igual ou parecida, viva, no mesmo mercado?
- **registro.br**: o domínio está livre?

O valor da skill está em três pontos:
- buscar do jeito certo: radical, por palavra, pelas classes do produto;
- abrir a ficha das marcas que parecem conflitar, porque é a especificação que decide;
- dizer o risco com o motivo, sem enrolar.

## Scripts

Os dois scripts estão em `scripts/` desta skill. Rode com `python`; eles só usam a biblioteca padrão.

```sh
# INPI: busca radical (acha a palavra dentro de outras), em todas as classes
python scripts/inpi.py buscar "viu sumiu"
# só nas classes do produto (sempre dois dígitos: 09), escondendo as marcas mortas
python scripts/inpi.py buscar viu --classe 09 --classe 42 --vivos
# só a marca igual
python scripts/inpi.py buscar "viu sumiu" --exata
# ficha de um processo: especificação, titular, situação
python scripts/inpi.py detalhe 938313193 921829710

# registro.br: .com.br por padrão
python scripts/dominio.py selar viusumiu esvai
python scripts/dominio.py sigilo --sufixo seg.br
# em que outras categorias .br o nome está livre
python scripts/dominio.py sigilo --sugestoes
# tabela para o relatório, com a situação por extenso
python scripts/dominio.py selar esvai --markdown
```

Use `--json` nos dois quando for processar o resultado.

Os scripts fazem pausas entre pedidos, porque o pePI e o registro.br são serviços públicos. Não rode em laço nem em paralelo. Para muitos nomes, rode uma lista só e espere.

A busca do pePI responde em segundos, mas a ficha (`detalhe`) pode levar de 1 a 3 minutos por processo. Com mais de uma ficha, rode o `detalhe` em segundo plano ou com o tempo máximo do terminal, e passe todos os processos num comando só.

## Fluxo

1. **Entenda o produto** em uma linha: o que faz e para quem. É isso que define as classes de Nice. Para software, comece por 09 e 42 e acrescente 35, 38 ou 45 conforme o serviço. A tabela está em `references/analise-de-risco.md`.
2. **Busque em camadas.** A estratégia completa está na referência, e o essencial é:
   - a marca inteira, sem classe;
   - a grafia junta e as variantes;
   - cada palavra distintiva sozinha, nas classes do produto;
   - o radical da sílaba tônica ou final, e a marca com uma letra a menos ou com hífen.

   Uma marca nova costuma bater de frente com outra por uma palavra só, ou por um nome quase igual, e não pelo nome inteiro. "Esvai" não tem marca igual, mas esbarra em "E-vai", do Banco do Brasil.
3. **Abra a ficha** (`detalhe`) de cada marca viva que pareça conflitar e leia a especificação. A mesma classe 42 cobre desde engenharia até "segurança por meio de senha"; só a especificação mostra se o mercado é o mesmo.
4. **Classifique o risco** (alto, médio ou baixo) pela escala da referência, citando o processo, o titular, a situação e a especificação que pesam.
5. **Domínio**, quando o usuário estiver escolhendo nome: consulte junto. Se ele restringiu a extensão (por exemplo, só `.com.br`), respeite.
6. **Relate** no formato abaixo.

Ao comparar vários nomes, faça o fluxo para cada um. Termine com uma recomendação que ponha os dois lados na balança: o que o nome tem de bom para vender e o risco que traz no INPI.

## Formato do relatório

Comece pela resposta: o nome está limpo, tem risco médio ou tem conflito. Depois:

- **O que a busca encontrou.** Para cada termo buscado, a contagem. Detalhe as marcas vivas que importam: processo, marca, titular, situação, classe e o trecho da especificação que pesa. Agrupe as mortas numa linha ("as outras 20 estão extintas ou arquivadas").
- **Risco e motivo.** Cite o dispositivo legal quando ele explicar o risco (art. 124, XIX, por exemplo), em uma frase de português claro.
- **Domínio**, se foi consultado.
- **Recomendação**: seguir, seguir com cautela (registrar o domínio, consultar advogado antes de investir na marca) ou trocar de nome.
- **Limites**, em uma linha: busca preliminar, não fonética, que não substitui a busca de anterioridade de um advogado.

Ponha a data da busca, porque o resultado muda com o tempo. O horário segue a regra de fuso do usuário.

## Quando algo der errado

- `RuntimeError: resposta do pePI sem contagem`: o formulário ou a sessão mudou. Não conclua "nenhuma marca". Abra `https://busca.inpi.gov.br/pePI/jsp/marcas/Pesquisa_classe_basica.jsp`, confira os campos do formulário e ajuste `Sessao.buscar` em `scripts/inpi.py`.
- `processo ... não encontrado`: confira se o número tem 9 dígitos. O `detalhe` recebe o número do processo, não o código interno.
- `pePI sem resposta` numa ficha: o script espera até 180 s, segue para o próximo processo e tenta as que faltaram mais uma vez no fim. Se alguma ainda faltar, ele lista em `FICHAS NÃO LIDAS` e sai com código 1, depois de mostrar as outras. Rode `detalhe` só com essas daqui a alguns minutos. Sem a ficha, não classifique o risco da marca; se precisar entregar antes, diga no relatório qual ficha não foi lida.
- `pePI sem resposta` na busca: não houve resultado. Espere alguns minutos e rode de novo; não conclua "nenhuma marca".
- Resultado com mais páginas do que as lidas: o cabeçalho avisa. Filtre por classe ou aumente `--max-paginas`, em vez de concluir com a lista cortada.
- registro.br com "limite de consultas" (status 8): o script já esperou e tentou de novo. Espere um minuto e consulte só esses nomes; costuma ser outra busca rodando do mesmo IP.
- registro.br com erro ou status desconhecido: diga o número do status e sugira conferir o domínio no site. Não adivinhe.
