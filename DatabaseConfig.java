/**
 * MaraBet AI - Database Configuration (Java)
 * Obtém credenciais do RDS PostgreSQL via AWS Secrets Manager
 */

package com.marabet.config;

import software.amazon.awssdk.regions.Region;
import software.amazon.awssdk.services.secretsmanager.SecretsManagerClient;
import software.amazon.awssdk.services.secretsmanager.model.GetSecretValueRequest;
import software.amazon.awssdk.services.secretsmanager.model.GetSecretValueResponse;
import com.google.gson.Gson;
import com.google.gson.JsonObject;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;
import java.util.HashMap;
import java.util.Map;

/**
 * Gerenciador de configuração do banco de dados RDS
 */
public class DatabaseConfig {
    
    private static final String SECRET_NAME = "rds!db-3758a324-12a2-4675-b5ff-b92acdf38483";
    private static final Region REGION = Region.EU_WEST_1;
    private static final String DATABASE_NAME = "marabet_production";
    
    private Map<String, String> credentials;
    private static DatabaseConfig instance;
    
    /**
     * Singleton instance
     */
    public static DatabaseConfig getInstance() {
        if (instance == null) {
            instance = new DatabaseConfig();
        }
        return instance;
    }
    
    private DatabaseConfig() {
        this.credentials = null;
    }
    
    /**
     * Obtém credenciais do AWS Secrets Manager
     * 
     * @return Map com username, password, host, port, engine
     * @throws Exception se falhar ao obter credenciais
     */
    public Map<String, String> getSecret() throws Exception {
        
        // Create a Secrets Manager client
        SecretsManagerClient client = SecretsManagerClient.builder()
                .region(REGION)
                .build();

        GetSecretValueRequest getSecretValueRequest = GetSecretValueRequest.builder()
                .secretId(SECRET_NAME)
                .build();

        GetSecretValueResponse getSecretValueResponse;

        try {
            getSecretValueResponse = client.getSecretValue(getSecretValueRequest);
        } catch (Exception e) {
            // For a list of exceptions thrown, see
            // https://docs.aws.amazon.com/secretsmanager/latest/apireference/API_GetSecretValue.html
            System.err.println("Erro ao obter secret: " + e.getMessage());
            throw e;
        } finally {
            client.close();
        }

        String secretString = getSecretValueResponse.secretString();
        
        // Parse JSON
        Gson gson = new Gson();
        JsonObject secretJson = gson.fromJson(secretString, JsonObject.class);
        
        Map<String, String> creds = new HashMap<>();
        creds.put("username", secretJson.get("username").getAsString());
        creds.put("password", secretJson.get("password").getAsString());
        creds.put("host", secretJson.get("host").getAsString());
        creds.put("port", secretJson.get("port").getAsString());
        creds.put("engine", secretJson.get("engine").getAsString());
        creds.put("dbInstanceIdentifier", secretJson.get("dbInstanceIdentifier").getAsString());
        
        return creds;
    }
    
    /**
     * Obtém credenciais (com cache)
     */
    public Map<String, String> getCredentials() throws Exception {
        if (credentials == null) {
            credentials = getSecret();
        }
        return credentials;
    }
    
    /**
     * Gera JDBC URL para PostgreSQL
     * 
     * @return JDBC URL
     */
    public String getJdbcUrl() throws Exception {
        Map<String, String> creds = getCredentials();
        return String.format(
            "jdbc:postgresql://%s:%s/%s?sslmode=require",
            creds.get("host"),
            creds.get("port"),
            DATABASE_NAME
        );
    }
    
    /**
     * Gera JDBC URL com database personalizado
     */
    public String getJdbcUrl(String database) throws Exception {
        Map<String, String> creds = getCredentials();
        return String.format(
            "jdbc:postgresql://%s:%s/%s?sslmode=require",
            creds.get("host"),
            creds.get("port"),
            database
        );
    }
    
    /**
     * Obtém conexão JDBC ao banco de dados
     * 
     * @return Conexão JDBC
     */
    public Connection getConnection() throws Exception {
        Map<String, String> creds = getCredentials();
        String url = getJdbcUrl();
        
        return DriverManager.getConnection(
            url,
            creds.get("username"),
            creds.get("password")
        );
    }
    
