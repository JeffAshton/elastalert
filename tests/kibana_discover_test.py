from elastalert.kibana_discover import kibana_discover_url


def test_kibana_discover_url_with_discover_url_env_substitution(environ):
    environ.update({
        'KIBANA_HOST': 'kibana',
        'KIBANA_PORT': '5601',
    })
    url = kibana_discover_url(
        rule={
            'use_kibana_discover': '6.8',
            'kibana_discover_url': 'http://$KIBANA_HOST:$KIBANA_PORT/#/discover',
            'kibana_discover_index_pattern_id': 'd6cabfb6-aaef-44ea-89c5-600e9a76991a',
            'timestamp_field': 'timestamp'
        },
        match={
            'timestamp': '2019-09-01T00:30:00Z'
        }
    )
    expectedUrl = (
        'http://kibana:5601/#/discover'
        + '?_g=%28'  # global start
        + 'refreshInterval%3A%28pause%3A%21t%2Cvalue%3A0%29%2C'
        + 'time%3A%28'  # time start
        + 'from%3A%272019-09-01T00%3A20%3A00Z%27%2C'
        + 'mode%3Aabsolute%2C'
        + 'to%3A%272019-09-01T00%3A40%3A00Z%27'
        + '%29'  # time end
        + '%29'  # global end
        + '&_a=%28'  # app start
        + 'columns%3A%21%28_source%29%2C'
        + 'filters%3A%21%28%29%2C'
        + 'index%3Ad6cabfb6-aaef-44ea-89c5-600e9a76991a%2C'
        + 'interval%3Aauto'
        + '%29'  # app end
    )
    assert url == expectedUrl


def test_kibana_discover_url_with_single_filter():
    url = kibana_discover_url(
        rule={
            'use_kibana_discover': '6.8',
            'kibana_discover_url': 'http://kibana:5601/#/discover',
            'kibana_discover_index_pattern_id': 'logs-*',
            'timestamp_field': 'timestamp',
            'filter': [
                {'term': {'level': 30}}
            ]
        },
        match={
            'timestamp': '2019-09-01T00:30:00Z'
        }
    )
    expectedUrl = (
        'http://kibana:5601/#/discover'
        + '?_g=%28'  # global start
        + 'refreshInterval%3A%28pause%3A%21t%2Cvalue%3A0%29%2C'
        + 'time%3A%28'  # time start
        + 'from%3A%272019-09-01T00%3A20%3A00Z%27%2C'
        + 'mode%3Aabsolute%2C'
        + 'to%3A%272019-09-01T00%3A40%3A00Z%27'
        + '%29'  # time end
        + '%29'  # global end
        + '&_a=%28'  # app start
        + 'columns%3A%21%28_source%29%2C'
        + 'filters%3A%21%28'  # filters start
        + '%28'  # filter start
        + '%27%24state%27%3A%28store%3AappState%29%2C'
        + 'bool%3A%28must%3A%21%28%28term%3A%28level%3A30%29%29%29%29%2C'
        + 'meta%3A%28'  # meta start
        + 'alias%3Afilter%2C'
        + 'disabled%3A%21f%2C'
        + 'index%3A%27logs-%2A%27%2C'
        + 'key%3Abool%2C'
        + 'negate%3A%21f%2C'
        + 'type%3Acustom%2C'
        + 'value%3A%27%7B%22must%22%3A%5B%7B%22term%22%3A%7B%22level%22%3A30%7D%7D%5D%7D%27'
        + '%29'  # meta end
        + '%29'  # filter end
        + '%29%2C'  # filters end
        + 'index%3A%27logs-%2A%27%2C'
        + 'interval%3Aauto'
        + '%29'  # app end
    )
    assert url == expectedUrl


def test_kibana_discover_url_with_multiple_filters():
    url = kibana_discover_url(
        rule={
            'use_kibana_discover': '6.8',
            'kibana_discover_url': 'http://kibana:5601/#/discover',
            'kibana_discover_index_pattern_id': '90943e30-9a47-11e8-b64d-95841ca0b247',
            'timestamp_field': 'timestamp',
            'filter': [
                {'term': {'app': 'test'}},
                {'term': {'level': 30}}
            ]
        },
        match={
            'timestamp': '2019-09-01T00:30:00Z'
        }
    )
    expectedUrl = (
        'http://kibana:5601/#/discover'
        + '?_g=%28'  # global start
        + 'refreshInterval%3A%28pause%3A%21t%2Cvalue%3A0%29%2C'
        + 'time%3A%28'  # time start
        + 'from%3A%272019-09-01T00%3A20%3A00Z%27%2C'
        + 'mode%3Aabsolute%2C'
        + 'to%3A%272019-09-01T00%3A40%3A00Z%27'
        + '%29'  # time end
        + '%29'  # global end
        + '&_a=%28'  # app start
        + 'columns%3A%21%28_source%29%2C'
        + 'filters%3A%21%28'  # filters start
        + '%28'  # filter start
        + '%27%24state%27%3A%28store%3AappState%29%2C'
        + 'bool%3A%28must%3A%21%28%28term%3A%28app%3Atest%29%29%2C%28term%3A%28level%3A30%29%29%29%29%2C'
        + 'meta%3A%28'  # meta start
        + 'alias%3Afilter%2C'
        + 'disabled%3A%21f%2C'
        + 'index%3A%2790943e30-9a47-11e8-b64d-95841ca0b247%27%2C'
        + 'key%3Abool%2C'
        + 'negate%3A%21f%2C'
        + 'type%3Acustom%2C'
        + 'value%3A%27%7B%22must%22%3A%5B'  # value start
        + '%7B%22term%22%3A%7B%22app%22%3A%22test%22%7D%7D%2C%7B%22term%22%3A%7B%22level%22%3A30%7D%7D'
        + '%5D%7D%27'  # value end
        + '%29'  # meta end
        + '%29'  # filter end
        + '%29%2C'  # filters end
        + 'index%3A%2790943e30-9a47-11e8-b64d-95841ca0b247%27%2C'
        + 'interval%3Aauto'
        + '%29'  # app end
    )
    print('url: ' + url)
    print('expectedUrl: ' + expectedUrl)
    assert url == expectedUrl


