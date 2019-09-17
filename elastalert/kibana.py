# -*- coding: utf-8 -*-
# flake8: noqa
import logging
import json
import os.path
import prison
import urllib.error
import urllib.parse
import urllib.request

from .util import EAException

dashboard_temp = {'editable': True,
                  'failover': False,
                  'index': {'default': 'NO_TIME_FILTER_OR_INDEX_PATTERN_NOT_MATCHED',
                            'interval': 'none',
                            'pattern': '',
                            'warm_fields': True},
                  'loader': {'hide': False,
                             'load_elasticsearch': True,
                             'load_elasticsearch_size': 20,
                             'load_gist': True,
                             'load_local': True,
                             'save_default': True,
                             'save_elasticsearch': True,
                             'save_gist': False,
                             'save_local': True,
                             'save_temp': True,
                             'save_temp_ttl': '30d',
                             'save_temp_ttl_enable': True},
                  'nav': [{'collapse': False,
                           'enable': True,
                           'filter_id': 0,
                           'notice': False,
                           'now': False,
                           'refresh_intervals': ['5s',
                                                 '10s',
                                                 '30s',
                                                 '1m',
                                                 '5m',
                                                 '15m',
                                                 '30m',
                                                 '1h',
                                                 '2h',
                                                 '1d'],
                           'status': 'Stable',
                           'time_options': ['5m',
                                            '15m',
                                            '1h',
                                            '6h',
                                            '12h',
                                            '24h',
                                            '2d',
                                            '7d',
                                            '30d'],
                           'timefield': '@timestamp',
                           'type': 'timepicker'}],
                  'panel_hints': True,
                  'pulldowns': [{'collapse': False,
                                 'enable': True,
                                 'notice': True,
                                 'type': 'filtering'}],
                  'refresh': False,
                  'rows': [{'collapsable': True,
                            'collapse': False,
                            'editable': True,
                            'height': '350px',
                            'notice': False,
                            'panels': [{'annotate': {'enable': False,
                                                     'field': '_type',
                                                     'query': '*',
                                                     'size': 20,
                                                     'sort': ['_score', 'desc']},
                                        'auto_int': True,
                                        'bars': True,
                                        'derivative': False,
                                        'editable': True,
                                        'fill': 3,
                                        'grid': {'max': None, 'min': 0},
                                        'group': ['default'],
                                        'interactive': True,
                                        'interval': '1m',
                                        'intervals': ['auto',
                                                      '1s',
                                                      '1m',
                                                      '5m',
                                                      '10m',
                                                      '30m',
                                                      '1h',
                                                      '3h',
                                                      '12h',
                                                      '1d',
                                                      '1w',
                                                      '1M',
                                                      '1y'],
                                        'legend': True,
                                        'legend_counts': True,
                                        'lines': False,
                                        'linewidth': 3,
                                        'mode': 'count',
                                        'options': True,
                                        'percentage': False,
                                        'pointradius': 5,
                                        'points': False,
                                        'queries': {'ids': [0], 'mode': 'all'},
                                        'resolution': 100,
                                        'scale': 1,
                                        'show_query': True,
                                        'span': 12,
                                        'spyable': True,
                                        'stack': True,
                                        'time_field': '@timestamp',
                                        'timezone': 'browser',
                                        'title': 'Events over time',
                                        'tooltip': {'query_as_alias': True,
                                                      'value_type': 'cumulative'},
                                        'type': 'histogram',
                                        'value_field': None,
                                        'x-axis': True,
                                        'y-axis': True,
                                        'y_format': 'none',
                                        'zerofill': True,
                                        'zoomlinks': True}],
                            'title': 'Graph'},
                           {'collapsable': True,
                            'collapse': False,
                            'editable': True,
                            'height': '350px',
                            'notice': False,
                            'panels': [{'all_fields': False,
                                        'editable': True,
                                        'error': False,
                                        'field_list': True,
                                        'fields': [],
                                        'group': ['default'],
                                        'header': True,
                                        'highlight': [],
                                        'localTime': True,
                                        'normTimes': True,
                                        'offset': 0,
                                        'overflow': 'min-height',
                                        'pages': 5,
                                        'paging': True,
                                        'queries': {'ids': [0], 'mode': 'all'},
                                        'size': 100,
                                        'sort': ['@timestamp', 'desc'],
                                        'sortable': True,
                                        'span': 12,
                                        'spyable': True,
                                        'status': 'Stable',
                                        'style': {'font-size': '9pt'},
                                        'timeField': '@timestamp',
                                        'title': 'All events',
                                        'trimFactor': 300,
                                        'type': 'table'}],
                            'title': 'Events'}],
                  'services': {'filter': {'ids': [0],
                                          'list': {'0': {'active': True,
                                                         'alias': '',
                                                         'field': '@timestamp',
                                                         'from': 'now-24h',
                                                         'id': 0,
                                                         'mandate': 'must',
                                                         'to': 'now',
                                                         'type': 'time'}}},
                               'query': {'ids': [0],
                                         'list': {'0': {'alias': '',
                                                        'color': '#7EB26D',
                                                        'enable': True,
                                                        'id': 0,
                                                        'pin': False,
                                                        'query': '',
                                                        'type': 'lucene'}}}},
                  'style': 'dark',
                  'title': 'ElastAlert Alert Dashboard'}

