#!/bin/bash
# MaraBet AI Backup Script
# Generated on 2025-10-21 14:04:32

set -euo pipefail

# Configuration
BACKUP_TYPE="$1"
BACKUP_DIR="backups"
LOGS_DIR="logs/backup"
RETENTION_DAYS=30
COMPRESSION=true
ENCRYPTION=true
VERIFICATION=true
PARALLEL_JOBS=4

# Database configuration
DB_HOST="marabet-master.cluster-xyz.us-east-1.rds.amazonaws.com"
DB_PORT="5432"
DB_NAME="marabet_production"
DB_USER="marabet_user"
DB_PASSWORD="secure_password_123"

# Storage configuration
STORAGE_TYPE="s3"
S3_BUCKET="marabet-backups"

# Logging
log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOGS_DIR/backup.log"
}

error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" | tee -a "$LOGS_DIR/backup.log"
    exit 1
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

# Database backup function
backup_database() {
    local backup_type="$1"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="$BACKUP_DIR/database_${backup_type}_${timestamp}.sql"
    
    log "Starting $backup_type database backup"
    
    # Set PGPASSWORD
    export PGPASSWORD="$DB_PASSWORD"
    
    # Create database backup
    if pg_dump -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" \
        --verbose --no-password --format=custom \
        --compress=9 --blobs \
        -f "$backup_file"; then
        log "Database backup completed: $backup_file"
    else
        error "Database backup failed"
    fi
    
    # Compress if enabled
    if [ "$COMPRESSION" = "true" ]; then
        log "Compressing backup file"
        gzip "$backup_file"
        backup_file="$backup_file.gz"
    fi
    
    # Encrypt if enabled
    if [ "$ENCRYPTION" = "true" ]; then
        log "Encrypting backup file"
        gpg --symmetric --cipher-algo AES256 --output "$backup_file.gpg" "$backup_file"
        rm "$backup_file"
        backup_file="$backup_file.gpg"
    fi
    
    # Upload to storage
    upload_to_storage "$backup_file"
    
    # Verify if enabled
    if [ "$VERIFICATION" = "true" ]; then
        verify_backup "$backup_file"
    fi
    
    log "Database backup completed successfully"
}

# File backup function
backup_files() {
    local backup_type="$1"
    local timestamp=$(date '+%Y%m%d_%H%M%S')
    local backup_file="$BACKUP_DIR/files_${backup_type}_${timestamp}.tar"
    
    log "Starting $backup_type file backup"
    
    # Source paths
    local source_paths=(
        "/var/www/marabet"
        "/etc/marabet"
        "/var/log/marabet"
        "/opt/marabet"
    )
    
    # Create tar backup
    if tar -cf "$backup_file" "${source_paths[@]}" 2>/dev/null; then
        log "File backup completed: $backup_file"
    else
        error "File backup failed"
    fi
    
    # Compress if enabled
    if [ "$COMPRESSION" = "true" ]; then
        log "Compressing backup file"
        gzip "$backup_file"
        backup_file="$backup_file.gz"
    fi
    
    # Encrypt if enabled
    if [ "$ENCRYPTION" = "true" ]; then
        log "Encrypting backup file"
        gpg --symmetric --cipher-algo AES256 --output "$backup_file.gpg" "$backup_file"
        rm "$backup_file"
        backup_file="$backup_file.gpg"
    fi
    
    # Upload to storage
    upload_to_storage "$backup_file"
    
    # Verify if enabled
    if [ "$VERIFICATION" = "true" ]; then
        verify_backup "$backup_file"
    fi
    
    log "File backup completed successfully"
}

# Upload to storage
upload_to_storage() {
    local file_path="$1"
    local file_name=$(basename "$file_path")
    
    log "Uploading $file_name to $STORAGE_TYPE"
    
    case "$STORAGE_TYPE" in
        "s3")
            if aws s3 cp "$file_path" "s3://$S3_BUCKET/backups/$file_name"; then
                log "Uploaded to S3: s3://$S3_BUCKET/backups/$file_name"
            else
                error "S3 upload failed"
            fi
            ;;
        "local")
            log "Backup stored locally: $file_path"
            ;;
        *)
            error "Unsupported storage type: $STORAGE_TYPE"
            ;;
    esac
}

# Verify backup
verify_backup() {
    local backup_file="$1"
    
    log "Verifying backup: $backup_file"
    
    # Check file exists and is not empty
    if [ ! -f "$backup_file" ] || [ ! -s "$backup_file" ]; then
        error "Backup file is missing or empty"
    fi
    
    # Check file integrity
    if [ "$ENCRYPTION" = "true" ]; then
        if gpg --verify "$backup_file" 2>/dev/null; then
            log "Backup verification successful (encrypted)"
        else
            error "Backup verification failed (encrypted)"
        fi
    else
        # For database backups, test restore
        if [[ "$backup_file" == *"database"* ]]; then
            test_restore "$backup_file"
        fi
    fi
    
    log "Backup verification completed"
}

# Test restore
test_restore() {
    local backup_file="$1"
    local test_db="marabet_test_restore_$$"
    
    log "Testing restore with database: $test_db"
    
    # Create test database
    export PGPASSWORD="$DB_PASSWORD"
    if createdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$test_db"; then
        log "Test database created: $test_db"
    else
        error "Failed to create test database"
    fi
    
    # Restore backup
    if pg_restore -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$test_db" \
        --verbose --no-password --clean --if-exists \
        "$backup_file"; then
        log "Test restore successful"
    else
        error "Test restore failed"
    fi
    
    # Drop test database
    dropdb -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" "$test_db"
    log "Test database dropped"
}

# Cleanup old backups
cleanup_backups() {
    log "Cleaning up backups older than $RETENTION_DAYS days"
    
    # Local cleanup
    find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete
    
    # S3 cleanup
    if [ "$STORAGE_TYPE" = "s3" ]; then
        aws s3 ls "s3://$S3_BUCKET/backups/" --recursive | \
        awk '$1 < "'$(date -d "$RETENTION_DAYS days ago" '+%Y-%m-%d')'" {print $4}' | \
        xargs -I {} aws s3 rm "s3://$S3_BUCKET/{}"
    fi
    
    log "Cleanup completed"
}

# Main function
main() {
    case "$BACKUP_TYPE" in
        "full")
            backup_database "full"
            backup_files "full"
            ;;
        "incremental")
            backup_database "incremental"
            backup_files "incremental"
            ;;
        "cleanup")
            cleanup_backups
            ;;
        "verify")
            # Verify all backups
            for backup in "$BACKUP_DIR"/*; do
                if [ -f "$backup" ]; then
                    verify_backup "$backup"
                fi
            done
            ;;
        *)
            echo "Usage: $0 {full|incremental|cleanup|verify}"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
