# Padrões por stack

Ponto de partida para os comandos, o `.gitignore`, os arquivos de `rules/` e as
armadilhas já conhecidas. **É ponto de partida, não verdade**: o que a entrevista
disser ganha de tudo o que está aqui, e armadilha que o projeto não tem não se
escreve (documento com aviso que não se aplica ensina a ignorar avisos).

Stack fora desta lista: siga a mesma forma — comandos literais, um arquivo de
regra por área com `paths:`, armadilhas com o sintoma antes da causa.

Os `paths:` abaixo supõem o layout de monorepo da casa (`backend/` e `frontend/`
lado a lado). Repositório de uma área só usa o layout que o gerador do stack
cria (`src/**`, `app/**`) — e se tudo é uma área só, a regra dela pode ficar sem
`paths:`, desde que caiba no orçamento das regras sempre carregadas.

## Ambiente — só o que a rodada 2 confirmou

O ambiente é resposta da entrevista, não suposição. Escreva no `workflow.md`
apenas o ramo que o usuário confirmou; os outros não existem para aquele
projeto.

**Windows + Docker Desktop** (o ramo com mais pegadinhas próprias):

- **Evento de filesystem não atravessa bind mount.** Hot reload que depende de
  watcher precisa de polling. E quando um fix "não funcionou", o primeiro passo é
  conferir nos logs se houve reload — várias horas já foram gastas corrigindo
  código que estava certo e nunca chegou a rodar.
- **`docker compose up -d <serviço>` não recria o container ao mudar o `.env`**:
  é preciso `--force-recreate`. Sem isso a variável nova simplesmente não existe
  lá dentro, e nada avisa.
- **Dependência nova precisa entrar no container**, não só no `package.json`/
  `pyproject.toml`, quando a pasta de dependências é volume próprio.
- Caminho com `\` e com espaço: comando que recebe caminho vai com aspas.

**Windows sem Docker**: caminho com `\` e com espaço entre aspas; PowerShell não
é bash (sem `&&` em algumas versões, sem `2>/dev/null`, sem here-string de bash);
fim de linha CRLF merece `.gitattributes` desde o primeiro commit.

**macOS, Linux, WSL ou remoto**: escreva o que o usuário descrever, e nada de
armadilha importada. Se ele não citar nenhuma, o `workflow.md` fica sem a seção
de ambiente — o que é melhor do que uma seção com avisos que não valem ali.

## Python — FastAPI / script / serviço

```sh
uv sync                      # instalar dependências
uv run pytest                # suíte de testes
uv run alembic upgrade head  # migrations (se houver banco)
docker compose up            # ambiente de dev completo
```

- `rules/`: `backend.md` com `paths: ["backend/**"]`. Com banco, vale uma seção
  só de modelos e migrations.
- `.gitignore`: `__pycache__/`, `*.py[cod]`, `.venv/`, `.env`, `.pytest_cache/`,
  `.ruff_cache/`, `dist/`, `*.egg-info/`.
- Armadilhas conhecidas: rodar teste do diretório errado gera falha em massa
  enganosa (fixar o cwd na regra); `create_all` fora do banco de teste esconde
  migration faltando; chamada externa sem timeout segura o processo até reiniciar.
- Com Docker: migration roda no host se o compose só faz bind mount do código —
  senão a versão de dentro do container é a congelada na imagem, e o erro
  (`Can't locate revision`) não fala disso.

## Node — React + Vite

```sh
npm run dev
npm run build                # é o que valida um bloco
npm run lint
```

- `rules/`: `frontend.md` com `paths: ["frontend/**"]`.
- `.gitignore`: `node_modules/`, `dist/`, `.env*`, `*.local`, `.vite/`.
- Armadilhas conhecidas: no Docker, o Vite precisa de polling (`usePolling` no
  `vite.config`) porque o watcher não vê a mudança pelo bind mount; dependência
  nova exige reinstalar dentro do container quando `node_modules` é volume
  próprio; rota nova entra como `lazy` desde o começo (é mais barato do que
  descobrir o bundle grande depois).

## Next.js

```sh
npm run dev
npm run build                # valida o bloco (e é onde erro de server/client aparece)
```

- `rules/`: `frontend.md` com `paths: ["app/**", "src/**", "components/**"]`
  (ou o prefixo do monorepo), e uma seção sobre a fronteira server/client — é
  onde quase todo erro desse stack nasce.
- `.gitignore`: `node_modules/`, `.next/`, `out/`, `.env*`, `.vercel/`.
- Armadilha: segredo em componente de cliente vaza para o bundle. Variável
  pública tem prefixo próprio, e tudo que não tem prefixo é segredo por
  definição.

## Expo / React Native

```sh
npm start                    # Metro
npm run android
npx expo export -p android   # compila o bundle: é o "build" que valida um bloco
```

- `rules/`: `mobile.md` com `paths: ["app/**", "src/**", "app.json",
  "metro.config.js"]` — a configuração do Metro entra porque é nela que mora
  metade das armadilhas abaixo.
- `.gitignore`: `node_modules/`, `.expo/`, `dist/`, `*.jks`, `*.keystore`,
  `google-services.json` se contiver credencial, `.env*`.
- Armadilhas conhecidas, cada uma já paga em dias de depuração: pacote com
  código nativo exige **development build novo** — o Metro serve o JS sem
  reclamar e o erro só aparece no aparelho; push não funciona no Expo Go nem em
  emulador; mudança em `app.json`/`metro.config.js` pede `--clear`, senão o Metro
  serve a configuração antiga em silêncio; celular físico não enxerga o
  `localhost` do Docker da máquina.
- Se usar NativeWind: cor só por token, nunca literal no JSX (literal não troca
  com o tema), e classe que gere valor em porcentagem merece conferência — o
  React Native descarta o estilo inteiro do componente ao receber `%` como
  string em propriedade de layout.

## CLI / script / automação

```sh
uv run <script>.py           # ou: node <script>.mjs
```

- `rules/`: um único `workflow.md` costuma bastar. Área extra só quando existir
  de verdade.
- Repositório de operação (infra, painéis, APIs de terceiro) quase não tem
  pasta por assunto: o conhecimento de "como operar o Coolify" não mora em
  arquivo nenhum do repo. Isso é skill de projeto (`.claude/skills/<tema>/`),
  não regra sem `paths:` — senão o manual de cada painel entra em toda sessão.
- Armadilha: script que mexe em arquivo do usuário precisa de modo de simulação
  (`--dry-run`) antes de ter modo de execução. É a diferença entre um erro
  irritante e um erro irreversível.

## Projeto com repositório irmão

Quando a rodada 1 revelar dependência entre repositórios (um backend e um app,
um serviço e seu cliente), o CLAUDE.md ganha uma seção própria — algo como "a
regra que sustenta os dois repositórios" — dizendo:

- qual arquivo é cópia adaptada de qual, e quais são exatamente as adaptações;
- o que quebra **em silêncio** quando um lado muda sozinho (o caso perigoso não é
  o que quebra no mesmo commit, é o que só falha em produção, no aparelho de
  quem está usando);
- o comando que existe para pegar isso antes — e se ele ainda não existe, ele é
  um bloco do TASKS.md.
