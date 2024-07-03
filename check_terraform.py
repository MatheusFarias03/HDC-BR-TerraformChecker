'''
check_terraform.py: Checks if the terraform.tfstate file contains the correct
created resources from Huawei Developer Conference 2024 terraform activity, 
hosted on São Paulo, Brazil. 
'''

import json


NAME = 'name'
CIDR = 'cidr'
SUBNET = 'subnet'
TYPE = 'type'
FLAVOR = 'flavor'
ECS = 'ecs'
DB = 'db'
RESOURCE_POINTS = []


def score_check(score_condition:bool) -> int:
    return 10 if score_condition else 5


def check_attribute(attribute_name:str, attributes:dict, total_score:int, pattern) -> int:
    value = attributes.get(attribute_name)
    condition = pattern(value)
    score = score_check(condition)
    total_score += score
    return total_score


def time_check(attributes:dict):
    created_at = attributes.get('created_at')
    created_at = created_at[11:19]

    updated_at = attributes.get('updated_at')
    if updated_at:
        updated_at = updated_at[11:19]
        return updated_at

    return created_at


def check_vpc(attributes, total_score:int, user:str) -> tuple[int, str, dict]:

    points = {}
    
    # The name of the VPC should be 'vpc-##' where the last two digits are the
    # same as the user's last two digits on its folder.
    name_pattern = lambda v: v.startswith('vpc-') and v.endswith(user[-2:])
    total_score = check_attribute(NAME, attributes, total_score, name_pattern)

    region_pattern = lambda v: v == 'sa-brazil-1'
    total_score = check_attribute('region', attributes, total_score, region_pattern)

    cidr_pattern = lambda v: v.startswith('10.') and v.endswith('.0.0/16')
    total_score = check_attribute(CIDR, attributes, total_score, cidr_pattern)

    id = attributes.get('id')
            
    return total_score, id, points


def check_subnet(attributes, total_score:int, vpc_id:str, user:str) -> tuple[int, str, dict]:

    points = {}
    
    vpc_id_pattern = lambda v: vpc_id == v
    total_score = check_attribute('vpc_id', attributes, total_score, vpc_id_pattern)

    def subnet_name_pattern(name:str) -> bool:
        ecs_name_con = SUBNET in name and ECS in name and name.endswith(user[-2:])
        db_name_con = SUBNET in name and DB in name and name.endswith(user[-2:])
        return ecs_name_con or db_name_con

    def subnet_cidr_pattern(cidr:str) -> bool:
        ecs_cidr_con = cidr.startswith('10.') and cidr.endswith('.0.0/24')
        db_cidr_con = cidr.startswith('10.') and cidr.endswith('.1.0/24')
        ecs_name_con = SUBNET in attributes.get(NAME) and ECS in attributes.get(NAME)
        db_name_con = SUBNET in attributes.get(NAME) and DB in attributes.get(NAME)
        return (ecs_cidr_con and ecs_name_con) or (db_cidr_con and db_name_con)

    total_score = check_attribute(NAME, attributes, total_score, subnet_name_pattern)

    total_score = check_attribute(CIDR, attributes, total_score, subnet_cidr_pattern)

    id = attributes.get('id')
            
    return total_score, id, points


def check_sec_group(attributes:dict, total_score:int, user:str) -> tuple[int, str, str, dict]:
    
    points = {}
    
    name_pattern = lambda v: 'secgroup-' in v and v.endswith(user[-2:])
    total_score = check_attribute(NAME, attributes, total_score, name_pattern)

    # Define patterns for the rules.
    mysql_pattern = lambda rule: (
        rule.get('ports') == '3306' and
        rule.get('remote_ip_prefix') == '0.0.0.0/0' and
        rule.get('priority') == 1
    )
    
    tcp_pattern = lambda rule: (
        rule.get('ports') == '22' and
        rule.get('remote_ip_prefix') and
        rule.get('priority') == 1
    )
    
    icmp_pattern = lambda rule: (
        rule.get('protocol') == 'icmp' and
        rule.get('remote_ip_prefix') == '0.0.0.0/0'
    )

    # Booleans to check if the rules were set or not.
    mysql_rule:bool = False
    icmp_rule:bool = False
    tcp_rule:bool = False

    # Check each rule in the security group rules.
    sec_group_rules = attributes.get('rules', [])
    for rule in sec_group_rules:
       
        if mysql_pattern(rule):
            mysql_rule = True
        
        elif tcp_pattern(rule):
            tcp_rule = True
        
        elif icmp_pattern(rule):
            icmp_rule = True

    # Function to handle scoring and messaging for rules.
    def handle_rule(rule_flag) -> None:
        if rule_flag:
            score  = score_check(rule_flag)
            nonlocal total_score
            total_score += score

    # Handle scoring and messaging for each rule
    handle_rule(mysql_rule)
    handle_rule(tcp_rule)
    handle_rule(icmp_rule)

    id = attributes.get('id')

    time_att = time_check(attributes)
            
    return total_score, id, time_att, points


