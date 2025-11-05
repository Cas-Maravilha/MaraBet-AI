{
  "resource": {
    "aws_s3_bucket": {
      "marabet_backups": {
        "bucket": "marabet-backups-${random_id.bucket_suffix.hex}",
        "force_destroy": false,
        "tags": {
          "Name": "MaraBet Backups",
          "Environment": "production"
        }
      }
    },
    "aws_s3_bucket_versioning": {
      "marabet_backups_versioning": {
        "bucket": "${aws_s3_bucket.marabet_backups.id}",
        "versioning_configuration": {
          "status": "Enabled"
        }
      }
    },
    "aws_s3_bucket_server_side_encryption_configuration": {
      "marabet_backups_encryption": {
        "bucket": "${aws_s3_bucket.marabet_backups.id}",
        "rule": [
          {
            "apply_server_side_encryption_by_default": {
              "sse_algorithm": "AES256"
            }
          }
        ]
      }
    },
    "aws_s3_bucket_lifecycle_configuration": {
      "marabet_backups_lifecycle": {
        "bucket": "${aws_s3_bucket.marabet_backups.id}",
        "rule": [
          {
            "id": "backup_lifecycle",
            "status": "Enabled",
            "expiration": {
              "days": 30
            },
            "noncurrent_version_expiration": {
              "days": 7
            },
            "transition": [
              {
                "days": 30,
                "storage_class": "STANDARD_IA"
              },
              {
                "days": 90,
                "storage_class": "GLACIER"
              }
            ]
          }
        ]
      }
    },
    "random_id": {
      "bucket_suffix": {
        "byte_length": 8
      }
    }
  }
}