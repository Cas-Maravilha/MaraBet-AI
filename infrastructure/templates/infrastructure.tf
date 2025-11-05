{
  "terraform": {
    "required_version": ">= 1.0",
    "required_providers": {
      "aws": {
        "source": "hashicorp/aws",
        "version": "~> 5.0"
      },
      "kubernetes": {
        "source": "hashicorp/kubernetes",
        "version": "~> 2.0"
      }
    }
  },
  "provider": {
    "aws": {
      "region": "us-east-1"
    }
  },
  "resource": {
    "aws_eks_cluster": {
      "marabet_cluster": {
        "name": "marabet-cluster",
        "role_arn": "${aws_iam_role.eks_cluster_role.arn}",
        "vpc_config": {
          "subnet_ids": [
            "${aws_subnet.private_1.id}",
            "${aws_subnet.private_2.id}"
          ],
          "endpoint_private_access": true,
          "endpoint_public_access": true
        },
        "enabled_cluster_log_types": [
          "api",
          "audit",
          "authenticator",
          "controllerManager",
          "scheduler"
        ],
        "tags": {
          "Name": "MaraBet EKS Cluster",
          "Environment": "production"
        }
      }
    },
    "aws_eks_node_group": {
      "marabet_nodes": {
        "cluster_name": "${aws_eks_cluster.marabet_cluster.name}",
        "node_group_name": "marabet-nodes",
        "node_role_arn": "${aws_iam_role.eks_node_role.arn}",
        "subnet_ids": [
          "${aws_subnet.private_1.id}",
          "${aws_subnet.private_2.id}"
        ],
        "instance_types": [
          "t3.medium"
        ],
        "capacity_type": "ON_DEMAND",
        "scaling_config": {
          "desired_size": 3,
          "max_size": 10,
          "min_size": 1
        },
        "update_config": {
          "max_unavailable_percentage": 25
        },
        "tags": {
          "Name": "MaraBet EKS Nodes",
          "Environment": "production"
        }
      }
    }
  }
}