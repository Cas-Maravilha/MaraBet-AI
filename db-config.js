/**
 * MaraBet AI - Database Configuration (Node.js)
 * Obtém credenciais do RDS PostgreSQL via AWS Secrets Manager
 */

const AWS = require('aws-sdk');
const { Pool } = require('pg');

/**
 * Configuração do Database
 */
class DatabaseConfig {
    constructor() {
        this.secretName = 'rds!db-3758a324-12a2-4675-b5ff-b92acdf38483';
        this.region = 'eu-west-1';
        this.databaseName = 'marabet_production';
        this.credentials = null;
        this.pool = null;
    }
    
    /**
     * Obtém credenciais do AWS Secrets Manager
     * @returns {Promise<Object>} Credenciais do RDS
     */
    async getSecret() {
        const client = new AWS.SecretsManager({
            region: this.region
        });
        
        try {
            const data = await client.getSecretValue({
                SecretId: this.secretName
            }).promise();
            
            // Parse JSON
            const secret = JSON.parse(data.SecretString);
            
            return {
                username: secret.username,
                password: secret.password,
                host: secret.host,
                port: secret.port,
                engine: secret.engine,
                dbInstanceIdentifier: secret.dbInstanceIdentifier
            };
            
        } catch (error) {
            if (error.code === 'ResourceNotFoundException') {
                throw new Error(`Secret ${this.secretName} não encontrado`);
            } else if (error.code === 'InvalidRequestException') {
                throw new Error(`Requisição inválida: ${error.message}`);
            } else if (error.code === 'InvalidParameterException') {
                throw new Error(`Parâmetro inválido: ${error.message}`);
            } else if (error.code === 'DecryptionFailure') {
                throw new Error(`Falha ao descriptografar: ${error.message}`);
            } else {
                throw error;
            }
        }
    }
    
    /**
     * Obtém credenciais (com cache)
     */
    async getCredentials() {
        if (!this.credentials) {
            this.credentials = await this.getSecret();
        }
        return this.credentials;
    }
    
    /**
     * Gera connection string para PostgreSQL
     * @param {string} database - Nome do database (opcional)
     * @returns {Promise<string>} Connection string
     */
    async getConnectionString(database = null) {
        const creds = await this.getCredentials();
        const dbName = database || this.databaseName;
        
        return `postgresql://${creds.username}:${creds.password}@${creds.host}:${creds.port}/${dbName}?sslmode=require`;
    }
    
    /**
     * Gera configuração para pg Pool
     * @param {string} database - Nome do database (opcional)
     * @returns {Promise<Object>} Configuração do Pool
     */
    async getPoolConfig(database = null) {
        const creds = await this.getCredentials();
        const dbName = database || this.databaseName;
        
        return {
            user: creds.username,
            password: creds.password,
            host: creds.host,
            port: parseInt(creds.port),
            database: dbName,
            ssl: {
                rejectUnauthorized: false
            },
            max: 20, // Máximo de conexões no pool
            idleTimeoutMillis: 30000,
            connectionTimeoutMillis: 2000,
        };
    }
    
    /**
     * Obtém Pool de conexões PostgreSQL
     * @returns {Promise<Pool>} Pool de conexões
     */
    async getPool() {
        if (!this.pool) {
            const config = await this.getPoolConfig();
            this.pool = new Pool(config);
            
            // Tratamento de erros
            this.pool.on('error', (err) => {
                console.error('❌ Erro inesperado no pool:', err);
            });
        }
        return this.pool;
    }
    
    /**
     * Obtém uma conexão do pool
     * @returns {Promise<Object>} Cliente PostgreSQL
     */
    async getClient() {
        const pool = await this.getPool();
        return await pool.connect();
    }
    
    /**
     * Testa conexão com o banco de dados
     * @returns {Promise<boolean>} true se conectou com sucesso
     */
    async testConnection() {
        try {
            const client = await this.getClient();
            
            // Testar query simples
            const result = await client.query('SELECT version()');
            const version = result.rows[0].version;
            
            console.log('✅ Conexão bem-sucedida!');
            console.log(`   PostgreSQL: ${version.substring(0, 50)}...`);
            
            client.release();
            return true;
            
        } catch (error) {
            console.error('❌ Erro na conexão:', error.message);
            return false;
        }
    }
    
    /**
     * Health check do banco de dados
     * @returns {Promise<Object>} Status do banco
     */
    async healthCheck() {
        try {
            const client = await this.getClient();
            
            // Versão
            const versionResult = await client.query('SELECT version()');
            const version = versionResult.rows[0].version;
            
            // Conexões ativas
            const connectionsResult = await client.query(
                'SELECT count(*) FROM pg_stat_activity'
            );
            const activeConnections = connectionsResult.rows[0].count;
            
            // Tamanho do database
            const sizeResult = await client.query(
                `SELECT pg_size_pretty(pg_database_size('${this.databaseName}'))`
            );
            const databaseSize = sizeResult.rows[0].pg_size_pretty;
            
            client.release();
            
            return {
                status: 'healthy',
                version: version,
                activeConnections: parseInt(activeConnections),
                databaseSize: databaseSize,
                timestamp: new Date().toISOString()
            };
            
        } catch (error) {
            return {
                status: 'unhealthy',
                error: error.message,
                timestamp: new Date().toISOString()
            };
        }
    }
    
