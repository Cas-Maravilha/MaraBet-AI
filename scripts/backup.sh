#!/bin/bash
# Script de backup para MaraBet AI

set -e

echo "💾 MARABET AI - BACKUP"
echo "====================="

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para log
log() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

# Função para erro
error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

# Função para sucesso
success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

# Função para warning
warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Configurações
BACKUP_DIR="backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_NAME="marabet_ai_backup_$TIMESTAMP"
FULL_BACKUP_PATH="$BACKUP_DIR/$BACKUP_NAME"

# Criar diretório de backup
create_backup_dir() {
    log "Criando diretório de backup..."
    mkdir -p "$FULL_BACKUP_PATH"
    success "Diretório criado: $FULL_BACKUP_PATH"
}

# Backup do banco de dados
backup_database() {
    log "Fazendo backup do banco de dados..."
    
    if [ -f "data/sports_data.db" ]; then
        cp data/sports_data.db "$FULL_BACKUP_PATH/"
        success "Banco de dados copiado"
        
        # Mostrar informações do banco
        DB_SIZE=$(du -h data/sports_data.db | cut -f1)
        log "Tamanho do banco: $DB_SIZE"
    else
        warning "Banco de dados não encontrado"
    fi
}

# Backup dos logs
backup_logs() {
    log "Fazendo backup dos logs..."
    
    if [ -d "logs" ]; then
        cp -r logs "$FULL_BACKUP_PATH/"
        success "Logs copiados"
        
        # Mostrar informações dos logs
        LOG_SIZE=$(du -sh logs | cut -f1)
        LOG_COUNT=$(find logs -name "*.log" | wc -l)
        log "Tamanho dos logs: $LOG_SIZE ($LOG_COUNT arquivos)"
    else
        warning "Diretório de logs não encontrado"
    fi
}

# Backup dos relatórios
backup_reports() {
    log "Fazendo backup dos relatórios..."
    
    if [ -d "reports" ]; then
        cp -r reports "$FULL_BACKUP_PATH/"
        success "Relatórios copiados"
        
        # Mostrar informações dos relatórios
        REPORT_COUNT=$(find reports -name "*.txt" -o -name "*.pdf" | wc -l)
        log "Relatórios encontrados: $REPORT_COUNT"
    else
        warning "Diretório de relatórios não encontrado"
    fi
}

# Backup da configuração
backup_config() {
    log "Fazendo backup da configuração..."
    
    # Backup do .env
    if [ -f ".env" ]; then
        cp .env "$FULL_BACKUP_PATH/"
        success "Arquivo .env copiado"
    else
        warning "Arquivo .env não encontrado"
    fi
    
    # Backup dos arquivos de configuração
    if [ -d "settings" ]; then
        cp -r settings "$FULL_BACKUP_PATH/"
        success "Configurações copiadas"
    fi
    
    # Backup do docker-compose.yml
    if [ -f "docker-compose.yml" ]; then
        cp docker-compose.yml "$FULL_BACKUP_PATH/"
        success "Docker Compose copiado"
    fi
}

# Backup dos modelos de ML
backup_models() {
    log "Fazendo backup dos modelos de ML..."
    
    if [ -d "ml" ]; then
        cp -r ml "$FULL_BACKUP_PATH/"
        success "Modelos de ML copiados"
    else
        warning "Diretório de ML não encontrado"
    fi
    
    # Backup de modelos treinados (se existirem)
    if [ -d "models" ]; then
        cp -r models "$FULL_BACKUP_PATH/"
        success "Modelos treinados copiados"
    fi
}

# Backup dos dados de cache
backup_cache() {
    log "Fazendo backup dos dados de cache..."
    
    if [ -d "data" ]; then
        # Copiar apenas arquivos de cache, não o banco principal
        find data -name "*.cache" -o -name "*.tmp" -o -name "*.json" | while read file; do
            cp "$file" "$FULL_BACKUP_PATH/data/" 2>/dev/null || true
        done
        success "Cache copiado"
    else
        warning "Diretório de dados não encontrado"
    fi
}

