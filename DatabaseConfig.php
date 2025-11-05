<?php
/**
 * MaraBet AI - Database Configuration (PHP)
 * Obtém credenciais do RDS PostgreSQL via AWS Secrets Manager
 */

require 'vendor/autoload.php';

use Aws\SecretsManager\SecretsManagerClient;
use Aws\Exception\AwsException;

/**
 * Gerenciador de configuração do banco de dados RDS
 */
class DatabaseConfig
{
    private const SECRET_NAME = 'rds!db-3758a324-12a2-4675-b5ff-b92acdf38483';
    private const REGION = 'eu-west-1';
    private const DATABASE_NAME = 'marabet_production';
    
    private $credentials = null;
    private $pdo = null;
    private static $instance = null;
    
    /**
     * Singleton instance
     */
    public static function getInstance()
    {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }
    
    private function __construct()
    {
    }
    
    /**
     * Obtém credenciais do AWS Secrets Manager
     * 
     * @return array Credenciais
     * @throws Exception
     */
    public function getSecret()
    {
        $client = new SecretsManagerClient([
            'region' => self::REGION,
            'version' => 'latest'
        ]);
        
        try {
            $result = $client->getSecretValue([
                'SecretId' => self::SECRET_NAME,
            ]);
            
        } catch (AwsException $e) {
            $error = $e->getAwsErrorCode();
            
            if ($error === 'ResourceNotFoundException') {
                throw new Exception("Secret " . self::SECRET_NAME . " não encontrado");
            } elseif ($error === 'InvalidRequestException') {
                throw new Exception("Requisição inválida: " . $e->getMessage());
            } elseif ($error === 'InvalidParameterException') {
                throw new Exception("Parâmetro inválido: " . $e->getMessage());
            } else {
                throw $e;
            }
        }
        
        // Parse JSON
        $secretString = $result['SecretString'];
        $secret = json_decode($secretString, true);
        
        return $secret;
    }
    
    /**
     * Obtém credenciais (com cache)
     */
    public function getCredentials()
    {
        if ($this->credentials === null) {
            $this->credentials = $this->getSecret();
        }
        return $this->credentials;
    }
    
    /**
     * Gera DSN para PostgreSQL (PDO)
     * 
     * @param string|null $database Nome do database
     * @return string DSN
     */
    public function getDsn($database = null)
    {
        $creds = $this->getCredentials();
        $dbName = $database ?? self::DATABASE_NAME;
        
        return sprintf(
            "pgsql:host=%s;port=%s;dbname=%s;sslmode=require",
            $creds['host'],
            $creds['port'],
            $dbName
        );
    }
    
    /**
     * Gera connection string completa
     */
    public function getConnectionString($database = null)
    {
        $creds = $this->getCredentials();
        $dbName = $database ?? self::DATABASE_NAME;
        
        return sprintf(
            "postgresql://%s:%s@%s:%s/%s?sslmode=require",
            $creds['username'],
            $creds['password'],
            $creds['host'],
            $creds['port'],
            $dbName
        );
    }
    
    /**
     * Obtém conexão PDO
     * 
     * @param string|null $database Nome do database
     * @return PDO Conexão PDO
     */
    public function getConnection($database = null)
    {
        $creds = $this->getCredentials();
        $dsn = $this->getDsn($database);
        
        $options = [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ];
        
        return new PDO($dsn, $creds['username'], $creds['password'], $options);
    }
    
    /**
     * Obtém conexão PDO (singleton)
     */
    public function getPdo()
    {
        if ($this->pdo === null) {
            $this->pdo = $this->getConnection();
        }
        return $this->pdo;
    }
    
    /**
     * Testa conexão com o banco
     * 
     * @return bool true se conectou
     */
    public function testConnection()
    {
        try {
            $pdo = $this->getConnection();
            
            // Testar query
            $stmt = $pdo->query('SELECT version()');
            $version = $stmt->fetchColumn();
            
            echo "✅ Conexão bem-sucedida!\n";
            echo "   PostgreSQL: " . substr($version, 0, 50) . "...\n";
            
            return true;
            
        } catch (Exception $e) {
            echo "❌ Erro na conexão: " . $e->getMessage() . "\n";
            return false;
        }
    }
    
