# setup.ps1 — Configuracao automatica do FinAgent
# Execute este script uma unica vez apos extrair o ZIP
# Comando: powershell -ExecutionPolicy Bypass -File setup.ps1

Write-Host ""
Write-Host "  FinAgent - Setup Automatico" -ForegroundColor Cyan
Write-Host "  UFG - Especializacao em Sistemas e Agentes Inteligentes" -ForegroundColor Cyan
Write-Host ""

# 1. Verificar Python
Write-Host "[1/5] Verificando Python..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Python nao encontrado. Instale em https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "      OK: $pythonVersion" -ForegroundColor Green

# 2. Criar ambiente virtual
Write-Host "[2/5] Criando ambiente virtual (.venv)..." -ForegroundColor Yellow
python -m venv .venv
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Falha ao criar o ambiente virtual." -ForegroundColor Red
    exit 1
}
Write-Host "      OK: .venv criado." -ForegroundColor Green

# 3. Instalar dependencias
Write-Host "[3/5] Instalando dependencias (requirements.txt)..." -ForegroundColor Yellow
.venv\Scripts\pip.exe install -r requirements.txt --quiet
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Falha ao instalar dependencias." -ForegroundColor Red
    exit 1
}
Write-Host "      OK: Dependencias instaladas." -ForegroundColor Green

# 4. Configurar .env (copia o exemplo se nao existir)
Write-Host "[4/5] Configurando variaveis de ambiente..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Host "      OK: .env criado a partir do .env.example." -ForegroundColor Green
    Write-Host "      ATENCAO: Edite o .env e coloque sua ANTHROPIC_API_KEY para usar o Chat IA." -ForegroundColor Yellow
} else {
    Write-Host "      OK: .env ja existe, mantendo o atual." -ForegroundColor Green
}

# 5. Verificar banco de dados
Write-Host "[5/5] Verificando banco de dados..." -ForegroundColor Yellow
if (Test-Path "db.sqlite3") {
    Write-Host "      OK: Banco de dados encontrado com dados de demonstracao." -ForegroundColor Green
} else {
    Write-Host "      Banco nao encontrado. Criando..." -ForegroundColor Yellow
    .venv\Scripts\python.exe manage.py migrate --run-syncdb
    Write-Host "      OK: Banco criado. Crie um superusuario com:" -ForegroundColor Green
    Write-Host "          .venv\Scripts\python.exe manage.py createsuperuser" -ForegroundColor White
}

# Resumo final
Write-Host ""
Write-Host "  SETUP CONCLUIDO COM SUCESSO!" -ForegroundColor Green
Write-Host ""
Write-Host "  Para iniciar o servidor, execute:" -ForegroundColor White
Write-Host "    .venv\Scripts\Activate.ps1" -ForegroundColor Cyan
Write-Host "    python manage.py runserver" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Acesse no navegador:" -ForegroundColor White
Write-Host "    http://127.0.0.1:8000/accounts/login/" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Credenciais de demonstracao:" -ForegroundColor White
Write-Host "    E-mail: admin@finagent.com" -ForegroundColor Cyan
Write-Host "    Senha : admin123" -ForegroundColor Cyan
Write-Host ""
