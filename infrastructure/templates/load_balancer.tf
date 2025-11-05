{
  "resource": {
    "aws_lb": {
      "marabet_alb": {
        "name": "marabet-alb",
        "internal": false,
        "load_balancer_type": "application",
        "security_groups": [
          "${aws_security_group.alb_sg.id}"
        ],
        "subnets": [
          "${aws_subnet.public_1.id}",
          "${aws_subnet.public_2.id}"
        ],
        "enable_deletion_protection": true,
        "tags": {
          "Name": "MaraBet ALB",
          "Environment": "production"
        }
      }
    },
    "aws_lb_target_group": {
      "marabet_tg": {
        "name": "marabet-tg",
        "port": 5000,
        "protocol": "HTTP",
        "vpc_id": "${aws_vpc.main.id}",
        "target_type": "ip",
        "health_check": {
          "enabled": true,
          "healthy_threshold": 2,
          "interval": 30,
          "matcher": "200",
          "path": "/api/health",
          "port": "traffic-port",
          "protocol": "HTTP",
          "timeout": 5,
          "unhealthy_threshold": 3
        },
        "stickiness": {
          "enabled": false,
          "type": "lb_cookie",
          "cookie_duration": 86400
        },
        "tags": {
          "Name": "MaraBet Target Group",
          "Environment": "production"
        }
      }
    },
    "aws_lb_listener": {
      "marabet_listener": {
        "load_balancer_arn": "${aws_lb.marabet_alb.arn}",
        "port": "443",
        "protocol": "HTTPS",
        "ssl_policy": "ELBSecurityPolicy-TLS-1-2-2017-01",
        "certificate_arn": "${aws_acm_certificate.marabet_cert.arn}",
        "default_action": {
          "type": "forward",
          "target_group_arn": "${aws_lb_target_group.marabet_tg.arn}"
        }
      }
    },
    "aws_lb_listener_rule": {
      "marabet_rule": {
        "listener_arn": "${aws_lb_listener.marabet_listener.arn}",
        "priority": 100,
        "action": {
          "type": "forward",
          "target_group_arn": "${aws_lb_target_group.marabet_tg.arn}"
        },
        "condition": {
          "field": "path-pattern",
          "values": [
            "/*"
          ]
        }
      }
    }
  }
}