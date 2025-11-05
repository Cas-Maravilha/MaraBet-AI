{
  "resource": {
    "aws_db_instance": {
      "marabet_slave": {
        "identifier": "marabet-slave",
        "replicate_source_db": "${aws_db_instance.marabet_master.identifier}",
        "instance_class": "db.t3.medium",
        "vpc_security_group_ids": [
          "${aws_security_group.rds_sg.id}"
        ],
        "db_subnet_group_name": "${aws_db_subnet_group.marabet_subnet_group.name}",
        "backup_retention_period": 0,
        "skip_final_snapshot": true,
        "tags": {
          "Name": "MaraBet Slave DB",
          "Environment": "production",
          "Role": "slave"
        }
      }
    }
  }
}