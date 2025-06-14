#!/bin/bash

# Script de Instalação Automatizada
# Sistema de Agendamentos para Salões de Beleza e Barbearias
# Versão: 1.0

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir mensagens coloridas
print_message() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[AVISO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERRO]${NC} $1"
}

print_header() {
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Verificar se está rodando como root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "Este script não deve ser executado como root!"
        print_message "Execute como usuário normal: ./install.sh"
        exit 1
    fi
}

# Detectar sistema operacional
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if command -v apt-get &> /dev/null; then
            OS="ubuntu"
            PACKAGE_MANAGER="apt"
        elif command -v yum &> /dev/null; then
            OS="centos"
            PACKAGE_MANAGER="yum"
        else
            print_error "Sistema Linux não suportado"
            exit 1
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        PACKAGE_MANAGER="brew"
    else
        print_error "Sistema operacional não suportado: $OSTYPE"
        exit 1
    fi
    
    print_message "Sistema detectado: $OS"
}

# Verificar dependências
check_dependencies() {
    print_header "VERIFICANDO DEPENDÊNCIAS"
    
    # Verificar Python
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_message "Python encontrado: $PYTHON_VERSION"
    else
        print_error "Python 3 não encontrado!"
        INSTALL_PYTHON=true
    fi
    
    # Verificar Node.js
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version)
        print_message "Node.js encontrado: $NODE_VERSION"
    else
        print_error "Node.js não encontrado!"
        INSTALL_NODE=true
    fi
    
    # Verificar Git
    if command -v git &> /dev/null; then
        print_message "Git encontrado"
    else
        print_error "Git não encontrado!"
        INSTALL_GIT=true
    fi
}

# Instalar dependências
install_dependencies() {
    if [[ "$INSTALL_PYTHON" == true ]] || [[ "$INSTALL_NODE" == true ]] || [[ "$INSTALL_GIT" == true ]]; then
        print_header "INSTALANDO DEPENDÊNCIAS"
        
        if [[ "$OS" == "ubuntu" ]]; then
            print_message "Atualizando repositórios..."
            sudo apt update
            
            if [[ "$INSTALL_PYTHON" == true ]]; then
                print_message "Instalando Python..."
                sudo apt install -y python3 python3-pip python3-venv
            fi
            
            if [[ "$INSTALL_NODE" == true ]]; then
                print_message "Instalando Node.js..."
                curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
                sudo apt-get install -y nodejs
            fi
            
            if [[ "$INSTALL_GIT" == true ]]; then
                print_message "Instalando Git..."
                sudo apt install -y git
            fi
            
        elif [[ "$OS" == "centos" ]]; then
            if [[ "$INSTALL_PYTHON" == true ]]; then
                print_message "Instalando Python..."
                sudo yum install -y python3 python3-pip
            fi
            
            if [[ "$INSTALL_NODE" == true ]]; then
                print_message "Instalando Node.js..."
                curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
                sudo yum install -y nodejs
            fi
            
            if [[ "$INSTALL_GIT" == true ]]; then
                print_message "Instalando Git..."
                sudo yum install -y git
            fi
            
        elif [[ "$OS" == "macos" ]]; then
            if ! command -v brew &> /dev/null; then
                print_message "Instalando Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi
            
            if [[ "$INSTALL_PYTHON" == true ]]; then
                print_message "Instalando Python..."
                brew install python
            fi
            
            if [[ "$INSTALL_NODE" == true ]]; then
                print_message "Instalando Node.js..."
                brew install node
            fi
            
            if [[ "$INSTALL_GIT" == true ]]; then
                print_message "Instalando Git..."
                brew install git
            fi
        fi
    fi
}

# Configurar backend
setup_backend() {
    print_header "CONFIGURANDO BACKEND"
    
    cd salon_booking_api
    
    print_message "Criando ambiente virtual Python..."
    python3 -m venv venv
    
    print_message "Ativando ambiente virtual..."
    source venv/bin/activate
    
    print_message "Instalando dependências Python..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    print_message "Configurando variáveis de ambiente..."
    if [[ ! -f .env ]]; then
        cat > .env << EOF
# Configurações do Flask
FLASK_ENV=development
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
DEBUG=True

# Banco de Dados
DATABASE_URL=sqlite:///salon_booking.db

# JWT
JWT_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
JWT_ACCESS_TOKEN_EXPIRES=3600

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Email (configurar conforme necessário)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=
MAIL_PASSWORD=
EOF
        print_message "Arquivo .env criado com configurações padrão"
    else
        print_warning "Arquivo .env já existe, mantendo configurações atuais"
    fi
    
    print_message "Inicializando banco de dados..."
    python src/main.py db init 2>/dev/null || true
    python src/main.py db migrate 2>/dev/null || true
    python src/main.py db upgrade 2>/dev/null || true
    
    cd ..
    print_message "Backend configurado com sucesso!"
}