    /**
     * Configuração para Laravel (config/database.php)
     */
    public function getLaravelConfig($database = null)
    {
        $creds = $this->getCredentials();
        $dbName = $database ?? self::DATABASE_NAME;
        
        return [
            'driver' => 'pgsql',
            'host' => $creds['host'],
            'port' => $creds['port'],
            'database' => $dbName,
            'username' => $creds['username'],
            'password' => $creds['password'],
            'charset' => 'utf8',
            'prefix' => '',
            'schema' => 'public',
            'sslmode' => 'require',
        ];
    }
    
    /**
     * Imprime informações do banco
     */
    public function printInfo()
    {
        $creds = $this->getCredentials();
        
        echo str_repeat('=', 70) . "\n";
        echo "🗄️  MARABET AI - RDS POSTGRESQL\n";
        echo str_repeat('=', 70) . "\n\n";
        echo "Host:         {$creds['host']}\n";
        echo "Port:         {$creds['port']}\n";
        echo "Username:     {$creds['username']}\n";
        echo "Password:     " . str_repeat('*', strlen($creds['password'])) . "\n";
        echo "Engine:       {$creds['engine']}\n";
        echo "Database:     " . self::DATABASE_NAME . "\n\n";
        echo "Connection String:\n";
        echo str_repeat('-', 70) . "\n";
        echo $this->getConnectionString() . "\n\n";
        echo "DSN (PDO):\n";
        echo str_repeat('-', 70) . "\n";
        echo $this->getDsn() . "\n\n";
        echo str_repeat('=', 70) . "\n";
    }
}

/**
 * Funções de conveniência
 */
function getCredentials()
{
    return DatabaseConfig::getInstance()->getCredentials();
}

function getConnectionString($database = null)
{
    return DatabaseConfig::getInstance()->getConnectionString($database);
}

function getPdo()
{
    return DatabaseConfig::getInstance()->getPdo();
}

function testConnection()
{
    return DatabaseConfig::getInstance()->testConnection();
}

/**
 * Teste do módulo
 */
if (php_sapi_name() === 'cli' && basename(__FILE__) === basename($_SERVER['SCRIPT_FILENAME'])) {
    echo "🚀 MaraBet AI - Database Configuration\n\n";
    
    try {
        $config = DatabaseConfig::getInstance();
        
        // Mostrar informações
        $config->printInfo();
        
        // Testar conexão
        echo "\n🔌 Testando conexão...\n";
        echo str_repeat('-', 70) . "\n";
        $config->testConnection();
        
        echo "\n✅ Configuração concluída!\n";
        
    } catch (Exception $e) {
        echo "\n❌ Erro: " . $e->getMessage() . "\n";
        exit(1);
    }
}

/**
 * composer.json:
 * 
 * {
 *     "require": {
 *         "aws/aws-sdk-php": "^3.0"
 *     }
 * }
 * 
 * Instalação:
 * composer require aws/aws-sdk-php
 */

/**
 * Exemplo de uso em Laravel:
 * 
 * // config/database.php
 * $dbConfig = DatabaseConfig::getInstance();
 * 
 * return [
 *     'connections' => [
 *         'pgsql' => $dbConfig->getLaravelConfig(),
 *     ],
 * ];
 */

/**
 * Exemplo de uso simples:
 * 
 * <?php
 * require 'DatabaseConfig.php';
 * 
 * // Obter PDO
 * $pdo = getPdo();
 * 
 * // Executar query
 * $stmt = $pdo->query('SELECT * FROM users');
 * $users = $stmt->fetchAll();
 * 
 * foreach ($users as $user) {
 *     echo $user['name'] . "\n";
 * }
 */

