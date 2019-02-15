#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from urllib.parse import quote_plus
from itertools import chain
from datetime import datetime, date

from leancloud import client, operation


def query_to_params(query, **extra):
    params = {}
    for k, v in chain(query.build_query().dump().items(), extra.items()):
        if v is None:
            continue
        if isinstance(v, dict):
            v = json.dumps(v, separators=(',', ':'))
        else:
            v = str(v)
        params[k] = v
    return params


def convert_value(cls, k, v):
    if isinstance(v, (datetime, date)):
        print(v.strftime('%Y-%m-%dH%H:%I:%S.%fZ'))
        return {'__type': 'Date', 'iso': v.strftime('%Y-%m-%dT%H:%I:%S.%fZ')}
    if isinstance(v, operation.BaseOp):
        return v.dump()
    return cls.__fields__[k].to_leancloud_value(v)


def convert_class_name(name):
    if name in ('User', 'File', 'Followee', 'Follower', 'Installation', 'Role'):
        return f'_{name}'
    return


class Batch(object):
    def __init__(self):
        self._requests = []
        self._post_response = []

    def find(self, query, skip=None, limit=None):
        self._requests.append({
            'method': 'GET',
            'path': '/{0}/classes/{1}'.format(client.SERVER_VERSION,
                                              convert_class_name(query._model.__lc_cls__)),
            'params': query_to_params(query, skip=skip, limit=limit),
        })
        self._post_response.append(lambda r: [query._model(i) for i in r.get('results', [])])
        return self

    def update(self, obj, updates):
        cls = obj.__class__
        data = {k: convert_value(cls, k, v) for (k, v) in updates.items()}
        self._requests.append({
            'method': 'PUT',
            'path': '/{0}/classes/{1}/{2}'.format(client.SERVER_VERSION,
                                                  convert_class_name(cls.__lc_cls__),
                                                  obj.object_id),
            'params': {'fetchWhenSave': 'true'},
            'body': data,
        })
        self._post_response.append(lambda r: cls(r))
        return self

    def create(self, obj):
        # TODO: Nest object creation not support.
        cls = obj.__class__
        data = {k: convert_value(cls, k, v)
                for (k, v) in obj.lc_object._attributes.items()}
        self._requests.append({
            'method': 'POST',
            'path': '/{0}/classes/{1}'.format(client.SERVER_VERSION,
                                              convert_class_name(cls.__lc_cls__)),
            'params': {'fetchWhenSave': 'true'},
            'body': data,
        })
        self._post_response.append(lambda r: cls(r))
        return self

    def execute(self):
        resp = client.post('/batch', params={'requests': self._requests})
        data = resp.json()
        result = []
        for post_fn, resp in zip(self._post_response, data):
            if 'error' in resp:
                result.append((
                    resp.get('code', 1),
                    resp.get('error', 'Unknown Error'),
                ))
            else:
                result.append((
                    0,
                    post_fn(resp.get('success', {}))
                ))
                # result.append(Result.Ok())
        self._requests = []
        self._post_response = []
        return result

    def __call__(self):
        return self.execute()