# Configurar frontend
setup_frontend() {
    print_header "CONFIGURANDO FRONTEND"
    
    cd salon-booking-frontend
    
    print_message "Instalando dependências Node.js..."
    npm install
    
    print_message "Configurando variáveis de ambiente..."
    if [[ ! -f .env.local ]]; then
        cat > .env.local << EOF
REACT_APP_API_URL=http://localhost:5000/api/v1
REACT_APP_ENVIRONMENT=development
EOF
        print_message "Arquivo .env.local criado"
    else
        print_warning "Arquivo .env.local já existe, mantendo configurações atuais"
    fi
    
    cd ..
    print_message "Frontend configurado com sucesso!"
}

# Criar scripts de execução
create_scripts() {
    print_header "CRIANDO SCRIPTS DE EXECUÇÃO"
    
    # Script para iniciar backend
    cat > start_backend.sh << 'EOF'
#!/bin/bash
cd salon_booking_api
source venv/bin/activate
echo "Iniciando backend na porta 5000..."
python src/main.py
EOF
    chmod +x start_backend.sh
    
    # Script para iniciar frontend
    cat > start_frontend.sh << 'EOF'
#!/bin/bash
cd salon-booking-frontend
echo "Iniciando frontend na porta 3000..."
npm start
EOF
    chmod +x start_frontend.sh
    
    # Script para iniciar ambos
    cat > start_system.sh << 'EOF'
#!/bin/bash

# Função para cleanup
cleanup() {
    echo "Parando serviços..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Capturar Ctrl+C
trap cleanup SIGINT

echo "Iniciando Sistema de Agendamentos..."
echo "=================================="

# Iniciar backend
echo "Iniciando backend..."
cd salon_booking_api
source venv/bin/activate
python src/main.py &
BACKEND_PID=$!
cd ..

# Aguardar backend inicializar
sleep 5

# Iniciar frontend
echo "Iniciando frontend..."
cd salon-booking-frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "Sistema iniciado com sucesso!"
echo "Frontend: http://localhost:3000"
echo "Backend:  http://localhost:5000"
echo ""
echo "Pressione Ctrl+C para parar o sistema"

# Aguardar
wait
EOF
    chmod +x start_system.sh
    
    print_message "Scripts de execução criados:"
    print_message "  - start_backend.sh  (apenas backend)"
    print_message "  - start_frontend.sh (apenas frontend)"
    print_message "  - start_system.sh   (sistema completo)"
}

# Testar instalação
test_installation() {
    print_header "TESTANDO INSTALAÇÃO"
    
    # Testar backend
    print_message "Testando backend..."
    cd salon_booking_api
    source venv/bin/activate
    timeout 10 python src/main.py &
    BACKEND_PID=$!
    sleep 5
    
    if curl -f http://localhost:5000/api/v1/health &>/dev/null; then
        print_message "✓ Backend funcionando corretamente"
    else
        print_warning "⚠ Backend pode não estar funcionando corretamente"
    fi
    
    kill $BACKEND_PID 2>/dev/null || true
    cd ..
    
    # Testar frontend
    print_message "Testando frontend..."
    cd salon-booking-frontend
    if npm run build &>/dev/null; then
        print_message "✓ Frontend compila corretamente"
    else
        print_warning "⚠ Problemas na compilação do frontend"
    fi
    cd ..
}

# Exibir informações finais
show_final_info() {
    print_header "INSTALAÇÃO CONCLUÍDA"
    
    echo -e "${GREEN}✓ Sistema instalado com sucesso!${NC}"
    echo ""
    echo -e "${BLUE}Como usar:${NC}"
    echo "  1. Para iniciar o sistema completo:"
    echo "     ./start_system.sh"
    echo ""
    echo "  2. Para iniciar apenas o backend:"
    echo "     ./start_backend.sh"
    echo ""
    echo "  3. Para iniciar apenas o frontend:"
    echo "     ./start_frontend.sh"
    echo ""
    echo -e "${BLUE}URLs de acesso:${NC}"
    echo "  Frontend: http://localhost:3000"
    echo "  Backend:  http://localhost:5000"
    echo ""
    echo -e "${BLUE}Documentação:${NC}"
    echo "  - Manual do Usuário: manual_usuario.pdf"
    echo "  - Guia de Instalação: guia_instalacao.pdf"
    echo "  - Documentação da API: documentacao_api.pdf"
    echo ""
    echo -e "${BLUE}Suporte:${NC}"
    echo "  Email: suporte@sistemasalao.com.br"
    echo "  WhatsApp: (11) 99999-9999"
    echo ""
    echo -e "${GREEN}Bom uso do sistema!${NC} 🚀"
}

# Função principal
main() {
    print_header "INSTALAÇÃO DO SISTEMA DE AGENDAMENTOS"
    print_message "Iniciando instalação automatizada..."
    
    check_root
    detect_os
    check_dependencies
    install_dependencies
    setup_backend
    setup_frontend
    create_scripts
    test_installation
    show_final_info
}

# Executar instalação
main "$@"

