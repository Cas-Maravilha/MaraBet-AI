#!/bin/bash
# MaraBet AI Secrets Rotation Script
# Generated on 2025-10-21 14:06:08

set -euo pipefail

# Configuration
SECRETS_PROVIDER="hashicorp_vault"
VAULT_URL="https://vault.marabet.com:8200"
AWS_REGION="us-east-1"
NAMESPACE="marabet"

# Logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a /var/log/secrets-rotation.log
}

error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" | tee -a /var/log/secrets-rotation.log
    exit 1
}

# Generate new secret
generate_new_secret() {
    local secret_type="$1"
    local length="$2"
    
    case "$secret_type" in
        "password")
            openssl rand -base64 "$length" | tr -d "=+/" | cut -c1-"$length"
            ;;
        "api_key")
            openssl rand -hex "$length"
            ;;
        "jwt_secret")
            openssl rand -base64 "$length" | tr -d "=+/"
            ;;
        "encryption_key")
            openssl rand -base64 "$length"
            ;;
        *)
            openssl rand -base64 "$length"
            ;;
    esac
}

# Rotate Vault secret
rotate_vault_secret() {
    local secret_path="$1"
    local secret_type="$2"
    local length="$3"
    
    log "Rotating Vault secret: $secret_path"
    
    # Generate new secret
    local new_secret=$(generate_new_secret "$secret_type" "$length")
    
    # Update in Vault
    if vault kv put "$secret_path" value="$new_secret"; then
        log "Vault secret updated: $secret_path"
    else
        error "Failed to update Vault secret: $secret_path"
    fi
}

# Rotate AWS Secrets Manager secret
rotate_aws_secret() {
    local secret_name="$1"
    local secret_type="$2"
    local length="$3"
    
    log "Rotating AWS secret: $secret_name"
    
    # Generate new secret
    local new_secret=$(generate_new_secret "$secret_type" "$length")
    
    # Update in AWS Secrets Manager
    if aws secretsmanager update-secret \
        --secret-id "$secret_name" \
        --secret-string "$new_secret" \
        --region "$AWS_REGION"; then
        log "AWS secret updated: $secret_name"
    else
        error "Failed to update AWS secret: $secret_name"
    fi
}

# Rotate Kubernetes secret
rotate_k8s_secret() {
    local secret_name="$1"
    local secret_key="$2"
    local secret_type="$3"
    local length="$4"
    
    log "Rotating Kubernetes secret: $secret_name/$secret_key"
    
    # Generate new secret
    local new_secret=$(generate_new_secret "$secret_type" "$length")
    
    # Update in Kubernetes
    if kubectl patch secret "$secret_name" \
        -n "$NAMESPACE" \
        -p="{\"data\":{\"$secret_key\":\"$(echo -n "$new_secret" | base64)\"}}"; then
        log "Kubernetes secret updated: $secret_name/$secret_key"
    else
        error "Failed to update Kubernetes secret: $secret_name/$secret_key"
    fi
}

# Rotate database password
rotate_database_password() {
    log "Rotating database password"
    
    local new_password=$(generate_new_secret "password" 32)
    
    # Update database password
    case "$SECRETS_PROVIDER" in
        "hashicorp_vault")
            rotate_vault_secret "secret/data/marabet/database" "password" 32
            ;;
        "aws_secrets_manager")
            rotate_aws_secret "marabet/database" "password" 32
            ;;
        "kubernetes_secrets")
            rotate_k8s_secret "marabet-secrets" "db-password" "password" 32
            ;;
        *)
            error "Unsupported secrets provider: $SECRETS_PROVIDER"
            ;;
    esac
    
    log "Database password rotated successfully"
}

# Rotate API keys
rotate_api_keys() {
    log "Rotating API keys"
    
    local new_api_key=$(generate_new_secret "api_key" 32)
    
    case "$SECRETS_PROVIDER" in
        "hashicorp_vault")
            rotate_vault_secret "secret/data/marabet/api-keys" "api_key" 32
            ;;
        "aws_secrets_manager")
            rotate_aws_secret "marabet/api-keys" "api_key" 32
            ;;
        "kubernetes_secrets")
            rotate_k8s_secret "marabet-secrets" "api-football-key" "api_key" 32
            ;;
        *)
            error "Unsupported secrets provider: $SECRETS_PROVIDER"
            ;;
    esac
    
    log "API keys rotated successfully"
}

# Rotate JWT secrets
rotate_jwt_secrets() {
    log "Rotating JWT secrets"
    
    local new_jwt_secret=$(generate_new_secret "jwt_secret" 64)
    
    case "$SECRETS_PROVIDER" in
        "hashicorp_vault")
            rotate_vault_secret "secret/data/marabet/jwt-secrets" "jwt_secret" 64
            ;;
        "aws_secrets_manager")
            rotate_aws_secret "marabet/jwt-secrets" "jwt_secret" 64
            ;;
        "kubernetes_secrets")
            rotate_k8s_secret "marabet-secrets" "jwt-secret" "jwt_secret" 64
            ;;
        *)
            error "Unsupported secrets provider: $SECRETS_PROVIDER"
            ;;
    esac
    
    log "JWT secrets rotated successfully"
}

# Main function
main() {
    local rotation_type="$1"
    
    case "$rotation_type" in
        "database")
            rotate_database_password
            ;;
        "api-keys")
            rotate_api_keys
            ;;
        "jwt")
            rotate_jwt_secrets
            ;;
        "all")
            rotate_database_password
            rotate_api_keys
            rotate_jwt_secrets
            ;;
        *)
            echo "Usage: $0 {database|api-keys|jwt|all}"
            exit 1
            ;;
    esac
    
    log "Secrets rotation completed successfully"
}

# Run main function
main "$@"
