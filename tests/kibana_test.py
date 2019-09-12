import copy
import json

from elastalert.kibana import add_filter
from elastalert.kibana import dashboard_temp
from elastalert.kibana import filters_from_dashboard
from elastalert.kibana import kibana4_dashboard_link
from elastalert.kibana import kibana6_discover_link


# Dashboard schema with only filters section
test_dashboard = '''{
  "title": "AD Lock Outs",
  "services": {
    "filter": {
      "list": {
        "0": {
          "type": "time",
          "field": "@timestamp",
          "from": "now-7d",
          "to": "now",
          "mandate": "must",
          "active": true,
          "alias": "",
          "id": 0
        },
        "1": {
          "type": "field",
          "field": "_log_type",
          "query": "\\"active_directory\\"",
          "mandate": "must",
          "active": true,
          "alias": "",
          "id": 1
        },
        "2": {
          "type": "querystring",
          "query": "ad.security_auditing_code:4740",
          "mandate": "must",
          "active": true,
          "alias": "",
          "id": 2
        }
      },
      "ids": [
        0,
        1,
        2
      ]
    }
  }
}'''
test_dashboard = json.loads(test_dashboard)


def test_filters_from_dashboard():
    filters = filters_from_dashboard(test_dashboard)
    assert {'term': {'_log_type': '"active_directory"'}} in filters
    assert {'query': {'query_string': {'query': 'ad.security_auditing_code:4740'}}} in filters


def test_add_filter():
    basic_filter = {"term": {"this": "that"}}
    db = copy.deepcopy(dashboard_temp)
    add_filter(db, basic_filter)
    assert db['services']['filter']['list']['1'] == {
        'field': 'this',
        'alias': '',
        'mandate': 'must',
        'active': True,
        'query': '"that"',
        'type': 'field',
        'id': 1
    }

    list_filter = {"term": {"this": ["that", "those"]}}
    db = copy.deepcopy(dashboard_temp)
    add_filter(db, list_filter)
    assert db['services']['filter']['list']['1'] == {
        'field': 'this',
        'alias': '',
        'mandate': 'must',
        'active': True,
        'query': '("that" AND "those")',
        'type': 'field',
        'id': 1
    }


def test_url_encoded():
    url = kibana4_dashboard_link('example.com/#/Dashboard', '2015-01-01T00:00:00Z', '2017-01-01T00:00:00Z')
    assert not any([special_char in url for special_char in ["',\":;?&=()"]])


def test_url_env_substitution(environ):
    environ.update({
        'KIBANA_HOST': 'kibana',
        'KIBANA_PORT': '5601',
    })
    url = kibana4_dashboard_link(
        'http://$KIBANA_HOST:$KIBANA_PORT/#/Dashboard',
        '2015-01-01T00:00:00Z',
        '2017-01-01T00:00:00Z',
    )
    assert url.startswith('http://kibana:5601/#/Dashboard')


def test_kibana6_discover_link(environ):
    environ.update({
        'KIBANA_HOST': 'kibana',
        'KIBANA_PORT': '5601',
    })
    discover = 'http://$KIBANA_HOST:$KIBANA_PORT/#/discover'
    index = 'logs-*'
    columns = ['timestamp', 'message']
    filters = [{'term': {'level': 30}}]
    starttime = '2019-09-01T00:00:00Z'
    endtime = '2019-09-02T00:00:00Z'
    url = kibana6_discover_link(discover, index, columns, filters, starttime, endtime)
    expectedUrl = (
        'http://kibana:5601/#/discover'
        + '?_g=%28'
        + 'refreshInterval%3A%28pause%3A%21t%2Cvalue%3A0%29%2C'
        + 'time%3A%28'
        + 'from%3A%272019-09-01T00%3A00%3A00Z%27%2C'
        + 'mode%3Aabsolute%2C'
        + 'to%3A%272019-09-02T00%3A00%3A00Z%27'
        + '%29'
        + '%29'
        + '&_a=%28'
        + 'columns%3A%21%28timestamp%2Cmessage%29%2C'
        + 'filters%3A%21%28'
        + '%28'
        + '%27%24state%27%3A%28store%3AappState%29%2C'
        + 'bool%3A%28must%3A%21%28%28term%3A%28level%3A30%29%29%29%29%2C'
        + 'meta%3A%28'
        + 'alias%3AFilter%2C'
        + 'disabled%3A%21f%2C'
        + 'index%3A%27logs-%2A%27%2C'
        + 'key%3Abool%2C'
        + 'negate%3A%21f%2C'
        + 'type%3Acustom%2C'
        + 'value%3A%27%7B%22must%22%3A%5B%7B%22term%22%3A%7B%22level%22%3A30%7D%7D%5D%7D%27'
        + '%29'
        + '%29'
        + '%29%2C'
        + 'index%3A%27logs-%2A%27%2C'
        + 'interval%3Aauto%29'
    )
    assert url == expectedUrl
