# Documentação do Projeto: FinAgent

## 1. O que é o FinAgent?
O FinAgent é um sistema de inteligência financeira automatizado projetado para processar dados contábeis (como balancetes e demonstrações de resultados) e gerar análises executivas, relatórios e indicadores de desempenho (KPIs). O sistema se baseia nas normas contábeis brasileiras (CVM/B3/IFRS) para realizar cálculos matemáticos e geração de documentos de auditoria visual (PDFs e XMLs).

## 2. Qual problema ele resolve e seus objetivos?
**Problema:** A análise financeira manual de balancetes mensais é demorada, suscetível a erros humanos, de difícil formatação cruzada e muitas vezes lenta, o que prejudica a tomada de decisão ágil pela diretoria.
**Objetivo:** Automatizar todo o pipeline de tratamento de dados contábeis. Desde a leitura de arquivos brutos (como Trial Balances) até a categorização de contas, modelagem das Demonstrações do Resultado do Exercício (DRE), cálculo de KPIs (EBITDA, ROIC, Margens) e elaboração de perfis de risco (Risk Score).

## 3. Quais os ganhos para o projeto?
- **Eficiência e Velocidade:** Relatórios gerados em questão de segundos e padronizados com alta qualidade para a diretoria e stakeholders.
- **Precisão Analítica:** Minimização do erro humano no cálculo de indicadores críticos.
- **Auditabilidade e Padronização:** O sistema pode gerar outputs em formato XML para integrações (machine-readable) e em PDF para consumo humano, facilitando processos de auditoria.

---

## 4. Escopo da Primeira Tela (Tela de Login)

O primeiro passo para tornar a interface do FinAgent acessível e segura é a plataforma de Login, que controlará o acesso ao motor de processamento.

### 4.1. Estrutura de Banco de Dados
A tabela de usuários (`Users`) deverá ter, como mínimo, os seguintes campos:
- `id` (Primary Key, Auto Increment)
- `nome_completo` (String)
- `email` (String, Unique) - Será utilizado como o "usuário" no momento do login.
- `senha_hash` (String) - Senha criptografada por segurança.
- `nivel_acesso` (Foreign Key / Integer) - Relacionado com a tabela de Perfil de Acesso.
- `is_active` (Boolean) - Se a conta do usuário está ativa.
- `data_criacao` (DateTime)

### 4.2. Definição do Nível de Acesso
Serão estabelecidos níveis e permissões por perfil (Role-Based Access Control):
- **Administrador:** Acesso total à plataforma, podendo gerenciar usuários, visualizar e gerar todos os relatórios, alterar regras do "engine" de geração de KPIs, bem como visualizar os painéis de auditoria.
- **Analista Financeiro:** Pode fazer a importação/upload dos balancetes, rodar o motor do FinAgent, extrair e visualizar os PDFs/planilhas do último período.
- **Gestor/Diretoria:** Perfil de acesso apenas de leitura (*View Only*) para o painel de resultados e aprovação de resumos.

### 4.3. Modelo de Layout
O layout e posicionamento estético da tela de login deverá transmitir modernidade e segurança corporativa:
- **Cores:** Fundo escuro ou tons de azul corporativo (navy blue, ou dark mode) para sensação de ambiente "premium", utilizando "Cards" brancos ou semi-transparentes (*glassmorphism*) para a região de formulário da tela, contrastando de forma elegante.
- **Estruturação:** O formulário centralizado, com logotipo da empresa ou sistema (FinAgent) no topo. Dois campos de input limpos com ícones auxiliares (um para `E-mail` e um para `Senha`), abaixo um botão destacado (ex: azul vibrante) escrito "Entrar". Adicionar um pequeno link discreto "Esqueceu a senha?".
- **Tipografia:** Fonte sem serifa moderna (como Inter, Roboto ou Open Sans), textos legíveis, espaçamento confortável (padding).

A implementação ocorrerá usando a estrutura do **Django** (Python) integrado ao **HTML/CSS** de forma responsiva.