kibana4_time_temp = "(refreshInterval:(display:Off,section:0,value:0),time:(from:'%s',mode:absolute,to:'%s'))"

def set_time(dashboard, start, end):
    dashboard['services']['filter']['list']['0']['from'] = start
    dashboard['services']['filter']['list']['0']['to'] = end


def set_index_name(dashboard, name):
    dashboard['index']['default'] = name


def set_timestamp_field(dashboard, field):
    # set the nav timefield if we don't want @timestamp
    dashboard['nav'][0]['timefield'] = field

    # set the time_field for each of our panels
    for row in dashboard.get('rows'):
        for panel in row.get('panels'):
            panel['time_field'] = field

    # set our filter's  time field
    dashboard['services']['filter']['list']['0']['field'] = field


def add_filter(dashboard, es_filter):
    next_id = max(dashboard['services']['filter']['ids']) + 1

    kibana_filter = {'active': True,
                     'alias': '',
                     'id': next_id,
                     'mandate': 'must'}

    if 'not' in es_filter:
        es_filter = es_filter['not']
        kibana_filter['mandate'] = 'mustNot'

    if 'query' in es_filter:
        es_filter = es_filter['query']
        if 'query_string' in es_filter:
            kibana_filter['type'] = 'querystring'
            kibana_filter['query'] = es_filter['query_string']['query']
    elif 'term' in es_filter:
        kibana_filter['type'] = 'field'
        f_field, f_query = list(es_filter['term'].items())[0]
        # Wrap query in quotes, otherwise certain characters cause Kibana to throw errors
        if isinstance(f_query, str):
            f_query = '"%s"' % (f_query.replace('"', '\\"'))
        if isinstance(f_query, list):
            # Escape quotes
            f_query = [item.replace('"', '\\"') for item in f_query]
            # Wrap in quotes
            f_query = ['"%s"' % (item) for item in f_query]
            # Convert into joined query
            f_query = '(%s)' % (' AND '.join(f_query))
        kibana_filter['field'] = f_field
        kibana_filter['query'] = f_query
    elif 'range' in es_filter:
        kibana_filter['type'] = 'range'
        f_field, f_range = list(es_filter['range'].items())[0]
        kibana_filter['field'] = f_field
        kibana_filter.update(f_range)
    else:
        raise EAException("Could not parse filter %s for Kibana" % (es_filter))

    dashboard['services']['filter']['ids'].append(next_id)
    dashboard['services']['filter']['list'][str(next_id)] = kibana_filter


def set_name(dashboard, name):
    dashboard['title'] = name


