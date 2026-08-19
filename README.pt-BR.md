# GroundedDesk

[English](README.md) | [Português](README.pt-BR.md)

**GroundedDesk** é uma plataforma de atendimento B2B multitenant com base de conhecimento governada e RAG orientado por evidências. O sistema integra tickets, filas, SLA, gestão de conhecimento, busca híbrida, respostas assistidas por IA e auditoria em um fluxo operacional único.

A arquitetura foi desenhada para manter as decisões críticas sob controle da aplicação: a IA auxilia na elaboração de respostas, mas não controla transições de tickets, autorização, envio de mensagens ou regras de negócio.

## Visão geral

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
- respostas assistidas por IA com citações e groundedness score;
- revisão humana obrigatória antes do envio;
- fallback determinístico quando o provedor de IA está indisponível;
- trilha de auditoria para eventos de domínio, recuperação e IA.

## Arquitetura

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

O PostgreSQL atua como armazenamento transacional e vetorial, reduzindo infraestrutura e mantendo integridade relacional entre tickets, documentos, chunks, citações e eventos de auditoria.

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

A camada de IA é substituível por provedor e possui implementação local determinística como padrão, permitindo executar o ambiente sem serviços pagos.

## Segurança e governança

- autorização aplicada no servidor;
- isolamento de tenant na camada de dados;
- papéis distintos para operação, gestão, administração da base e auditoria;
- respostas assistidas exigem revisão humana;
- eventos relevantes são registrados para auditoria;
- falhas do provedor de IA não interrompem o fluxo principal de tickets.

## Executar localmente

```bash
cp .env.example .env
docker compose up --build
```

- Web: `http://localhost:3000`
- API / OpenAPI: `http://localhost:8000/docs`

A API inicializa o schema e os dados locais necessários. O worker processa os jobs de ingestão armazenados no PostgreSQL.

## Estrutura do repositório

```text
GroundedDesk/
├── apps/
│   ├── api/              # FastAPI, domínio, persistência, worker e testes
│   └── web/              # Next.js e interface do usuário
├── docs/                 # Arquitetura, RAG, segurança e documentação técnica
├── scripts/              # Validações determinísticas
├── docker-compose.yml
└── .github/workflows/
```

## Validação

```bash
python scripts/validate_repo.py
pip install ./apps/api
python -m unittest discover apps/api/tests -v
cd apps/web
npm ci
npm run typecheck
npm run build
```

O CI executa as validações de backend e frontend em pushes para `main` e pull requests.

## Documentação técnica

- `docs/architecture.md`
- `docs/rag.md`
- `docs/security.md`
- `docs/demo.md`

## Licença

Este projeto é distribuído sob os termos definidos em `LICENSE`.