    /**
     * Imprime informações do banco
     */
    async printInfo() {
        const creds = await this.getCredentials();
        
        console.log('='.repeat(70));
        console.log('🗄️  MARABET AI - RDS POSTGRESQL');
        console.log('='.repeat(70));
        console.log();
        console.log(`Host:         ${creds.host}`);
        console.log(`Port:         ${creds.port}`);
        console.log(`Username:     ${creds.username}`);
        console.log(`Password:     ${'*'.repeat(creds.password.length)}`);
        console.log(`Engine:       ${creds.engine}`);
        console.log(`Database:     ${this.databaseName}`);
        console.log();
        console.log('Connection String:');
        console.log('-'.repeat(70));
        console.log(await this.getConnectionString());
        console.log();
        console.log('JDBC URL:');
        console.log('-'.repeat(70));
        console.log(await this.getJdbcUrl());
        console.log();
        console.log('='.repeat(70));
    }
    
    /**
     * Fecha pool de conexões
     */
    async close() {
        if (this.pool) {
            await this.pool.end();
            this.pool = null;
        }
    }
}

// Instância singleton
const dbConfig = new DatabaseConfig();

// Exports
module.exports = {
    DatabaseConfig,
    dbConfig,
    
    // Funções de conveniência
    getCredentials: () => dbConfig.getCredentials(),
    getConnectionString: (database) => dbConfig.getConnectionString(database),
    getPool: () => dbConfig.getPool(),
    getClient: () => dbConfig.getClient(),
    testConnection: () => dbConfig.testConnection(),
    healthCheck: () => dbConfig.healthCheck(),
};

/**
 * Exemplo de uso direto
 */
if (require.main === module) {
    (async () => {
        try {
            console.log('🚀 MaraBet AI - Database Configuration\n');
            
            // Mostrar informações
            await dbConfig.printInfo();
            
            // Testar conexão
            console.log('\n🔌 Testando conexão...');
            console.log('-'.repeat(70));
            await dbConfig.testConnection();
            
            // Health check
            console.log('\n📊 Health Check...');
            console.log('-'.repeat(70));
            const health = await dbConfig.healthCheck();
            console.log(JSON.stringify(health, null, 2));
            
            // Fechar pool
            await dbConfig.close();
            
            console.log('\n✅ Configuração concluída!');
            
        } catch (error) {
            console.error('\n❌ Erro:', error.message);
            process.exit(1);
        }
    })();
}

/**
 * package.json dependencies:
 * 
 * {
 *   "dependencies": {
 *     "aws-sdk": "^2.1400.0",
 *     "pg": "^8.11.0"
 *   }
 * }
 * 
 * Instalação:
 * npm install aws-sdk pg
 */

/**
 * Exemplo de uso em Express.js:
 * 
 * const express = require('express');
 * const { getPool } = require('./db-config');
 * 
 * const app = express();
 * let pool;
 * 
 * // Inicializar pool
 * (async () => {
 *     pool = await getPool();
 * })();
 * 
 * // Route exemplo
 * app.get('/users', async (req, res) => {
 *     try {
 *         const result = await pool.query('SELECT * FROM users');
 *         res.json(result.rows);
 *     } catch (error) {
 *         res.status(500).json({ error: error.message });
 *     }
 * });
 * 
 * app.listen(3000);
 */

/**
 * Exemplo com TypeScript:
 * 
 * import { getCredentials, getConnectionString, getPool } from './db-config';
 * 
 * async function main() {
 *     const creds = await getCredentials();
 *     const connString = await getConnectionString();
 *     const pool = await getPool();
 *     
 *     const result = await pool.query('SELECT NOW()');
 *     console.log(result.rows[0]);
 * }
 */

/**
 * Exemplo com Sequelize:
 * 
 * const { Sequelize } = require('sequelize');
 * const { getConnectionString } = require('./db-config');
 * 
 * (async () => {
 *     const connectionString = await getConnectionString();
 *     const sequelize = new Sequelize(connectionString, {
 *         dialect: 'postgres',
 *         dialectOptions: {
 *             ssl: {
 *                 require: true,
 *                 rejectUnauthorized: false
 *             }
 *         }
 *     });
 *     
 *     await sequelize.authenticate();
 *     console.log('✅ Sequelize conectado!');
 * })();
 */

/**
 * Exemplo com Prisma (schema.prisma):
 * 
 * datasource db {
 *   provider = "postgresql"
 *   url      = env("DATABASE_URL")
 * }
 * 
 * // Obter DATABASE_URL:
 * const { getConnectionString } = require('./db-config');
 * process.env.DATABASE_URL = await getConnectionString();
 */