def set_included_fields(dashboard, fields):
    dashboard['rows'][1]['panels'][0]['fields'] = list(set(fields))


def filters_from_dashboard(db):
    filters = db['services']['filter']['list']
    config_filters = []
    or_filters = []
    for filter in list(filters.values()):
        filter_type = filter['type']
        if filter_type == 'time':
            continue

        if filter_type == 'querystring':
            config_filter = {'query': {'query_string': {'query': filter['query']}}}

        if filter_type == 'field':
            config_filter = {'term': {filter['field']: filter['query']}}

        if filter_type == 'range':
            config_filter = {'range': {filter['field']: {'from': filter['from'], 'to': filter['to']}}}

        if filter['mandate'] == 'mustNot':
            config_filter = {'not': config_filter}

        if filter['mandate'] == 'either':
            or_filters.append(config_filter)
        else:
            config_filters.append(config_filter)

    if or_filters:
        config_filters.append({'or': or_filters})

    return config_filters


def kibana4_dashboard_link(dashboard, starttime, endtime):
    dashboard = os.path.expandvars(dashboard)
    time_settings = kibana4_time_temp % (starttime, endtime)
    time_settings = urllib.parse.quote(time_settings)
    return "%s?_g=%s" % (dashboard, time_settings)

kibana5_and_6_versions = frozenset(['5.6', '6.0', '6.1', '6.2', '6.3', '6.4', '6.5', '6.6', '6.7', '6.8'])
kibana7_versions = frozenset(['7.0', '7.1', '7.2', '7.3'])

def kibana_discover_link(kibana_version, discover_url, index, columns, filters, query_keys, starttime, endtime):

    if kibana_version in kibana5_and_6_versions:
        globalState = kibana6_disover_global_state(starttime, endtime)
        appState = kibana6_kibana7_app_state(index, columns, filters, query_keys)

    elif kibana_version in kibana7_versions:
        globalState = kibana7_disover_global_state(starttime, endtime)
        appState = kibana6_kibana7_app_state(index, columns, filters, query_keys)

    else:
        logging.warning(
            'Unknown kibana discover app version %s' % (
                kibana_version
            )
        )
        return None

    return "%s?_g=%s&_a=%s" % (
        os.path.expandvars(discover_url),
        urllib.parse.quote(globalState),
        urllib.parse.quote(appState)
    )

def kibana6_disover_global_state(starttime, endtime):
    return prison.dumps( {
        'refreshInterval': {
            'pause': True,
            'value': 0
        },
        'time': {
            'from': starttime,
            'mode': 'absolute',
            'to': endtime
        }
    } )

def kibana7_disover_global_state(starttime, endtime):
    return prison.dumps( {
        'refreshInterval': {
            'pause': True,
            'value': 0
        },
        'time': {
            'from': starttime,
            'to': endtime
        }
    } )

def kibana6_kibana7_app_state(index, columns, filters, query_keys):
    app_filters = []

    if filters:
        bool_filter = { 'must': filters }
        app_filters.append( {
            '$state': {
                'store': 'appState'
            },
            'bool': bool_filter,
            'meta': {
                'alias': 'filter',
                'disabled': False,
                'index': index,
                'key': 'bool',
                'negate': False,
                'type': 'custom',
                'value': json.dumps(bool_filter, separators=(',', ':'))
            },
        } )

    if query_keys:
        for key in query_keys:
            value = query_keys[ key ]
            app_filters.append( {
                '$state': {
                    'store': 'appState'
                },
                'meta': {
                    'alias': None,
                    'disabled': False,
                    'index': index,
                    'key': key,
                    'negate': False,
                    'params': {
                        'query': value,
                        'type': 'phrase'
                    },
                    'type': 'phrase',
                    'value': value
                },
                'query': {
                    'match': {
                        key: {
                            'query': value,
                            'type': 'phrase'
                        }
                    }
                },
            } )

    return prison.dumps( {
        'columns': columns,
        'filters': app_filters,
        'index': index,
        'interval': 'auto'
    } )
