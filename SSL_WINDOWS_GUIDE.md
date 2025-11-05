# 🔐 SSL em Windows (Desenvolvimento Local) - MaraBet AI

Para desenvolvimento local no Windows, você pode usar certificados auto-assinados.

## 🔧 MÉTODO 1: mkcert (Recomendado)

### Instalar mkcert:

```powershell
# Usando Chocolatey
choco install mkcert

# Usando Scoop
scoop bucket add extras
scoop install mkcert
```

### Criar Certificados:

```powershell
# Instalar CA local
mkcert -install

# Criar certificados
mkcert localhost 127.0.0.1 ::1

# Mover para diretório do projeto
mkdir certs
move localhost+2.pem certs/cert.pem
move localhost+2-key.pem certs/key.pem
```

### Usar no Docker:

```yaml
# Adicionar ao docker-compose.yml
services:
  nginx:
    volumes:
      - ./certs:/etc/nginx/certs:ro
```

## 🔧 MÉTODO 2: OpenSSL

### Instalar OpenSSL:

```powershell
# Baixar de: https://slproweb.com/products/Win32OpenSSL.html
# Ou usar Git Bash que inclui OpenSSL
```

### Criar Certificados:

```bash
# Gerar chave privada
openssl genrsa -out certs/key.pem 2048

# Gerar certificado auto-assinado
openssl req -new -x509 -key certs/key.pem -out certs/cert.pem -days 365
```

## ⚠️ IMPORTANTE

Certificados auto-assinados são apenas para desenvolvimento local!

Para produção, use sempre certificados válidos (Let's Encrypt).