def check_ecs(attributes:dict, total_score:int, subnet_id:str, sec_group_id:str, user:str
              ) -> tuple[int, str, dict]:

    points = {}
    
    subnet_id_pattern = lambda v: subnet_id == v
    network = attributes.get('network')
    total_score = check_attribute('uuid', network[0], total_score, subnet_id_pattern)

    sec_group_dict = {'sec_group_id': ''}
    sec_group_arr = attributes.get('security_group_ids')
    sec_group_dict['sec_group_id'] = sec_group_arr[0]
    sec_group_pattern = lambda v: sec_group_id == v
    total_score = check_attribute('sec_group_id', sec_group_dict, total_score, 
                                  sec_group_pattern)

    hostname_pattern = lambda v: ECS in v and v.endswith(user[-2:])
    total_score = check_attribute('hostname', attributes, total_score, hostname_pattern)

    ip_pattern = lambda v: v.startswith('10.') and v.endswith('.0.10')
    total_score = check_attribute('access_ip_v4', attributes, total_score, ip_pattern)

    flavor_pattern = lambda v: 's6.large.4' in v
    total_score = check_attribute('flavor_id', attributes, total_score, flavor_pattern)

    time_att = time_check(attributes)

    return total_score, time_att, points


def check_eip(attributes:dict, total_score:int, user:str) -> tuple[int, str, dict]:

    points = {}
    
    bandwidth_atts = attributes['bandwidth'][0]

    name_pattern = lambda v: 'eip' in v and v.endswith(user[-2:])
    total_score = check_attribute(NAME, bandwidth_atts, total_score, name_pattern)

    charge_pattern = lambda v: 'traffic' == v
    total_score = check_attribute('charge_mode', bandwidth_atts, total_score, charge_pattern)

    size_pattern = lambda v: 100 == v
    total_score = check_attribute('size', bandwidth_atts, total_score, size_pattern)

    status_pattern = lambda v: 'BOUND' == v
    total_score = check_attribute('status', attributes, total_score, status_pattern)

    time_att = time_check(attributes)

    return total_score, time_att, points


def check_rds(attributes:dict, total_score:int, vpc_id:str, subnet_id:str, user:str
              ) -> tuple[int, str, dict]:

    points = {}
    
    db_atts = attributes[DB][0]

    vpc_id_pattern = lambda v: vpc_id == v
    total_score = check_attribute('vpc_id', attributes, total_score, vpc_id_pattern)

    subnet_id_pattern = lambda v: subnet_id == v
    total_score = check_attribute('subnet_id', attributes, total_score, subnet_id_pattern)

    type_pattern = lambda v: 'MySQL' == v
    total_score = check_attribute(TYPE, db_atts, total_score, type_pattern)

    port_pattern = lambda v: 3306 == v
    total_score = check_attribute('port', db_atts, total_score, port_pattern)

    version_pattern = lambda v: '5.7' == v
    total_score = check_attribute('version', db_atts, total_score, version_pattern)

    name_pattern = lambda v: 'rds' in v and v.endswith(user[-2:])
    total_score = check_attribute(NAME, attributes, total_score, name_pattern)

    flavor_pattern = lambda v: 'rds.mysql.n1.large.4.ha' == v
    total_score = check_attribute(FLAVOR, attributes, total_score, flavor_pattern)

    created = attributes.get('created')
    created = created[11:19]

    return total_score, created, points


def check_gaussdb(attributes:dict, total_score:int, sec_group_id:str, subnet_id:str, user:str
                  ) -> tuple[int, dict]:

    points = {}

    sec_group_id_pattern = lambda v: sec_group_id == v
    total_score = check_attribute('security_group_id', attributes, total_score, 
                                  sec_group_id_pattern)
    
    subnet_id_pattern = lambda v: subnet_id == v
    total_score = check_attribute('subnet_id', attributes, total_score,
                                   subnet_id_pattern)

    name_pattern = lambda v: 'gauss' in v and v.endswith(user[-2:])
    total_score = check_attribute(NAME, attributes, total_score, name_pattern)

    flavor_pattern = lambda v: 'gaussdb.mysql.large.x86.4' == v
    total_score = check_attribute(FLAVOR, attributes, total_score, flavor_pattern)

    return total_score, points


