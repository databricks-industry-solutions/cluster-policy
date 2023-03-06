module "marketing_compute_policy" {
  source = "../modules/base-cluster-policy"
  team   = "marketing"
  policy_overrides = {
    // only marketing guys will benefit from delta cache this way
    "spark_conf.spark.databricks.io.cache.enabled" : {
      "type" : "fixed",
      "value" : "true"
    },
  }
}

module "engineering_compute_policy" {
  source = "../modules/base-cluster-policy"
  team   = "engineering"
  policy_overrides = {
    "dbus_per_hour" : {
      "type" : "range",
      // allow data engineering to use larger clusters
      "maxValue" : 50
    },
  }
}