/**
 * MaraBet AI - Database Configuration (C# / .NET)
 * Obtém credenciais do RDS PostgreSQL via AWS Secrets Manager
 */

using System;
using System.Threading.Tasks;
using Amazon;
using Amazon.SecretsManager;
using Amazon.SecretsManager.Model;
using Npgsql;
using Newtonsoft.Json;
using System.Collections.Generic;

namespace MaraBet.Config
{
    /// <summary>
    /// Gerenciador de configuração do banco de dados RDS
    /// </summary>
    public class DatabaseConfig
    {
        private const string SecretName = "rds!db-3758a324-12a2-4675-b5ff-b92acdf38483";
        private const string RegionName = "eu-west-1";
        private const string DatabaseName = "marabet_production";
        
        private Dictionary<string, string> _credentials;
        private static DatabaseConfig _instance;
        private static readonly object _lock = new object();
        
        /// <summary>
        /// Singleton instance
        /// </summary>
        public static DatabaseConfig Instance
        {
            get
            {
                if (_instance == null)
                {
                    lock (_lock)
                    {
                        if (_instance == null)
                        {
                            _instance = new DatabaseConfig();
                        }
                    }
                }
                return _instance;
            }
        }
        
        private DatabaseConfig()
        {
            _credentials = null;
        }
        
        /// <summary>
        /// Obtém credenciais do AWS Secrets Manager
        /// </summary>
        public async Task<Dictionary<string, string>> GetSecretAsync()
        {
            var region = RegionEndpoint.GetBySystemName(RegionName);
            var client = new AmazonSecretsManagerClient(region);
            
            var request = new GetSecretValueRequest
            {
                SecretId = SecretName
            };
            
            GetSecretValueResponse response;
            
            try
            {
                response = await client.GetSecretValueAsync(request);
            }
            catch (ResourceNotFoundException)
            {
                throw new Exception($"Secret {SecretName} não encontrado");
            }
            catch (InvalidRequestException e)
            {
                throw new Exception($"Requisição inválida: {e.Message}");
            }
            catch (InvalidParameterException e)
            {
                throw new Exception($"Parâmetro inválido: {e.Message}");
            }
            catch (DecryptionFailureException e)
            {
                throw new Exception($"Falha ao descriptografar: {e.Message}");
            }
            catch (InternalServiceErrorException e)
            {
                throw new Exception($"Erro interno AWS: {e.Message}");
            }
            
            var secretString = response.SecretString;
            
            // Parse JSON
            var secret = JsonConvert.DeserializeObject<Dictionary<string, string>>(secretString);
            
            return secret;
        }
        
        /// <summary>
        /// Obtém credenciais (com cache)
        /// </summary>
        public async Task<Dictionary<string, string>> GetCredentialsAsync()
        {
            if (_credentials == null)
            {
                _credentials = await GetSecretAsync();
            }
            return _credentials;
        }
        
        /// <summary>
        /// Gera connection string para PostgreSQL
        /// </summary>
        public async Task<string> GetConnectionStringAsync(string database = null)
        {
            var creds = await GetCredentialsAsync();
            var dbName = database ?? DatabaseName;
            
            return $"Host={creds["host"]};" +
                   $"Port={creds["port"]};" +
                   $"Database={dbName};" +
                   $"Username={creds["username"]};" +
                   $"Password={creds["password"]};" +
                   $"SSL Mode=Require;" +
                   $"Trust Server Certificate=true";
        }
        
        /// <summary>
        /// Obtém conexão Npgsql ao banco de dados
        /// </summary>
        public async Task<NpgsqlConnection> GetConnectionAsync(string database = null)
        {
            var connectionString = await GetConnectionStringAsync(database);
            var connection = new NpgsqlConnection(connectionString);
            await connection.OpenAsync();
            return connection;
        }
        
        /// <summary>
        /// Testa conexão com o banco
        /// </summary>
        public async Task<bool> TestConnectionAsync()
        {
            try
            {
                using (var conn = await GetConnectionAsync())
                {
                    using (var cmd = new NpgsqlCommand("SELECT version()", conn))
                    {
                        var version = await cmd.ExecuteScalarAsync();
                        Console.WriteLine("✅ Conexão bem-sucedida!");
                        Console.WriteLine($"   PostgreSQL: {version.ToString().Substring(0, 50)}...");
                    }
                }
                return true;
            }
            catch (Exception e)
            {
                Console.WriteLine($"❌ Erro na conexão: {e.Message}");
                return false;
            }
        }
        
