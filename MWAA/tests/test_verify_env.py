import argparse
import pytest
from verify_env import verify_env


def test_verify_boto3():
    '''
    test version equal to 1.16.25
    test various version numbers below
    '''
    assert verify_env.verify_boto3('1.17.4')
    assert verify_env.verify_boto3('1.17.33')
    assert verify_env.verify_boto3('1.16.27')
    assert verify_env.verify_boto3('1.16.26')
    assert verify_env.verify_boto3('1.16.25')
    assert not verify_env.verify_boto3('1.16.24')
    assert not verify_env.verify_boto3('1.16.23')
    assert not verify_env.verify_boto3('1.16.22')
    assert not verify_env.verify_boto3('1.16.21')
    assert not verify_env.verify_boto3('1.7.65')
    assert not verify_env.verify_boto3('1.9.105')
    assert not verify_env.verify_boto3('1.10.33')


def test_validation_region():
    '''
    test various inputs for regions and all valid MWAA regions
    https://aws.amazon.com/about-aws/global-infrastructure/regional-product-services/
    '''
    regions = [
        'us-east-2',
        'us-east-1',
        'us-west-2',
        'ap-southeast-1',
        'ap-southeast-2',
        'ap-northeast-1',
        'eu-central-1',
        'eu-west-1',
        'eu-north-1'
    ]
    for region in regions:
        assert verify_env.validation_region(region) == region
    unsupport_regions = [
        'us-west-1',
        'af-south-1',
        'ap-east-1',
        'ap-south-1',
        'ap-northeast-3',
        'ap-northeast-2',
        'ca-central-1',
        'eu-west-2',
        'eu-south-1',
        'eu-west-3',
        'me-sourth-1',
        'sa-east-1'
    ]
    for unsupport_region in unsupport_regions:
        with pytest.raises(argparse.ArgumentTypeError) as excinfo:
            verify_env.validation_region(unsupport_region)
        assert ("%s is an invalid REGION value" % unsupport_region) in str(excinfo.value)
    bad_regions = [
        'us-east-11',
        'us-west-3',
        'eu-wheat-3'
    ]
    for region in bad_regions:
        with pytest.raises(argparse.ArgumentTypeError) as excinfo:
            verify_env.validation_region(region)
        assert ("%s is an invalid REGION value" % region) in str(excinfo.value)


def test_validate_envname():
    '''
    test invalid and valid names for MWAA environment
    '''
    with pytest.raises(argparse.ArgumentTypeError) as excinfo:
        env_name = '42'
        verify_env.validate_envname(env_name)
    assert ("%s is an invalid environment name value" % env_name) in str(excinfo.value)
    env_name = 'test'
    result = verify_env.validate_envname(env_name)
    assert result == env_name


def test_validate_profile():
    '''
    test invalid and valid names for MWAA environment
    '''
    with pytest.raises(argparse.ArgumentTypeError) as excinfo:
        profile_name = 'test space'
        verify_env.validation_profile(profile_name)
    assert ("%s is an invalid profile name value" % profile_name) in str(excinfo.value)
    profile_name = 'test'
    result = verify_env.validation_profile(profile_name)
    assert result == profile_name
    profile_name = '42'
    result = verify_env.validation_profile(profile_name)
    assert result == profile_name
    profile_name = '4HelloWorld2'
    result = verify_env.validation_profile(profile_name)
    assert result == profile_name
    profile_name = 'HelloWorld'
    result = verify_env.validation_profile(profile_name)
    assert result == profile_name


def test_check_ingress_acls():
    ''' goes through the following scenarios
    * if no acls are passed
    * if there is an allow
    * if there is a deny but no allow
    '''
    acls = []
    src_port_from = 5432
    src_port_to = 5432
    result = verify_env.check_ingress_acls(acls, src_port_from, src_port_to)
    assert result == ''
    acls = [
        {
            'CidrBlock': '0.0.0.0/0',
            'Egress': False,
            'Protocol': '-1',
            'RuleAction': 'allow',
            'RuleNumber': 1
        },
        {
            'CidrBlock': '0.0.0.0/0',
            'Egress': False,
            'Protocol': '-1',
            'RuleAction': 'deny',
            'RuleNumber': 32767
        }
    ]
    result = verify_env.check_ingress_acls(acls, src_port_from, src_port_to)
    assert result
    acls = [
        {
            'CidrBlock': '0.0.0.0/0',
            'Egress': False,
            'Protocol': '-1',
            'RuleAction': 'deny',
            'RuleNumber': 32767
        }
    ]
    result = verify_env.check_ingress_acls(acls, src_port_from, src_port_to)
    assert not result


def test_check_egress_acls():
    ''' goes through the following scenarios
    * if no acls are passed
    * if there is an allow
    * if there is a deny but no allow
    '''
    acls = []
    dest_port = 5432
    result = verify_env.check_egress_acls(acls, dest_port)
    assert result == ''
    acls = [
        {
            'CidrBlock': '0.0.0.0/0',
            'Egress': False,
            'Protocol': '-1',
            'RuleAction': 'allow',
            'RuleNumber': 1
        },
        {
            'CidrBlock': '0.0.0.0/0',
            'Egress': False,
            'Protocol': '-1',
            'RuleAction': 'deny',
            'RuleNumber': 32767
        }
    ]
    result = verify_env.check_egress_acls(acls, dest_port)
    assert result
    acls = [
        {
            'CidrBlock': '0.0.0.0/0',
            'Egress': False,
            'Protocol': '-1',
            'RuleAction': 'deny',
            'RuleNumber': 32767
        }
    ]
    result = verify_env.check_egress_acls(acls, dest_port)
    assert not result
