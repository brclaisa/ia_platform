# Plataforma IA MultiAgente

Assistente inteligente baseado em LLMs com verificação de compliance, RAG (Retrieval-Augmented Generation) e arquitetura multi-agente orquestrada por LangGraph.

## Arquitetura

O sistema utiliza um **grafo de estados LangGraph** com 5 nodes especializados:

```
Pergunta → [Compliance] → [Router] → [RAG ou Direct] → [Synthesizer] → Resposta
```

1. **Compliance**: Verifica se a pergunta toca em tópicos proibidos (política, religião, violência, drogas, demissões) usando dupla camada de segurança (regex + LLM).
2. **Router**: Decide se a resposta deve usar documentos internos (RAG) ou conhecimento geral (Direct).
3. **RAG**: Busca documentos relevantes no ChromaDB e gera resposta fundamentada no contexto.
4. **Direct**: Responde diretamente usando o LLM para perguntas de conhecimento geral.
5. **Synthesizer**: Formata a resposta final de maneira clara e profissional.

## Stack Técnica

| Componente | Tecnologia |
|---|---|
| LLM | OpenAI GPT-4o-mini |
| Embeddings | OpenAI text-embedding-3-small |
| Orquestrador | LangGraph |
| Vector Store | ChromaDB |
| API | FastAPI |
| Interface | Streamlit |

## Executando com Docker (recomendado)

### Pré-requisitos

- Docker e Docker Compose
- Chave de API da OpenAI

### Setup

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd ia_platform

# Configure as variáveis de ambiente
copy .env.example .env       # Windows
# cp .env.example .env       # Linux/Mac
```

Edite o arquivo `.env` com sua chave da OpenAI:

```
OPENAI_API_KEY=sk-sua-chave-aqui
```

### Subir os serviços

```bash
docker compose up --build
```

Isso inicia dois containers:

| Serviço | URL | Descrição |
|---|---|---|
| **api** | http://localhost:8000 | FastAPI (backend) |
| **ui** | http://localhost:8501 | Streamlit (interface) |

A documentação interativa da API estará em: http://localhost:8000/docs

### Parar os serviços

```bash
docker compose down
```

Para remover também o volume do ChromaDB:

```bash
docker compose down -v
```

### Ingestão de Documentos

Coloque seus documentos (`.txt`, `.md`, `.pdf`) na pasta `documents/` antes de subir os containers, ou use a interface Streamlit para upload. Para processar todos os documentos via API:

```bash
curl -X POST http://localhost:8000/documents/ingest-all
```

## Executando sem Docker

### Pré-requisitos

- Python 3.11+
- Chave de API da OpenAI

### Instalação

```bash
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/Mac

pip install -r requirements.txt

copy .env.example .env       # Windows
# cp .env.example .env       # Linux/Mac
```

### API (FastAPI)

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Interface Web (Streamlit)

Em outro terminal (com a API rodando):

```bash
streamlit run app/ui/streamlit_app.py
```

Acesse: http://localhost:8501

## Endpoints da API

| Método | Endpoint | Descrição |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/ask` | Envia uma pergunta ao assistente |
| POST | `/documents` | Upload de documento para ingestão |
| POST | `/documents/ingest-all` | Processa todos os documentos da pasta |

### Exemplo de uso

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "Qual a política de férias da empresa?"}'
```

## Testes

```bash
pip install pytest pytest-asyncio
pytest tests/ -v
```

## Estrutura do Projeto

```
ia_platform/
├── app/
│   ├── main.py                  # FastAPI
│   ├── config.py                # Configurações
│   ├── models.py                # Schemas Pydantic
│   ├── agents/
│   │   ├── graph.py             # Grafo LangGraph
│   │   ├── state.py             # Estado do grafo
│   │   ├── nodes/               # Nodes do grafo
│   │   │   ├── compliance.py
│   │   │   ├── router.py
│   │   │   ├── rag.py
│   │   │   ├── direct.py
│   │   │   └── synthesizer.py
│   │   └── prompts/             # Prompts por responsabilidade
│   ├── rag/
│   │   ├── ingestion.py         # Carregamento e chunking
│   │   ├── embeddings.py        # Embeddings OpenAI
│   │   └── retriever.py         # Busca no ChromaDB
│   └── ui/
│       └── streamlit_app.py     # Interface web
├── documents/                   # Documentos para RAG
├── tests/                       # Testes automatizados
├── Dockerfile                   # Multi-stage (api + ui)
├── docker-compose.yml           # Orquestração dos serviços
├── requirements.txt
└── .env.example
```
