# -*- coding: utf-8 -*-
# flake8: noqa
import datetime
import logging
import json
import os.path
import prison
import urllib.parse

from .util import EAException
from .util import lookup_es_key
from .util import ts_add


kibana5_kibana6_versions = frozenset(['5.6', '6.0', '6.1', '6.2', '6.3', '6.4', '6.5', '6.6', '6.7', '6.8'])
kibana7_versions = frozenset(['7.0', '7.1', '7.2', '7.3'])


def kibana_discover_url(rule, match):
    ''' Creates a link for a kibana discover app which has time set to the match. '''
    kibana_version = rule.get('use_kibana_discover')

    discover_url = rule.get('kibana_discover_url')
    if not discover_url:
        logging.warning(
            'use_kibana_discover was configured without kibana_discover_url for rule %s' % (
                rule['name']
            )
        )
        return None

    index = rule.get('kibana_discover_index_pattern_id')
    if not index:
        logging.warning(
            'use_kibana_discover was configured without kibana_discover_index_pattern_id for rule %s' % (
                rule['name']
            )
        )
        return None

    columns = rule.get('kibana_discover_columns', ['_source'])
    filters = rule.get('filter', [])

    query_keys = {}
    if 'query_key' in rule:
        rule_query_keys=rule.get('compound_query_key', [rule['query_key']])
        for qk in rule_query_keys:
            query_keys[qk] = lookup_es_key(match, qk)

    timestamp = lookup_es_key(match, rule['timestamp_field'])
    start_timedelta = rule.get('kibana_discover_start_timedelta', rule.get('timeframe', datetime.timedelta(minutes=10)))
    starttime = ts_add(timestamp, -start_timedelta)
    end_timedelta = rule.get('kibana_discover_end_timedelta', rule.get('timeframe', datetime.timedelta(minutes=10)))
    endtime = ts_add(timestamp, end_timedelta)

    if kibana_version in kibana5_kibana6_versions:
        globalState = kibana6_disover_global_state(starttime, endtime)
        appState = kibana_discover_app_state(index, columns, filters, query_keys)

    elif kibana_version in kibana7_versions:
        globalState = kibana7_disover_global_state(starttime, endtime)
        appState = kibana_discover_app_state(index, columns, filters, query_keys)

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
        'filters': [],
        'refreshInterval': {
            'pause': True,
            'value': 0
        },
        'time': {
            'from': starttime,
            'to': endtime
        }
    } )


def kibana_discover_app_state(index, columns, filters, query_keys):
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
            if value is None:
                value_str=''
            else:
                value_str = str(value)
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
                    'value': value_str
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
