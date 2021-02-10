resource "kubernetes_service" "nhais" {
  metadata {
    name = local.resource_prefix
    namespace = kubernetes_namespace.nhais.metadata.0.name

    labels = {
      Project = var.project
      Environment = var.environment
      Component = var.component
      Name = local.resource_prefix
    }

    annotations = {
      "service.beta.kubernetes.io/azure-load-balancer-internal" = true
    }
  }

  spec {
    port {
      port = var.nhais_application_port
      target_port = var.nhais_container_port
    }

    type = "LoadBalancer"
    load_balancer_ip = var.nhais_lb_ip

    selector = {
      Component = "nhais"
      Environment = var.environment
    }

  }
}

output nhais_ingress {
  value = kubernetes_service.nhais.status[0].load_balancer[0].ingress
}