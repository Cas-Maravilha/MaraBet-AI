{
  "resource": {
    "aws_elasticache_replication_group": {
      "marabet_redis": {
        "replication_group_id": "marabet-redis",
        "description": "MaraBet Redis cluster",
        "node_type": "cache.t3.micro",
        "port": 6379,
        "parameter_group_name": "default.redis6.x",
        "num_cache_clusters": 3,
        "engine_version": "6.x",
        "subnet_group_name": "${aws_elasticache_subnet_group.marabet_redis_subnet_group.name}",
        "security_group_ids": [
          "${aws_security_group.redis_sg.id}"
        ],
        "at_rest_encryption_enabled": true,
        "transit_encryption_enabled": true,
        "snapshot_retention_limit": 5,
        "snapshot_window": "03:00-05:00",
        "maintenance_window": "sun:05:00-sun:07:00",
        "tags": {
          "Name": "MaraBet Redis",
          "Environment": "production"
        }
      }
    }
  }
}