def check_resources(json_object:dict, total_score:int, user:str) -> tuple[int, str]:

    # Dictionary just to be easier to check each resource attributes.
    resources = {
        'VPC': {}, 'ECS': {}, 'EIP': {}, 'RDS': {},
        'GAUSSDB': {}, 'SECGROUP': {}, 'SUBNET_DB': {}, 'SUBNET_ECS': {},
    }

    # Dictionary to record the creation time of resources. Later we will check
    # which of these is the most recent.
    creation_time = {
        'ECS': '', 'SECGROUP': '', 'RDS': '', 'EIP': ''
    }

    # Dictionary for the points of each resource.
    points = {
        'VPC': {}, 'ECS': {}, 'EIP': {}, 'RDS': {},
        'GAUSSDB': {}, 'SECGROUP': {}, 'SUBNET_DB': {}, 'SUBNET_ECS': {},
    }
    
    # Collect the attributes from each resource created from terraform.tfstate
    # and store them in the `creation_time` dictionary. We do this because the
    # file contains data that it is not ordered (i.e. resources that depend on
    # each other may appear in different order).
    for element in json_object.get('resources', []):
        
        instance = element.get('instances', [])[0]
        attributes = instance.get('attributes', {})
        
        if element.get(TYPE) == 'huaweicloud_vpc':
            resources['VPC'] = attributes
        
        elif element.get(TYPE) == 'huaweicloud_vpc_subnet':
            if ECS in attributes.get(NAME):
                resources['SUBNET_ECS'] = attributes
            elif DB in attributes.get(NAME):
                resources['SUBNET_DB'] = attributes

        elif element.get(TYPE) == 'huaweicloud_networking_secgroup':
            resources['SECGROUP'] = attributes

        elif element.get(TYPE) == 'huaweicloud_compute_instance':
            resources['ECS'] = attributes

        elif element.get(TYPE) == 'huaweicloud_vpc_eip':
            resources['EIP'] = attributes

        elif element.get(TYPE) == 'huaweicloud_rds_instance':
            resources['RDS'] = attributes
            
        elif element.get(TYPE) == 'huaweicloud_gaussdb_mysql_instance':
            resources['GAUSSDB'] = attributes

    # Check if the resources have been created correctly.
    total_score, vpc_id, points['VPC'] = check_vpc(resources['VPC'], total_score, user)
    total_score, subnet_db_id, points['SUBNET_DB'] = check_subnet(resources['SUBNET_DB'], total_score, vpc_id, user)
    total_score, subnet_ecs_id, points['SUBNET_ECS'] = check_subnet(resources['SUBNET_ECS'], total_score, vpc_id, user)
    total_score, sec_group_id, creation_time['SECGROUP'], points['SECGROUP'] = check_sec_group(resources['SECGROUP'], total_score, user)
    total_score, creation_time['ECS'], points['ECS'] = check_ecs(resources['ECS'], total_score, subnet_ecs_id, sec_group_id, user)
    total_score, creation_time['EIP'], points['EIP'] = check_eip(resources['EIP'], total_score, user)
    total_score, creation_time['RDS'], points['RDS'] = check_rds(resources['RDS'], total_score, vpc_id, subnet_db_id, user)
    total_score, points['GAUSSDB'] = check_gaussdb(resources['GAUSSDB'], total_score, sec_group_id, subnet_db_id, user)

    # Find the oldest and most recent time.
    oldest = creation_time['ECS']
    most_recent = creation_time['ECS']
    for _, t in creation_time.items():
        if t > most_recent:
            most_recent = t
        elif t < oldest:
            oldest = t
    
    return total_score, most_recent


def execute(tf_file:str, user:str) -> tuple[int, str]: # TODO: Mudar aqui

    try:
        # Read the tfstate file.
        with open(f'{tf_file}', 'r') as tfstate_file:
            json_object = json.load(tfstate_file)
    except Exception as e:
        print(e)

    total_score:int = 0
    total_score, creation_time = check_resources(json_object, total_score, user) # TODO: Mudar aqui
    return total_score, creation_time