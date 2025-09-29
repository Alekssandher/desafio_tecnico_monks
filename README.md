# Dashboard de Métricas - Desafio Técnico Monks

## 📑 Índice

- [Alterações nos dados CSV](#alterações-nos-dados-csv)
- [Credenciais de Acesso](#credenciais-de-acesso)
  - [Usuário Admin](#usuário-admin)
  - [Usuário Comum](#usuário-comum)
- [Funcionalidades](#funcionalidades)
- [🏗️ Arquitetura](#-arquitetura)
  - [Backend (Python)](#backend-python)
  - [Frontend](#frontend)
  - [Infraestrutura](#infraestrutura)
- [Como Executar](#como-executar)
  - [Pré-requisitos](#pré-requisitos)
  - [Opção 1: Execução com Docker (Recomendado)](#opção-1-execução-com-docker-recomendado)
  - [Opção 2: Execução Local (Desenvolvimento)](#opção-2-execução-local-desenvolvimento)
- [📊 Endpoints da API](#-endpoints-da-api)
- [🗂️ Estrutura do Projeto](#️-estrutura-do-projeto)
- [🛠️ Tecnologias Utilizadas](#️-tecnologias-utilizadas)
- [⚡ Performance](#-performance)
- [🔒 Segurança](#-segurança)
- [📝 Comandos Úteis](#-comandos-úteis)
- [🧪 Testando a API](#-testando-a-api)
- [📦 Dados de Exemplo](#-dados-de-exemplo)
- [👨‍💻 Desenvolvedor](#-desenvolvedor)
  
### Alterações nos dados CSV
Conforme dito, foram feitas alterações no arquivo `users.csv` para que atendesse aos requisitos do desafio. As senhas foram substítuidas por valores hash e foi adicionado um campo de email a tabela.

## Credenciais de Acesso

### Usuário Admin
- **Email**: user1@user.com
- **Senha**: admin1234
- **Privilégios**: Visualiza todas as colunas, incluindo "cost_micros"

### Usuário Comum
- **Email**: user2@user.com
- **Senha**: user1234
- **Privilégios**: Visualiza todas as colunas, exceto "cost_micros"
  
### Funcionalidades

- ✅ Sistema de login com email e senha (JWT)
- ✅ Visualização de métricas em formato tabular
- ✅ Filtros por período (data inicial e final)
- ✅ Ordenação por qualquer coluna
- ✅ Controle de acesso: coluna "cost_micros" visível apenas para admins
- ✅ Paginação de resultados
- ✅ Dashboard com métricas agregadas
- ✅ Duas fontes de dados: CSV e MySQL

## 🏗️ Arquitetura

### Backend (Python)
- **Framework**: FastAPI
- **Autenticação**: JWT (JSON Web Tokens)
- **Processamento de Dados**: Polars (CSV) e MySQL (Database)
- **Documentação API**: Scalar

### Frontend
- **Stack**: HTML, CSS e JavaScript Vanilla
- **Servidor**: Nginx

### Infraestrutura
- **Containerização**: Docker e Docker Compose
- **Banco de Dados**: MySQL 8.0

## Como Executar

### Pré-requisitos

- Docker e Docker Compose instalados
- Porta 8000 (API), 8080 (Frontend) e 3307 (MySQL) disponíveis

### Opção 1: Execução com Docker (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/Alekssandher/desafio_tecnico_monks/
cd desafio-tecnico-monks

# Inicie todos os serviços
docker-compose up --build
```

Aguarde alguns instantes para que o banco de dados seja inicializado e o seed seja executado.

**Acesse:**
- Frontend: http://localhost:8080
- API: http://localhost:8000
- Documentação: http://localhost:8000/scalar

### Opção 2: Execução Local (Desenvolvimento)

#### 1. Configure o Banco de Dados
```
Crie um banco de dados MySql em sua máquina para conexão.
```
#### 2. Configure o .env

```bash
# Configure o arquivo .env conforme o .env.example

# JWT
SECRET_KEY = "super-ultra-blaster-secret-key"          
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 180

# DATABASE
DB_URL = "localhost"
DB_PORT = 8000
DB_USER = "root"
DB_PASSWORD = "batatinha22"
DB_NAME = "desafio_monks"
```

#### 2. Configure e Execute a API

```bash
# Instale as dependências
make install

# Popule o banco de dados com os valores do arquivo metrics.csv
make seed

# Execute a API
make run
```

#### 3. Execute o Frontend

```bash
# Opção 1: Usando Python
cd frontend
python -m http.server 8080

# Opção 2: Usando qualquer servidor web de sua preferência
```

## 📊 Endpoints da API

### Autenticação
```
POST /login
Body: email, password (form-data)
Response: { "token": "jwt_token" }
```

### Métricas (CSV)
```
GET /metrics/csv
Headers: Authorization: Bearer <token>
Query Params: start_date, end_date, limit, offset, order_by, descending
```

### Métricas (Database)
```
GET /metrics/db
Headers: Authorization: Bearer <token>
Query Params: start_date, end_date, limit, offset, order_by, descending
```

### Health Check
```
GET /healthcheck
Response: { "status": "ok" }
```

## 🗂️ Estrutura do Projeto

```
.
├── api/
│   ├── auth/              # Autenticação e autorização
│   ├── config/            # Configurações da aplicação
│   ├── data/              # Arquivos CSV (users e metrics)
│   ├── dtos/              # Data Transfer Objects
│   ├── models/            # Modelos Pydantic
│   ├── repositories/      # Camada de acesso aos dados
│   ├── scripts/           # Scripts utilitários
│   ├── seeds/             # Seeds do banco de dados
│   └── main.py            # Aplicação FastAPI
├── frontend/
│   ├── index.html         # Interface principal
│   ├── scripts.js         # Lógica da aplicação
│   └── style.css          # Estilos
├── docker-compose.yml     # Orquestração dos containers
├── Dockerfile             # Imagem da API
├── pyproject.toml         # Dependências Python (Poetry)
└── Makefile               # Comandos úteis
```

## 🛠️ Tecnologias Utilizadas

### Backend
- FastAPI 0.117.1
- Polars 1.33.1 (processamento de CSV)
- MySQL Connector 9.4.0
- Python-Jose (JWT)
- Passlib (hash de senhas)
- Uvicorn (ASGI server)

### Frontend
- JavaScript 
- CSS
- HTML

### DevOps
- Docker & Docker Compose
- Poetry (gerenciamento de dependências)
- Nginx (servidor web)

## ⚡ Performance

A aplicação implementa middleware para medição de tempo de resposta:
- Header `X-Process-Time-Ms` em todas as respostas

## 🔒 Segurança

- Senhas armazenadas com hash bcrypt
- Autenticação via JWT
- Controle de acesso baseado em roles
- Validação de dados com Pydantic

## 📝 Comandos Úteis

```bash
# Iniciar aplicação
make start

# Executar apenas a API
make run

# Executar seed do banco
make seed

# Limpar cache Python
make clean

# Instalar dependências
make install
```

## 🧪 Testando a API

```bash
Entre na url da api ex: localhost:8000/scalar e veja a documentação scalar.
```

## 📦 Dados de Exemplo

O arquivo `api/data/metrics.csv` contém métricas de campanhas com as seguintes colunas:
- `date`: Data da métrica
- `account_id`: ID da conta
- `campaign_id`: ID da campanha
- `clicks`: Número de cliques
- `conversions`: Número de conversões
- `impressions`: Número de impressões
- `interactions`: Número de interações
- `cost_micros`: Custo em micros (visível apenas para admins)

### Erro de permissão no MySQL
```bash
# Reinicie os containers
docker-compose down -v
docker-compose up --build
```

## 👨‍💻 Desenvolvedor

Projeto desenvolvido por Alekssandher para o processo seletivo de estágio em engenharia na Monks.

---

**Nota**: Este projeto foi desenvolvido como parte de um desafio técnico e serve como demonstração de habilidades em desenvolvimento full-stack com Python, FastAPI, Docker e JavaScript.
