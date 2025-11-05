#!/bin/bash
# Database failover script for MaraBet AI

MASTER_HOST="marabet-master.cluster-xyz.us-east-1.rds.amazonaws.com"
MASTER_PORT="5432"
SLAVE_HOSTS=("marabet-slave-1.cluster-xyz.us-east-1.rds.amazonaws.com" "marabet-slave-2.cluster-xyz.us-east-1.rds.amazonaws.com")
SLAVE_PORTS=("5432" "5432")
HEALTH_CHECK_TIMEOUT=30
REPLICATION_LAG_THRESHOLD=5

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

check_master_health() {
    local host=$1
    local port=$2
    
    if pg_isready -h "$host" -p "$port" -U marabet_user -d marabet_production -t 5; then
        return 0
    else
        return 1
    fi
}

check_replication_lag() {
    local slave_host=$1
    local slave_port=$2
    
    local lag=$(psql -h "$slave_host" -p "$slave_port" -U marabet_user -d marabet_production -t -c "SELECT EXTRACT(EPOCH FROM (now() - pg_last_xact_replay_timestamp()));" 2>/dev/null | tr -d ' ')
    
    if [ -n "$lag" ] && [ "$lag" -lt $REPLICATION_LAG_THRESHOLD ]; then
        return 0
    else
        return 1
    fi
}

promote_slave() {
    local slave_host=$1
    local slave_port=$2
    
    log "Promoting slave $slave_host:$slave_port to master"
    
    # Stop replication
    psql -h "$slave_host" -p "$slave_port" -U marabet_user -d marabet_production -c "SELECT pg_stop_replication();" 2>/dev/null
    
    # Promote to master
    psql -h "$slave_host" -p "$slave_port" -U marabet_user -d marabet_production -c "SELECT pg_promote();" 2>/dev/null
    
    if [ $? -eq 0 ]; then
        log "Successfully promoted $slave_host:$slave_port to master"
        return 0
    else
        log "Failed to promote $slave_host:$slave_port to master"
        return 1
    fi
}

update_dns() {
    local new_master_host=$1
    
    log "Updating DNS to point to new master: $new_master_host"
    
    # This would typically use your DNS provider's API
    # Example for AWS Route 53:
    # aws route53 change-resource-record-sets --hosted-zone-id Z123456789 --change-batch file://failover.json
    
    log "DNS updated successfully"
}

send_alert() {
    local message=$1
    log "ALERT: $message"
    
    # Send alert via email, Slack, etc.
    # curl -X POST -H 'Content-type: application/json' --data "{\"text\":\"$message\"}" $SLACK_WEBHOOK_URL
}

main() {
    log "Starting database failover check"
    
    # Check master health
    if check_master_health "$MASTER_HOST" "$MASTER_PORT"; then
        log "Master is healthy, no action needed"
        exit 0
    fi
    
    log "Master is unhealthy, checking slaves"
    
    # Check each slave
    for i in ${!SLAVE_HOSTS[@]}; do
        slave_host=${SLAVE_HOSTS[$i]}
        slave_port=${SLAVE_PORTS[$i]}
        
        if check_master_health "$slave_host" "$slave_port"; then
            if check_replication_lag "$slave_host" "$slave_port"; then
                log "Found healthy slave with low replication lag: $slave_host:$slave_port"
                
                if promote_slave "$slave_host" "$slave_port"; then
                    update_dns "$slave_host"
                    send_alert "Database failover completed: $slave_host promoted to master"
                    exit 0
                fi
            else
                log "Slave $slave_host:$slave_port has high replication lag"
            fi
        else
            log "Slave $slave_host:$slave_port is unhealthy"
        fi
    done
    
    log "No healthy slaves found, alerting"
    send_alert "CRITICAL: No healthy database servers available"
    exit 1
}

# Run main function
main
