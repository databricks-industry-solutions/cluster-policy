import json
import os
import logging

from databricks_cli.cluster_policies.api import ClusterPolicyApi
from databricks_cli.sdk.api_client import ApiClient

log = logging.Logger(name='policy-deployment', level='INFO')
db_host = os.getenv('DATABRICKS_HOST')
db_token = os.getenv('DATABRICKS_TOKEN')
environment = os.getenv('environment')
policy_name = os.getenv('policy')
inherit_from = os.getenv('inherit_from')

client = ApiClient(host=db_host, token=db_token)
policy_api = ClusterPolicyApi(client)

if __name__ == '__main__':
    full_policy_name = f'{environment}-{policy_name}'
    log.info(f'Deploying policy: {full_policy_name} to {environment}')

    policy_list = policy_api.list_cluster_policies()
    data = { "name": full_policy_name }

    for policy in policy_list['policies']:
        if policy['name'] == full_policy_name:
            data['policy_id'] = policy['policy_id']
            break

    if inherit_from is not None:
        log.info(f'Inheriting from {inherit_from} for {full_policy_name} in {environment}')
        data['policy_family_id'] = inherit_from
        data['policy_family_definition_overrides'] = json.loads(open(f'{policy_name}.json', 'r').read())
    else:
        data['definition'] = json.loads(open(f'{policy_name}.json', 'r').read())

    if 'policy_id' not in data:
        log.info(f'Creating new policy {full_policy_name} in {environment}')
        policy_api.create_cluster_policy(data)
    else:
        log.info(f'Updating existing policy {full_policy_name} ({data["policy_id"]}) in {environment}')
        policy_api.edit_cluster_policy(data)

    log.info(f'{full_policy_name} successfully deployed in {environment}')
