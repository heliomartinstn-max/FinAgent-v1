# FinAgent — Motor de Inteligência Financeira
**UFG · Especialização em Sistemas e Agentes Inteligentes · Abril 2026**

> Sistema de análise financeira com pipeline de 7 agentes de IA, integração com Claude Sonnet API, dashboards Plotly e interface web Django.

---

## 🚀 Como rodar o projeto do zero

### Pré-requisitos
- **Python 3.11+** instalado ([python.org](https://python.org))
- **pip** (já vem com o Python)
- Conexão com internet (para baixar os pacotes)

---

### 1. Criar e ativar o ambiente virtual

```powershell
# Entrar na pasta do projeto
cd FinAgent-v1

# Criar o ambiente virtual
python -m venv .venv

# Ativar (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Ativar (Windows CMD)
.venv\Scripts\activate.bat

# Ativar (Linux / macOS)
source .venv/bin/activate
```

> ✅ Você verá `(.venv)` na frente do prompt.

---

### 2. Instalar as dependências

```powershell
pip install -r requirements.txt
```

---

### 3. Configurar as variáveis de ambiente

```powershell
# Copie o arquivo de exemplo
copy .env.example .env
```

Abra o `.env` e configure:
```env
SECRET_KEY=coloque-uma-chave-secreta-aqui
DEBUG=True
ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui   # opcional para o chat
```

> 💡 Para gerar uma SECRET_KEY segura:
> ```python
> python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
> ```

---

### 4. Criar o banco de dados

```powershell
python manage.py migrate
```

---

### 5. Criar o superusuário (administrador)

```powershell
python manage.py createsuperuser
```

Você precisará informar:
- **Username:** (pode ser qualquer nome, ex: `admin`)
- **E-mail:** (será o e-mail de login, ex: `admin@finagent.com`)
- **Senha:** (mínimo 8 caracteres)

---

### 6. Iniciar o servidor

```powershell
python manage.py runserver
```

Acesse no navegador: **http://127.0.0.1:8000**

---

## 🗺️ Mapa do Sistema

| URL | Descrição | Acesso |
|---|---|---|
| `/accounts/login/` | Tela de login | Público |
| `/` | Dashboard principal | Logado |
| `/empresas/` | Lista de empresas | Logado |
| `/empresas/nova/` | Cadastrar empresa | Logado |
| `/upload/` | Upload de balancete Excel | Logado |
| `/balancete/<id>/` | Visualizar balancete | Logado |
| `/dre/<id>/` | DRE Gerencial + Waterfall | Logado |
| `/analises/<id>/` | Análise Vertical & Horizontal | Logado |
| `/indicadores/<id>/` | KPIs + Gauge Charts | Logado |
| `/risco/<id>/` | Score de Risco + Radar Chart | Logado |
| `/projecoes/<id>/` | Forecast Prophet | Logado |
| `/chat/` | Chat IA (Claude Sonnet) | Logado |
| `/accounts/usuarios/` | Gestão de Usuários | **Admin** |
| `/admin/` | Painel Django Admin | **Admin** |

---

## 🏗️ Estrutura do Projeto

```
FinAgent-v1/
│
├── manage.py                 # Ponto de entrada Django
├── requirements.txt          # Dependências Python
├── .env.example              # Template de variáveis de ambiente
├── .gitignore
│
├── finagent_web/             # Configurações do projeto
│   ├── settings.py
│   └── urls.py
│
├── accounts/                 # 🔐 Autenticação + Gestão de Usuários
├── core/                     # 🏠 Dashboard + template base
├── empresas/                 # 🏢 CRUD de Empresas
├── contabil/                 # 📊 Upload e visualização de Balancetes
├── analises/                 # 📈 DRE, V&H, KPIs (Plotly)
├── risco/                    # ⚠️  Score de Risco + Claude AI
├── forecast/                 # 🔮 Projeções Prophet
└── chat/                     # 💬 Chat NLP (Claude Sonnet API)
```

---

## 🤖 Pipeline de Agentes

```
Upload Excel/CSV
      ↓
[Agente 1] Parser       → Normaliza o balancete
      ↓
[Agente 2] DRE Builder  → Monta a DRE Gerencial
      ↓
[Agente 3] Analyzer     → Análises Vertical e Horizontal
      ↓
[Agente 4] KPI Engine   → Liquidez, Rentabilidade, Endividamento
      ↓
[Agente 5] Risk Scorer  → Score ponderado + Narrativa Claude AI
      ↓
[Agente 6] Forecast     → Projeções Prophet (12+ meses)
      ↓
[Agente 7] Chat NLP     → Interface conversacional Claude Sonnet
```

---

## 👥 Níveis de Acesso

| Nível | Permissões |
|---|---|
| **ADMIN** | Acesso total — CRUD de usuários, todas as telas |
| **ANALISTA** | Upload, análise e relatórios financeiros |
| **GESTOR** | Visualização de dashboards e relatórios |

---

## 📦 Dependências Principais

| Pacote | Versão | Uso |
|---|---|---|
| Django | 6.0.5 | Framework web principal |
| pandas | 3.0.2 | Processamento de DataFrames contábeis |
| openpyxl | 3.1.5 | Leitura de arquivos Excel |
| plotly | 6.7.0 | Gráficos interativos (DRE, KPIs, Radar) |
| anthropic | ≥0.40 | SDK Claude API (instalar separado) |
| prophet | ≥1.1 | Forecast de séries temporais (instalar separado) |

Para instalar os opcionais:
```powershell
pip install anthropic prophet
```

---

## 🔑 Credenciais de Demonstração

Após `createsuperuser`, use o e-mail e senha que você definiu.

Ou, para criar um usuário de teste via shell:
```python
python manage.py shell
>>> from accounts.models import User
>>> User.objects.create_superuser(username='admin', email='admin@finagent.com', password='admin123', nome_completo='Administrador')
```

---

## ⚙️ Tecnologias

- **Backend:** Django 6.0, Python 3.11+
- **Banco de dados:** SQLite (dev) · PostgreSQL (produção)
- **Frontend:** Bootstrap 5, Bootstrap Icons, Plotly.js
- **IA:** Claude Sonnet API (Anthropic)
- **ML:** Prophet (Meta) para forecasting
- **Deploy:** Docker + Gunicorn + Nginx + PostgreSQL + Redis

---

*FinAgent — UFG Especialização em Sistemas e Agentes Inteligentes · Abril 2026*
