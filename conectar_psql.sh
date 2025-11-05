#!/bin/bash
# Script para conectar ao PostgreSQL
export PGPASSWORD='dudbeeGdNBSxjpEWlop'
psql -U "meu_root\$marabet" -d marabet -h localhost "$@"

