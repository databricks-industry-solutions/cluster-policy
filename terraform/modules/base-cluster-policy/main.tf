variable "team" {
  description = "line of business that owns the workloads"
}

variable "policy_overrides" {
  description = "Cluster policy overrides"
}

resource "databricks_cluster_policy" "fair_use" {
  name       = "${var.team} cluster policy"
  definition = jsonencode(merge(jsondecode(file("../../../policies/default-policy.json")), var.policy_overrides))
}

resource "databricks_permissions" "can_use_cluster_policyinstance_profile" {
  cluster_policy_id = databricks_cluster_policy.fair_use.id
  access_control {
    group_name       = var.team
    permission_level = "CAN_USE"
  }
}