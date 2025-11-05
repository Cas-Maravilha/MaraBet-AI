#!/bin/bash
# MaraBet AI Secrets Validation Script
# Generated on 2025-10-21 14:06:08

set -euo pipefail

# Configuration
SECRETS_PROVIDER="hashicorp_vault"
VAULT_URL="https://vault.marabet.com:8200"
AWS_REGION="us-east-1"
NAMESPACE="marabet"

# Logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a /var/log/secrets-validation.log
}

error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" | tee -a /var/log/secrets-validation.log
    exit 1
}

# Validate Vault secret
validate_vault_secret() {
    local secret_path="$1"
    local expected_keys="$2"
    
    log "Validating Vault secret: $secret_path"
    
    if vault kv get "$secret_path" > /dev/null 2>&1; then
        log "Vault secret exists: $secret_path"
        
        # Check if all expected keys are present
        for key in $expected_keys; do
            if vault kv get -field="$key" "$secret_path" > /dev/null 2>&1; then
                log "Key '$key' found in secret: $secret_path"
            else
                error "Key '$key' not found in secret: $secret_path"
            fi
        done
    else
        error "Vault secret not found: $secret_path"
    fi
}

# Validate AWS Secrets Manager secret
validate_aws_secret() {
    local secret_name="$1"
    local expected_keys="$2"
    
    log "Validating AWS secret: $secret_name"
    
    if aws secretsmanager describe-secret --secret-id "$secret_name" --region "$AWS_REGION" > /dev/null 2>&1; then
        log "AWS secret exists: $secret_name"
        
        # Get secret value
        local secret_value=$(aws secretsmanager get-secret-value --secret-id "$secret_name" --region "$AWS_REGION" --query SecretString --output text)
        
        # Check if all expected keys are present
        for key in $expected_keys; do
            if echo "$secret_value" | jq -r ".$key" > /dev/null 2>&1; then
                log "Key '$key' found in secret: $secret_name"
            else
                error "Key '$key' not found in secret: $secret_name"
            fi
        done
    else
        error "AWS secret not found: $secret_name"
    fi
}

# Validate Kubernetes secret
validate_k8s_secret() {
    local secret_name="$1"
    local expected_keys="$2"
    
    log "Validating Kubernetes secret: $secret_name"
    
    if kubectl get secret "$secret_name" -n "$NAMESPACE" > /dev/null 2>&1; then
        log "Kubernetes secret exists: $secret_name"
        
        # Check if all expected keys are present
        for key in $expected_keys; do
            if kubectl get secret "$secret_name" -n "$NAMESPACE" -o jsonpath="{.data.$key}" > /dev/null 2>&1; then
                log "Key '$key' found in secret: $secret_name"
            else
                error "Key '$key' not found in secret: $secret_name"
            fi
        done
    else
        error "Kubernetes secret not found: $secret_name"
    fi
}

# Validate all secrets
validate_all_secrets() {
    log "Validating all secrets"
    
    case "$SECRETS_PROVIDER" in
        "hashicorp_vault")
            validate_vault_secret "secret/data/marabet/database" "host port database username password"
            validate_vault_secret "secret/data/marabet/api-keys" "api_football_key telegram_bot_token slack_webhook_url"
            validate_vault_secret "secret/data/marabet/jwt-secrets" "jwt_secret jwt_refresh_secret"
            validate_vault_secret "secret/data/marabet/encryption-keys" "encryption_key backup_encryption_key"
            ;;
        "aws_secrets_manager")
            validate_aws_secret "marabet/database" "host port database username password"
            validate_aws_secret "marabet/api-keys" "api_football_key telegram_bot_token slack_webhook_url"
            validate_aws_secret "marabet/jwt-secrets" "jwt_secret jwt_refresh_secret"
            validate_aws_secret "marabet/encryption-keys" "encryption_key backup_encryption_key"
            ;;
        "kubernetes_secrets")
            validate_k8s_secret "marabet-secrets" "db-host db-port db-name db-username db-password"
            validate_k8s_secret "marabet-secrets" "api-football-key telegram-bot-token slack-webhook-url"
            validate_k8s_secret "marabet-secrets" "jwt-secret jwt-refresh-secret"
            validate_k8s_secret "marabet-secrets" "encryption-key backup-encryption-key"
            ;;
        *)
            error "Unsupported secrets provider: $SECRETS_PROVIDER"
            ;;
    esac
    
    log "All secrets validated successfully"
}

# Main function
main() {
    local validation_type="$1"
    
    case "$validation_type" in
        "all")
            validate_all_secrets
            ;;
        "database")
            case "$SECRETS_PROVIDER" in
                "hashicorp_vault")
                    validate_vault_secret "secret/data/marabet/database" "host port database username password"
                    ;;
                "aws_secrets_manager")
                    validate_aws_secret "marabet/database" "host port database username password"
                    ;;
                "kubernetes_secrets")
                    validate_k8s_secret "marabet-secrets" "db-host db-port db-name db-username db-password"
                    ;;
            esac
            ;;
        *)
            echo "Usage: $0 {all|database}"
            exit 1
            ;;
    esac
    
    log "Secrets validation completed successfully"
}

# Run main function
main "$@"