def test_kibana_discover_url_with_int_query_key():
    url = kibana_discover_url(
        rule={
            'use_kibana_discover': '6.8',
            'kibana_discover_url': 'http://kibana:5601/#/discover',
            'kibana_discover_index_pattern_id': 'logs-*',
            'timestamp_field': 'timestamp',
            'query_key': 'response'
        },
        match={
            'timestamp': '2019-09-01T00:30:00Z',
            'response': 200
        }
    )
    expectedUrl = (
        'http://kibana:5601/#/discover'
        + '?_g=%28'  # global start
        + 'refreshInterval%3A%28pause%3A%21t%2Cvalue%3A0%29%2C'
        + 'time%3A%28'  # time start
        + 'from%3A%272019-09-01T00%3A20%3A00Z%27%2C'
        + 'mode%3Aabsolute%2C'
        + 'to%3A%272019-09-01T00%3A40%3A00Z%27'
        + '%29'  # time end
        + '%29'  # global end
        + '&_a=%28'  # app start
        + 'columns%3A%21%28_source%29%2C'
        + 'filters%3A%21%28'  # filters start
        + '%28'  # filters end
        + '%27%24state%27%3A%28store%3AappState%29%2C'
        + 'meta%3A%28'  # meta start
        + 'alias%3A%21n%2C'
        + 'disabled%3A%21f%2C'
        + 'index%3A%27logs-%2A%27%2C'
        + 'key%3Aresponse%2C'
        + 'negate%3A%21f%2C'
        + 'params%3A%28query%3A200%2C'  # params start
        + 'type%3Aphrase'
        + '%29%2C'  # params end
        + 'type%3Aphrase%2C'
        + 'value%3A%27200%27'
        + '%29%2C'  # meta end
        + 'query%3A%28'  # query start
        + 'match%3A%28'  # match start
        + 'response%3A%28'  # reponse start
        + 'query%3A200%2C'
        + 'type%3Aphrase'
        + '%29'  # response end
        + '%29'  # match end
        + '%29'  # query end
        + '%29'  # filter end
        + '%29%2C'  # filters end
        + 'index%3A%27logs-%2A%27%2C'
        + 'interval%3Aauto'
        + '%29'  # app end
    )
    assert url == expectedUrl


def test_kibana_discover_url_with_str_query_key():
    url = kibana_discover_url(
        rule={
            'use_kibana_discover': '6.8',
            'kibana_discover_url': 'http://kibana:5601/#/discover',
            'kibana_discover_index_pattern_id': 'logs-*',
            'timestamp_field': 'timestamp',
            'query_key': 'response'
        },
        match={
            'timestamp': '2019-09-01T00:30:00Z',
            'response': 'ok'
        }
    )
    expectedUrl = (
        'http://kibana:5601/#/discover'
        + '?_g=%28'  # global start
        + 'refreshInterval%3A%28pause%3A%21t%2Cvalue%3A0%29%2C'
        + 'time%3A%28'  # time start
        + 'from%3A%272019-09-01T00%3A20%3A00Z%27%2C'
        + 'mode%3Aabsolute%2C'
        + 'to%3A%272019-09-01T00%3A40%3A00Z%27'
        + '%29'  # time end
        + '%29'  # global end
        + '&_a=%28'  # app start
        + 'columns%3A%21%28_source%29%2C'
        + 'filters%3A%21%28'  # filters start
        + '%28'  # filters end
        + '%27%24state%27%3A%28store%3AappState%29%2C'
        + 'meta%3A%28'  # meta start
        + 'alias%3A%21n%2C'
        + 'disabled%3A%21f%2C'
        + 'index%3A%27logs-%2A%27%2C'
        + 'key%3Aresponse%2C'
        + 'negate%3A%21f%2C'
        + 'params%3A%28query%3Aok%2C'  # params start
        + 'type%3Aphrase'
        + '%29%2C'  # params end
        + 'type%3Aphrase%2C'
        + 'value%3Aok'
        + '%29%2C'  # meta end
        + 'query%3A%28'  # query start
        + 'match%3A%28'  # match start
        + 'response%3A%28'  # reponse start
        + 'query%3Aok%2C'
        + 'type%3Aphrase'
        + '%29'  # response end
        + '%29'  # match end
        + '%29'  # query end
        + '%29'  # filter end
        + '%29%2C'  # filters end
        + 'index%3A%27logs-%2A%27%2C'
        + 'interval%3Aauto'
        + '%29'  # app end
    )
    assert url == expectedUrl