        /// <summary>
        /// Health check do banco de dados
        /// </summary>
        public async Task<Dictionary<string, object>> HealthCheckAsync()
        {
            try
            {
                using (var conn = await GetConnectionAsync())
                {
                    // Versão
                    using (var cmd = new NpgsqlCommand("SELECT version()", conn))
                    {
                        var version = await cmd.ExecuteScalarAsync();
                        
                        // Conexões ativas
                        cmd.CommandText = "SELECT count(*) FROM pg_stat_activity";
                        var connections = await cmd.ExecuteScalarAsync();
                        
                        // Tamanho do database
                        cmd.CommandText = $"SELECT pg_size_pretty(pg_database_size('{DatabaseName}'))";
                        var size = await cmd.ExecuteScalarAsync();
                        
                        return new Dictionary<string, object>
                        {
                            ["status"] = "healthy",
                            ["version"] = version,
                            ["activeConnections"] = connections,
                            ["databaseSize"] = size,
                            ["timestamp"] = DateTime.UtcNow
                        };
                    }
                }
            }
            catch (Exception e)
            {
                return new Dictionary<string, object>
                {
                    ["status"] = "unhealthy",
                    ["error"] = e.Message,
                    ["timestamp"] = DateTime.UtcNow
                };
            }
        }
        
        /// <summary>
        /// Imprime informações do banco
        /// </summary>
        public async Task PrintInfoAsync()
        {
            var creds = await GetCredentialsAsync();
            
            Console.WriteLine(new string('=', 70));
            Console.WriteLine("🗄️  MARABET AI - RDS POSTGRESQL");
            Console.WriteLine(new string('=', 70));
            Console.WriteLine();
            Console.WriteLine($"Host:         {creds["host"]}");
            Console.WriteLine($"Port:         {creds["port"]}");
            Console.WriteLine($"Username:     {creds["username"]}");
            Console.WriteLine($"Password:     {new string('*', creds["password"].Length)}");
            Console.WriteLine($"Engine:       {creds["engine"]}");
            Console.WriteLine($"Database:     {DatabaseName}");
            Console.WriteLine();
            Console.WriteLine("Connection String:");
            Console.WriteLine(new string('-', 70));
            Console.WriteLine(await GetConnectionStringAsync());
            Console.WriteLine();
            Console.WriteLine(new string('=', 70));
        }
    }
    
    /// <summary>
    /// Classe principal para teste
    /// </summary>
    class Program
    {
        static async Task Main(string[] args)
        {
            Console.WriteLine("🚀 MaraBet AI - Database Configuration\n");
            
            try
            {
                var config = DatabaseConfig.Instance;
                
                // Mostrar informações
                await config.PrintInfoAsync();
                
                // Testar conexão
                Console.WriteLine("\n🔌 Testando conexão...");
                Console.WriteLine(new string('-', 70));
                await config.TestConnectionAsync();
                
                // Health check
                Console.WriteLine("\n📊 Health Check...");
                Console.WriteLine(new string('-', 70));
                var health = await config.HealthCheckAsync();
                var healthJson = JsonConvert.SerializeObject(health, Formatting.Indented);
                Console.WriteLine(healthJson);
                
                Console.WriteLine("\n✅ Configuração concluída!");
            }
            catch (Exception e)
            {
                Console.WriteLine($"\n❌ Erro: {e.Message}");
                Environment.Exit(1);
            }
        }
    }
}

/**
 * .csproj dependencies:
 * 
 * <ItemGroup>
 *   <PackageReference Include="AWSSDK.SecretsManager" Version="3.7.0" />
 *   <PackageReference Include="Npgsql" Version="7.0.0" />
 *   <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
 * </ItemGroup>
 * 
 * Instalação:
 * dotnet add package AWSSDK.SecretsManager
 * dotnet add package Npgsql
 * dotnet add package Newtonsoft.Json
 */

/**
 * Exemplo de uso em ASP.NET Core (Startup.cs ou Program.cs):
 * 
 * public void ConfigureServices(IServiceCollection services)
 * {
 *     var dbConfig = DatabaseConfig.Instance;
 *     var connectionString = dbConfig.GetConnectionStringAsync().Result;
 *     
 *     services.AddDbContext<ApplicationDbContext>(options =>
 *         options.UseNpgsql(connectionString));
 * }
 */

/**
 * Exemplo com Entity Framework Core:
 * 
 * public class ApplicationDbContext : DbContext
 * {
 *     protected override void OnConfiguring(DbContextOptionsBuilder optionsBuilder)
 *     {
 *         var dbConfig = DatabaseConfig.Instance;
 *         var connectionString = dbConfig.GetConnectionStringAsync().Result;
 *         optionsBuilder.UseNpgsql(connectionString);
 *     }
 * }
 */

/**
 * Exemplo com Dapper:
 * 
 * using (var conn = await DatabaseConfig.Instance.GetConnectionAsync())
 * {
 *     var users = await conn.QueryAsync<User>("SELECT * FROM users");
 *     foreach (var user in users)
 *     {
 *         Console.WriteLine(user.Name);
 *     }
 * }
 */