# Criar arquivo de informações do backup
create_backup_info() {
    log "Criando arquivo de informações do backup..."
    
    cat > "$FULL_BACKUP_PATH/backup_info.txt" << EOF
MaraBet AI - Informações do Backup
==================================

Data/Hora: $(date)
Versão: 1.0.0
Sistema: $(uname -s) $(uname -m)

Conteúdo do Backup:
- Banco de dados: $(ls -la "$FULL_BACKUP_PATH/sports_data.db" 2>/dev/null | awk '{print $5}' || echo "N/A")
- Logs: $(du -sh "$FULL_BACKUP_PATH/logs" 2>/dev/null | cut -f1 || echo "N/A")
- Relatórios: $(find "$FULL_BACKUP_PATH/reports" -name "*.txt" -o -name "*.pdf" 2>/dev/null | wc -l || echo "0")
- Configuração: $(ls -la "$FULL_BACKUP_PATH/.env" 2>/dev/null | awk '{print $5}' || echo "N/A")

Tamanho Total: $(du -sh "$FULL_BACKUP_PATH" | cut -f1)

Arquivos Incluídos:
$(find "$FULL_BACKUP_PATH" -type f | sed 's|.*/||' | sort)

Instruções de Restore:
1. Pare os serviços: docker-compose down
2. Extraia o backup: tar -xzf $BACKUP_NAME.tar.gz
3. Restaure os arquivos: cp -r $BACKUP_NAME/* ./
4. Reinicie os serviços: docker-compose up -d
EOF
    
    success "Arquivo de informações criado"
}

# Comprimir backup
compress_backup() {
    log "Comprimindo backup..."
    
    cd "$BACKUP_DIR"
    tar -czf "$BACKUP_NAME.tar.gz" "$BACKUP_NAME"
    cd ..
    
    # Remover diretório não comprimido
    rm -rf "$FULL_BACKUP_PATH"
    
    # Mostrar informações do arquivo comprimido
    COMPRESSED_SIZE=$(du -h "$BACKUP_DIR/$BACKUP_NAME.tar.gz" | cut -f1)
    success "Backup comprimido: $BACKUP_NAME.tar.gz ($COMPRESSED_SIZE)"
}

# Verificar integridade do backup
verify_backup() {
    log "Verificando integridade do backup..."
    
    if [ -f "$BACKUP_DIR/$BACKUP_NAME.tar.gz" ]; then
        # Testar extração
        if tar -tzf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" > /dev/null 2>&1; then
            success "Backup verificado com sucesso"
        else
            error "Backup corrompido"
        fi
    else
        error "Arquivo de backup não encontrado"
    fi
}

# Limpar backups antigos
cleanup_old_backups() {
    log "Limpando backups antigos..."
    
    # Manter apenas os últimos 10 backups
    cd "$BACKUP_DIR"
    ls -t marabet_ai_backup_*.tar.gz | tail -n +11 | xargs rm -f 2>/dev/null || true
    cd ..
    
    success "Backups antigos removidos"
}

# Listar backups existentes
list_backups() {
    log "Listando backups existentes..."
    
    if [ -d "$BACKUP_DIR" ]; then
        echo
        echo "=== Backups Disponíveis ==="
        ls -lah "$BACKUP_DIR"/*.tar.gz 2>/dev/null | awk '{print $9, $5, $6, $7, $8}' | column -t || echo "Nenhum backup encontrado"
        
        echo
        echo "=== Espaço Usado ==="
        du -sh "$BACKUP_DIR"
    else
        warning "Diretório de backups não encontrado"
    fi
}

# Restaurar backup
restore_backup() {
    local backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        error "Especifique o arquivo de backup para restaurar"
    fi
    
    if [ ! -f "$backup_file" ]; then
        error "Arquivo de backup não encontrado: $backup_file"
    fi
    
    log "Restaurando backup: $backup_file"
    
    # Parar serviços
    log "Parando serviços..."
    docker-compose down || true
    
    # Extrair backup
    log "Extraindo backup..."
    tar -xzf "$backup_file"
    
    # Restaurar arquivos
    log "Restaurando arquivos..."
    BACKUP_DIR_NAME=$(basename "$backup_file" .tar.gz)
    cp -r "$BACKUP_DIR/$BACKUP_DIR_NAME"/* ./
    
    # Limpar arquivos temporários
    rm -rf "$BACKUP_DIR/$BACKUP_DIR_NAME"
    
    success "Backup restaurado com sucesso"
    log "Reinicie os serviços com: docker-compose up -d"
}

# Função principal
main() {
    case "${1:-backup}" in
        "backup")
            create_backup_dir
            backup_database
            backup_logs
            backup_reports
            backup_config
            backup_models
            backup_cache
            create_backup_info
            compress_backup
            verify_backup
            cleanup_old_backups
            success "Backup concluído com sucesso!"
            ;;
        "list")
            list_backups
            ;;
        "restore")
            restore_backup "$2"
            ;;
        "cleanup")
            cleanup_old_backups
            ;;
        *)
            echo "Uso: $0 {backup|list|restore|cleanup}"
            echo
            echo "Comandos:"
            echo "  backup           - Criar backup completo"
            echo "  list             - Listar backups existentes"
            echo "  restore <file>   - Restaurar backup específico"
            echo "  cleanup          - Limpar backups antigos"
            exit 1
            ;;
    esac
}

# Executar comando
main "$@"
