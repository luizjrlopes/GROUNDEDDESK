# GroundedDesk

**GroundedDesk** é uma plataforma de atendimento B2B multitenant com base de conhecimento governada e RAG orientado por evidências. O sistema integra tickets, filas, SLA, gestão de conhecimento, busca híbrida, respostas assistidas por IA e auditoria em um fluxo operacional único.

A arquitetura foi desenhada para manter as decisões críticas sob controle da aplicação: a IA auxilia na elaboração de respostas, mas não controla transições de tickets, autorização, envio de mensagens ou regras de negócio.

## Visão geral

O GroundedDesk combina operação de suporte e recuperação de conhecimento com rastreabilidade de ponta a ponta.

Principais capacidades:

- atendimento multitenant com isolamento por organização;
- autenticação JWT, RBAC e escopo de dados por tenant;
- tickets, filas, prioridades, SLA e transições explícitas de estado;
- comentários, respostas de atendentes e metadados de anexos;
- base de conhecimento com versionamento e reprocessamento;
- ingestão assíncrona de documentos;
- chunking e embeddings para recuperação semântica;
- busca híbrida lexical + vetorial;
- combinação de resultados por Reciprocal Rank Fusion (RRF);
- geração de respostas assistidas por IA com citações e groundedness score;
- revisão humana obrigatória antes do envio de respostas assistidas;
- fallback determinístico quando o provedor de IA está indisponível;
- trilha de auditoria para eventos de domínio, recuperação e IA.

## Arquitetura

O sistema é dividido em aplicação web, API HTTP, banco PostgreSQL e worker assíncrono.

```text
Browser / Next.js
        │ JWT
        ▼
FastAPI API
  │
  ├── autenticação e autorização
  ├── tickets e SLA
  ├── base de conhecimento
  ├── busca híbrida / RAG
  ├── assistência por IA
  └── auditoria
        │
        ▼
PostgreSQL + pgvector
  │
  ├── dados transacionais
  ├── documentos e chunks
  ├── embeddings
  ├── eventos de auditoria
  └── fila transacional de ingestão
        ▲
        │
   Python Worker
```

O PostgreSQL atua como armazenamento transacional e vetorial, reduzindo a quantidade de infraestrutura necessária e mantendo integridade relacional entre tickets, documentos, chunks, citações e eventos de auditoria.

## Stack

### Frontend

- Next.js 16
- React 19
- TypeScript
- App Router

### Backend

- Python 3.13
- FastAPI
- SQLAlchemy 2
- Pydantic
- JWT

### Dados e busca

- PostgreSQL 18
- pgvector
- busca lexical e vetorial
- Reciprocal Rank Fusion

### Processamento assíncrono

- worker Python
- fila transacional no PostgreSQL
- `FOR UPDATE SKIP LOCKED`

### Infraestrutura local

- Docker
- Docker Compose

## RAG orientado por evidências

O fluxo de recuperação prioriza rastreabilidade. O sistema recupera chunks autorizados da base de conhecimento, calcula sinais lexicais e vetoriais, combina os rankings e mantém as evidências associadas à resposta sugerida.

```text
Pergunta / contexto do ticket
        │
        ▼
Recuperação autorizada
        │
        ├── lexical score
        └── vector score
                │
                ▼
        Reciprocal Rank Fusion
                │
                ▼
       Evidências + citações
                │
                ▼
        Assistência por IA
                │
                ▼
          Revisão humana
                │
                ▼
              Envio
```

A camada de IA é substituível por provedor e possui implementação local determinística como padrão, permitindo executar o ambiente sem depender de serviços pagos.

## Segurança e governança

O GroundedDesk mantém as regras sensíveis fora do modelo de IA:

- autorização aplicada no servidor;
- isolamento de tenant na camada de dados;
- papéis distintos para operação, gestão, administração da base e auditoria;
- respostas assistidas exigem revisão humana;
- eventos relevantes são registrados para auditoria;
- falhas do provedor de IA não interrompem o fluxo principal de tickets.

## Executar localmente

### Pré-requisitos

- Docker
- Docker Compose

### Inicialização

```bash
cp .env.example .env
docker compose up --build
```

Após a inicialização:

- Aplicação web: `http://localhost:3000`
- API / OpenAPI: `http://localhost:8000/docs`

A API inicializa o schema e os dados locais necessários. O worker processa os jobs de ingestão armazenados no PostgreSQL.

## Estrutura do repositório

```text
GroundedDesk/
├── apps/
│   ├── api/              # FastAPI, domínio, persistência, worker e testes
│   └── web/              # Next.js e interface do usuário
├── docs/                 # Arquitetura, RAG, segurança e documentação técnica
├── scripts/              # Validações determinísticas do repositório
├── docker-compose.yml    # Ambiente local
└── .github/workflows/    # Integração contínua
```

## Validação

### Validação estrutural

```bash
python scripts/validate_repo.py
```

### Testes do backend

```bash
pip install ./apps/api
python -m unittest discover apps/api/tests -v
```

### Frontend

```bash
cd apps/web
npm ci
npm run typecheck
npm run build
```

O pipeline de CI executa as validações de backend e frontend a cada push para `main` e em pull requests.

## Documentação técnica

A documentação complementar está em:

- `docs/architecture.md`
- `docs/rag.md`
- `docs/security.md`
- `docs/demo.md`

## Licença

Este projeto é distribuído sob os termos definidos em `LICENSE`.
