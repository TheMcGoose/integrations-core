# -*- coding: utf-8 -*-

# (C) Datadog, Inc. 2018-present
# All rights reserved
# Licensed under a 3-clause BSD style license (see LICENSE)

import mock
import pytest

from datadog_checks.http_check import HTTPCheck


def test__init__():
    # empty values should be ignored
    init_config = {'ca_certs': ''}
    # `get_ca_certs_path` needs to be mocked because it's used as fallback when
    # init_config doesn't contain `ca_certs`
    with mock.patch('datadog_checks.http_check.http_check.get_ca_certs_path', return_value='bar'):
        http_check = HTTPCheck('http_check', init_config, [{}])
        assert http_check.ca_certs == 'bar'

    # normal case
    init_config = {'ca_certs': 'foo'}
    http_check = HTTPCheck('http_check', init_config, [{}])
    assert http_check.ca_certs == 'foo'


def test_instances_do_not_share_data():
    http_check_1 = HTTPCheck('http_check', {'ca_certs': 'foo'}, [{}])
    http_check_1.HTTP_CONFIG_REMAPPER['ca_certs']['default'] = 'foo'
    http_check_2 = HTTPCheck('http_check', {'ca_certs': 'bar'}, [{}])
    http_check_2.HTTP_CONFIG_REMAPPER['ca_certs']['default'] = 'bar'

    assert http_check_1.HTTP_CONFIG_REMAPPER['ca_certs']['default'] == 'foo'
    assert http_check_2.HTTP_CONFIG_REMAPPER['ca_certs']['default'] == 'bar'


def test_unexisting_ca_cert_should_throw_error():
    instance = {
        'name': 'Test Web VM HTTPS SSL',
        'url': 'https://foo.bar.net/',
        'method': 'get',
        'tls_ca_cert': '/tmp/unexisting.crt',
        'check_certificate_expiration': 'true',
        'days_critical': 60,
        'collect_response_time': 'false',
        'disable_ssl_validation': 'false',
        'skip_proxy': 'false',
    }

    check = HTTPCheck('http_check', {}, [instance])
    with pytest.raises(OSError):
        check.check()
