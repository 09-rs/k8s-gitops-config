# Production-Grade Platform Engineering — Kubernetes GitOps Platform

## Capstone Project 5

A production-oriented Kubernetes platform for a SaaS application moving from a monolith toward microservices. The platform demonstrates Infrastructure as Code, Kubernetes workload management, Ansible node configuration, Helm packaging, Argo CD GitOps, autoscaling, observability, and alerting.

> **Submission note:** The AWS runtime environment was intentionally destroyed after validation to avoid ongoing cloud charges. The evidence in this package documents the validated runtime state.

---

## 1. Project Objectives

The platform was designed around the following requirements:

- Run multiple independent microservices on Kubernetes.
- Provision the Kubernetes infrastructure with Terraform.
- Configure worker nodes using Ansible.
- Package every service as an independent Helm chart.
- Deploy workloads through Argo CD using Git as the source of truth.
- Support horizontal autoscaling from 2 to 8 replicas.
- Provide Prometheus, Grafana, Alertmanager, and Node Exporter observability.
- Alert when a container restarts more than 3 times within 5 minutes.
- Route alerts to Slack.
- Prevent production configuration drift by using Git-reviewed changes rather than manual `kubectl edit`.

---

## 2. Repository Structure

The solution was organized into three repositories:

| Repository | Responsibility |
|---|---|
| `k8s-gitops-platform` | Terraform/EKS infrastructure, platform components, RBAC and supporting configuration |
| `k8s-ansible-config` | Ansible inventory, roles and worker-node configuration |
| `k8s-gitops-config` | Application source, Helm charts, Argo CD Applications, monitoring resources and GitOps configuration |

### GitOps repository

