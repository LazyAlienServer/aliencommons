discovery.docker "containers" {
    host = "unix:///var/run/docker.sock"
}

discovery.relabel "backend_services" {
  targets = discovery.docker.containers.targets

  rule {
    source_labels = ["__meta_docker_container_name"]
    regex         = ".*/(backend-api|backend-task-worker|backend-task-scheduler)$"
    action        = "keep"
  }

  rule {
    source_labels = ["__meta_docker_container_name"]
    regex         = ".*/(.*)"
    target_label  = "container"
    replacement   = "$1"
  }

  rule {
    source_labels = ["container"]
    regex         = "backend-api"
    target_label  = "service"
    replacement   = "backend-api"
  }

  rule {
    source_labels = ["container"]
    regex         = "backend-task-worker"
    target_label  = "service"
    replacement   = "backend-task-worker"
  }

  rule {
    source_labels = ["container"]
    regex         = "backend-task-scheduler"
    target_label  = "service"
    replacement   = "backend-task-scheduler"
  }

  rule {
    target_label = "environment"
    replacement  = "pro"
  }
}

loki.source.docker "backend_logs" {
  host       = "unix:///var/run/docker.sock"
  targets    = discovery.relabel.backend_services.output
  forward_to = [loki.write.default.receiver]
}

loki.write "default" {
  endpoint {
    url = "http://loki:3100/loki/api/v1/push"
  }
}