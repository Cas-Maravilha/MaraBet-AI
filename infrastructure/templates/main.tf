{
  "terraform": {
    "required_version": ">= 1.0",
    "required_providers": {
      "aws": {
        "source": "hashicorp/aws",
        "version": "~> 5.0"
      }
    }
  },
  "provider": {
    "aws": {
      "region": "us-east-1",
      "default_tags": {
        "Project": "MaraBet-AI",
        "Environment": "production"
      }
    }
  },
  "data": {
    "aws_availability_zones": {
      "available": {
        "state": "available"
      }
    }
  },
  "locals": {
    "common_tags": {
      "Project": "MaraBet-AI",
      "Environment": "production",
      "ManagedBy": "Terraform"
    }
  },
  "resource": {
    "aws_vpc": {
      "main": {
        "cidr_block": "10.0.0.0/16",
        "enable_dns_hostnames": true,
        "enable_dns_support": true,
        "tags": {
          "Name": "marabet-vpc",
          "Project": "MaraBet-AI",
          "Environment": "production",
          "ManagedBy": "Terraform"
        }
      }
    },
    "aws_subnet_subnet_0": {
      "vpc_id": "${aws_vpc.main.id}",
      "cidr_block": "10.0.1.0/24",
      "availability_zone": "us-east-1a",
      "map_public_ip_on_launch": true,
      "tags": {
        "Name": "marabet-subnet-0",
        "Project": "MaraBet-AI",
        "Environment": "production",
        "ManagedBy": "Terraform"
      }
    },
    "aws_subnet_subnet_1": {
      "vpc_id": "${aws_vpc.main.id}",
      "cidr_block": "10.0.2.0/24",
      "availability_zone": "us-east-1b",
      "map_public_ip_on_launch": true,
      "tags": {
        "Name": "marabet-subnet-1",
        "Project": "MaraBet-AI",
        "Environment": "production",
        "ManagedBy": "Terraform"
      }
    },
    "aws_subnet_subnet_2": {
      "vpc_id": "${aws_vpc.main.id}",
      "cidr_block": "10.0.3.0/24",
      "availability_zone": "us-east-1c",
      "map_public_ip_on_launch": true,
      "tags": {
        "Name": "marabet-subnet-2",
        "Project": "MaraBet-AI",
        "Environment": "production",
        "ManagedBy": "Terraform"
      }
    },
    "aws_security_group_web_sg": {
      "name": "web_sg",
      "description": "Security group for web traffic",
      "vpc_id": "${aws_vpc.main.id}",
      "ingress": [
        {
          "from_port": 80,
          "to_port": 80,
          "protocol": "tcp",
          "cidr_blocks": [
            "0.0.0.0/0"
          ]
        },
        {
          "from_port": 443,
          "to_port": 443,
          "protocol": "tcp",
          "cidr_blocks": [
            "0.0.0.0/0"
          ]
        }
      ],
      "egress": [
        {
          "from_port": 0,
          "to_port": 0,
          "protocol": "-1",
          "cidr_blocks": [
            "0.0.0.0/0"
          ]
        }
      ],
      "tags": {
        "Project": "MaraBet-AI",
        "Environment": "production",
        "ManagedBy": "Terraform"
      }
    },
    "aws_security_group_db_sg": {
      "name": "db_sg",
      "description": "Security group for database",
      "vpc_id": "${aws_vpc.main.id}",
      "ingress": [
        {
          "from_port": 5432,
          "to_port": 5432,
          "protocol": "tcp",
          "source_security_group_id": "${aws_security_group_web_sg.id}"
        }
      ],
      "egress": [
        {
          "from_port": 0,
          "to_port": 0,
          "protocol": "-1",
          "cidr_blocks": [
            "0.0.0.0/0"
          ]
        }
      ],
      "tags": {
        "Project": "MaraBet-AI",
        "Environment": "production",
        "ManagedBy": "Terraform"
      }
    },
    "aws_lb": {
      "main": {
        "name": "marabet-alb",
        "internal": false,
        "load_balancer_type": "application",
        "security_groups": [
          "${aws_security_group_web_sg.id}"
        ],
        "subnets": [
          "${aws_subnet_subnet_0.id}",
          "${aws_subnet_subnet_1.id}",
          "${aws_subnet_subnet_2.id}"
        ],
        "tags": {
          "Project": "MaraBet-AI",
          "Environment": "production",
          "ManagedBy": "Terraform"
        }
      }
    },
    "aws_db_instance": {
      "main": {
        "identifier": "marabet-db",
        "engine": "postgres",
        "engine_version": "15.4",
        "instance_class": "db.t3.micro",
        "allocated_storage": 20,
        "storage_type": "gp2",
        "storage_encrypted": true,
        "vpc_security_group_ids": [
          "${aws_security_group_db_sg.id}"
        ],
        "db_subnet_group_name": "${aws_db_subnet_group.main.name}",
        "backup_retention_period": 7,
        "backup_window": "03:00-04:00",
        "maintenance_window": "sun:04:00-sun:05:00",
        "multi_az": true,
        "deletion_protection": true,
        "tags": {
          "Project": "MaraBet-AI",
          "Environment": "production",
          "ManagedBy": "Terraform"
        }
      }
    },
    "aws_db_subnet_group": {
      "main": {
        "name": "marabet-db-subnet-group",
        "subnet_ids": [
          "${aws_subnet_subnet_0.id}",
          "${aws_subnet_subnet_1.id}",
          "${aws_subnet_subnet_2.id}"
        ],
        "tags": {
          "Project": "MaraBet-AI",
          "Environment": "production",
          "ManagedBy": "Terraform"
        }
      }
    },
    "aws_elasticache_subnet_group": {
      "main": {
        "name": "marabet-cache-subnet-group",
        "subnet_ids": [
          "${aws_subnet_subnet_0.id}",
          "${aws_subnet_subnet_1.id}",
          "${aws_subnet_subnet_2.id}"
        ]
      }
    },
    "aws_elasticache_replication_group": {
      "main": {
        "replication_group_id": "marabet-redis",
        "description": "MaraBet Redis cluster",
        "node_type": "cache.t3.micro",
        "port": 6379,
        "parameter_group_name": "default.redis7",
        "num_cache_clusters": 2,
        "subnet_group_name": "${aws_elasticache_subnet_group.main.name}",
        "security_group_ids": [
          "${aws_security_group_db_sg.id}"
        ],
        "at_rest_encryption_enabled": true,
        "transit_encryption_enabled": true,
        "tags": {
          "Project": "MaraBet-AI",
          "Environment": "production",
          "ManagedBy": "Terraform"
        }
      }
    },
    "aws_s3_bucket": {
      "backups": {
        "bucket": "marabet-backups-production",
        "tags": {
          "Project": "MaraBet-AI",
          "Environment": "production",
          "ManagedBy": "Terraform"
        }
      }
    },
    "aws_s3_bucket_versioning": {
      "backups": {
        "bucket": "${aws_s3_bucket.backups.id}",
        "versioning_configuration": {
          "status": "Enabled"
        }
      }
    },
    "aws_s3_bucket_encryption": {
      "backups": {
        "bucket": "${aws_s3_bucket.backups.id}",
        "server_side_encryption_configuration": {
          "rule": {
            "apply_server_side_encryption_by_default": {
              "sse_algorithm": "AES256"
            }
          }
        }
      }
    },
    "aws_cloudwatch_log_group": {
      "main": {
        "name": "/aws/ecs/marabet",
        "retention_in_days": 30,
        "tags": {
          "Project": "MaraBet-AI",
          "Environment": "production",
          "ManagedBy": "Terraform"
        }
      }
    }
  }
}