```text
k8s-gitops-config/
├── apps/
│   ├── service-a/
│   ├── service-b/
│   └── service-c/
├── charts/
│   ├── service-a/
│   ├── service-b/
│   └── service-c/
├── environments/
│   ├── dev/
│   └── prod/
├── argocd/
└── monitoring/
3. Platform Architecture

The platform used:

AWS EKS — managed Kubernetes control plane
EC2 / EKS managed node group — worker capacity
Terraform — infrastructure provisioning
Ansible — worker-node configuration
Helm — application packaging
Argo CD — GitOps deployment and drift correction
Prometheus — metrics collection
Grafana — visualization
Alertmanager — alert routing
Node Exporter — node-level metrics
Kubernetes Metrics Server — resource metrics used by HPA
Slack — alert destination

See ARCHITECTURE.md for the architecture diagram.

4. Application Layer

Three independent services were deployed:

service-a
service-b
service-c

Each service had:

its own application directory
its own Dockerfile
its own Helm chart
Kubernetes Deployment
ClusterIP Service
health endpoint
readiness probe
liveness probe
resource requests and limits
HPA
optional Ingress configuration

The application containers used Python 3.12 Alpine and exposed port 8080.

5. Helm

Each microservice had an independent Helm chart:

charts/service-a/
charts/service-b/
charts/service-c/

The charts defined Kubernetes resources declaratively rather than requiring manually edited live objects.

The workload configuration included:

replicas: 2
CPU request: 10m
Memory request: 32Mi
CPU limit: 100m
Memory limit: 128Mi
HPA minimum: 2
HPA maximum: 8
CPU target: 70%
6. Autoscaling

Each service was configured with an HPA.

Validated runtime state showed:

service-a   CPU 10%/70%   min 2   max 8   replicas 2
service-b   CPU 10%/70%   min 2   max 8   replicas 2
service-c   CPU 10%/70%   min 2   max 8   replicas 2

The HPA therefore provided a scaling range of 2–8 replicas per service, subject to available cluster capacity and workload demand.

7. GitOps with Argo CD

Argo CD Applications were created for:

service-a
service-b
service-c
monitoring-rules

The service Applications used the GitHub repository as the source:

https://github.com/09-rs/k8s-gitops-config.git

with the respective Helm chart paths:

charts/service-a
charts/service-b
charts/service-c

Automated synchronization was enabled with:

syncPolicy:
  automated:
    prune: true
    selfHeal: true

This means Git is the desired-state source and Argo CD continuously reconciles the cluster toward that state.

8. Monitoring and Observability

The monitoring stack was deployed with kube-prometheus-stack.

Validated components included:

Prometheus
Grafana
Alertmanager
Prometheus Operator
kube-state-metrics
Node Exporter on all three worker nodes

Resource metrics were also available through Metrics Server.

Validated examples:

kubectl top nodes
kubectl top pods

showed live CPU and memory metrics during the deployment.

9. Pod Restart Alert

A PrometheusRule was created:

PodRestartingFrequently

with the expression:

increase(kube_pod_container_status_restarts_total[5m]) > 3

and a one-minute for period.

Purpose:

Detect a container that has restarted more than three times within five minutes.

The rule was stored in Git under:

monitoring/pod-restart-alert.yaml

and managed by the Argo CD monitoring-rules Application.

10. Slack Alerting

Alertmanager was configured through an AlertmanagerConfig named:

slack-alerts

The configuration used a Kubernetes Secret for the Slack webhook rather than committing the webhook value to Git.

The target Slack channel was:

#pipeline-alerts

Resolved alerts were also enabled.

Security note: the actual Slack webhook secret is intentionally excluded from this repository/documentation.

11. Ansible

The Ansible repository implemented these roles:

node-setup
node-exporter
prometheus-config
alertmanager-config

The main playbook applied the roles to the EKS worker nodes.

The validated Ansible run completed successfully on all three workers:

ok=15
changed=1
unreachable=0
failed=0
skipped=0
rescued=0
ignored=0

The inventory used AWS Systems Manager connectivity so SSH access was not required for worker configuration.

12. Infrastructure as Code

Terraform was used to provision:

VPC
subnets
routing
NAT Gateway
EKS cluster
managed node group
IAM resources
supporting infrastructure

The validated EKS environment used:

Region: ap-south-1
Cluster: k8s-gitops-platform
Kubernetes: 1.36
Worker type: t3.small
Desired workers: 3
Minimum workers: 2
Maximum workers: 3

The infrastructure was destroyed after validation to prevent unnecessary AWS charges.

13. Validated Runtime Evidence

Before cleanup, the following runtime checks were successfully performed:

kubectl get nodes
kubectl get pods
kubectl get hpa
kubectl get applications -n argocd
kubectl get pods -n monitoring
kubectl get prometheusrule -n monitoring
kubectl get alertmanagerconfig -n monitoring
kubectl top nodes
kubectl top pods

The runtime evidence demonstrated:

3 Ready EKS worker nodes
3 application services running
HPA configured for 2–8 replicas
Argo CD applications synchronized
Prometheus/Grafana/Alertmanager healthy
Node Exporter running on all workers
Pod restart PrometheusRule present
Slack Alertmanager configuration present
CPU and memory metrics available
14. Git Workflow

The intended production workflow is:

Developer changes application or infrastructure configuration.
Change is committed to Git.
Change is reviewed through the Git workflow.
Approved configuration is merged.
Argo CD detects the Git change.
Argo CD synchronizes the desired state.
Kubernetes performs the deployment.
Prometheus/Grafana observe the workload.
Alertmanager reports defined failures.

No production kubectl edit workflow is required.

15. Security Practices
Secrets are stored in Kubernetes Secrets rather than committed as plaintext.
Slack webhook values are excluded from Git.
Infrastructure changes are managed through Terraform.
Kubernetes application configuration is managed through Git.
Argo CD provides drift detection and self-healing.
Worker access used AWS Systems Manager rather than exposing SSH as the configuration mechanism.
16. Submission Documents
ARCHITECTURE.md — platform architecture
GITOPS-WORKFLOW.md — GitOps workflow
DEMO-SCRIPT.md — three-minute demonstration script
SUBMISSION-CHECKLIST.md — final rubric/evidence checklist
17. Demo Summary

The three-minute demonstration should show:

Architecture and repository separation.
Terraform → EKS infrastructure.
Ansible worker configuration.
Helm charts for three services.
Argo CD GitOps synchronization.
HPA configuration.
Prometheus/Grafana/Alertmanager monitoring.
Pod restart alert and Slack integration.
Git-based production change workflow.
18. Cleanup

After the runtime evidence was captured, the AWS environment was destroyed.

Final verification confirmed:

EKS cluster: absent
VPC: absent
NAT Gateway: deleted
Internet Gateway: deleted
Subnets: deleted
Route tables: cleaned
EIP: absent
ECR application repositories: absent

Terraform was also checked:

terraform destroy

complete 