    /**
     * Obtém conexão com database específico
     */
    public Connection getConnection(String database) throws Exception {
        Map<String, String> creds = getCredentials();
        String url = getJdbcUrl(database);
        
        return DriverManager.getConnection(
            url,
            creds.get("username"),
            creds.get("password")
        );
    }
    
    /**
     * Testa conexão com o banco de dados
     * 
     * @return true se conectou com sucesso
     */
    public boolean testConnection() {
        try {
            Connection conn = getConnection();
            
            // Testar query simples
            var stmt = conn.createStatement();
            var rs = stmt.executeQuery("SELECT version()");
            
            if (rs.next()) {
                String version = rs.getString(1);
                System.out.println("✅ Conexão bem-sucedida!");
                System.out.println("   PostgreSQL: " + version.substring(0, 50) + "...");
            }
            
            rs.close();
            stmt.close();
            conn.close();
            
            return true;
            
        } catch (Exception e) {
            System.err.println("❌ Erro na conexão: " + e.getMessage());
            return false;
        }
    }
    
    /**
     * Imprime informações do banco de dados
     */
    public void printInfo() throws Exception {
        Map<String, String> creds = getCredentials();
        
        System.out.println("=" .repeat(70));
        System.out.println("🗄️  MARABET AI - RDS POSTGRESQL");
        System.out.println("=" .repeat(70));
        System.out.println();
        System.out.println("Host:         " + creds.get("host"));
        System.out.println("Port:         " + creds.get("port"));
        System.out.println("Username:     " + creds.get("username"));
        System.out.println("Password:     " + "*".repeat(creds.get("password").length()));
        System.out.println("Engine:       " + creds.get("engine"));
        System.out.println("Database:     " + DATABASE_NAME);
        System.out.println();
        System.out.println("JDBC URL:");
        System.out.println("-".repeat(70));
        System.out.println(getJdbcUrl());
        System.out.println();
        System.out.println("=" .repeat(70));
    }
    
    /**
     * Método main para teste
     */
    public static void main(String[] args) {
        try {
            DatabaseConfig config = DatabaseConfig.getInstance();
            
            // Mostrar informações
            config.printInfo();
            
            // Testar conexão
            System.out.println("\n🔌 Testando conexão...");
            System.out.println("-".repeat(70));
            config.testConnection();
            
            System.out.println("\n✅ Configuração concluída!");
            
        } catch (Exception e) {
            System.err.println("\n❌ Erro: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
}


/**
 * Maven dependencies (pom.xml):
 * 
 * <dependencies>
 *     <!-- AWS SDK Secrets Manager -->
 *     <dependency>
 *         <groupId>software.amazon.awssdk</groupId>
 *         <artifactId>secretsmanager</artifactId>
 *         <version>2.20.0</version>
 *     </dependency>
 *     
 *     <!-- PostgreSQL JDBC Driver -->
 *     <dependency>
 *         <groupId>org.postgresql</groupId>
 *         <artifactId>postgresql</artifactId>
 *         <version>42.6.0</version>
 *     </dependency>
 *     
 *     <!-- Gson for JSON parsing -->
 *     <dependency>
 *         <groupId>com.google.code.gson</groupId>
 *         <artifactId>gson</artifactId>
 *         <version>2.10.1</version>
 *     </dependency>
 * </dependencies>
 */


/**
 * Exemplo de uso em Spring Boot:
 * 
 * @Configuration
 * public class DataSourceConfig {
 *     
 *     @Bean
 *     public DataSource dataSource() throws Exception {
 *         DatabaseConfig dbConfig = DatabaseConfig.getInstance();
 *         Map<String, String> creds = dbConfig.getCredentials();
 *         
 *         HikariConfig config = new HikariConfig();
 *         config.setJdbcUrl(dbConfig.getJdbcUrl());
 *         config.setUsername(creds.get("username"));
 *         config.setPassword(creds.get("password"));
 *         config.setDriverClassName("org.postgresql.Driver");
 *         config.setMaximumPoolSize(10);
 *         
 *         return new HikariDataSource(config);
 *     }
 * }
 */

