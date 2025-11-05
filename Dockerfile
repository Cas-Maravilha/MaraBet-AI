FROM python:3.11-slim

# ============================================================================
# MARABET AI - DOCKERFILE
# Imagem otimizada para produção AWS
# ============================================================================

# Metadata
LABEL maintainer="MaraBet AI <suporte@marabet.com>"
LABEL version="1.0.0"
LABEL description="MaraBet AI - Sistema de Análise Desportiva com IA"

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    ENVIRONMENT=production \
    TZ=Africa/Luanda

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    libpq-dev \
    postgresql-client \
    redis-tools \
    curl \
    wget \
    git \
    && rm -rf /var/lib/apt/lists/*

# Criar diretório de trabalho
WORKDIR /app

# Copiar requirements primeiro (para cache do Docker)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Criar diretórios necessários
RUN mkdir -p static media logs backups

# Coletar arquivos estáticos (Django)
RUN python manage.py collectstatic --noinput || true

# Criar usuário não-root (segurança)
RUN useradd -m -u 1000 marabet && \
    chown -R marabet:marabet /app

# Mudar para usuário não-root
USER marabet

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando padrão (Gunicorn para Django/Flask)
CMD ["gunicorn", "marabet.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "2", "--timeout", "120", "--access-logfile", "-", "--error-logfile", "-"]
