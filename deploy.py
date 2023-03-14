import logging
import os
import sys
import json

from databricks_cli.cluster_policies.api import ClusterPolicyApi
from databricks_cli.sdk.api_client import ApiClient

log = logging.Logger(name='policy-deployment', level='INFO')
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
log.addHandler(handler)

db_host = os.getenv('DATABRICKS_HOST')
db_token = os.getenv('DATABRICKS_TOKEN')
environment = os.getenv('environment')
policy_name = os.getenv('policy')
inherit_from = os.getenv('inherit_from')
acl = os.getenv('acl')

client = ApiClient(host=db_host, token=db_token)
policy_api = ClusterPolicyApi(client)

if __name__ == '__main__':
    full_policy_name = f'{environment}-{policy_name}'
    log.info(f'Deploying policy: {full_policy_name} to {environment}')

    policy_list = policy_api.list_cluster_policies()
    data = {"name": full_policy_name}

    for policy in policy_list['policies']:
        if policy['name'] == full_policy_name:
            data['policy_id'] = policy['policy_id']
            break

    if inherit_from is not None:
        log.info(f'Inheriting from {inherit_from} for {full_policy_name} in {environment}')
        data['policy_family_id'] = inherit_from
        with open(f'{policy_name}.json', 'r') as policy_file:
            data['policy_family_definition_overrides'] = policy_file.read()
    else:
        with open(f'{policy_name}.json', 'r') as policy_file:
            data['definition'] = policy_file.read()

    if 'policy_id' not in data:
        log.info(f'Creating new policy {full_policy_name} in {environment}')
        policy_id = policy_api.create_cluster_policy(data)
    else:
        log.info(f'Updating existing policy {full_policy_name} ({data["policy_id"]}) in {environment}')
        policy_id = policy_api.edit_cluster_policy(data)

    if acl is not None:
        with open(f'{acl}.json', 'r') as acl_file:
            # The databricks CLI does not have an easy way to update the ACLs on a specific cluster policy, so we have to
            # directly use the client. Not ideal, but I see no better way  right now.
            policy_id = data['policy_id']
            client.perform_query('PUT', f'/permissions/cluster-policies/{policy_id}', data=json.loads(acl_file.read()))
            log.info(f'Created acl for {policy_id} from {acl} in {environment}')

    log.info(f'{full_policy_name} successfully deployed in {environment}')
