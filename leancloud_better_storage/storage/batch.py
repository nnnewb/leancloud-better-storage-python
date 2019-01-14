#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from urllib.parse import quote_plus
from itertools import chain

from leancloud import client


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


class Batch(object):
    def __init__(self):
        self._requests = []
        self._post_response = []

    def find(self, query, skip=None, limit=None):
        self._requests.append({
            'method': 'GET',
            'path': '/{0}/classes/{1}'.format(client.SERVER_VERSION, query._model.__lc_cls__),
            'params': query_to_params(query, skip=skip, limit=limit),
        })
        self._post_response.append(lambda r: [query._model(i) for i in r.get('results', [])])
        return self

    def update(self, obj, updates):
        cls = obj.__class__
        self._requests.append({
            'method': 'PUT',
            'path': '/{0}/classes/{1}/{2}'.format(client.SERVER_VERSION, cls.__lc_cls__, obj.id),
            'params': {'fetchWhenSave': 'true'},
            'body': updates,
        })
        self._post_response.append(lambda r: cls(r))
        return self

    def execute(self):
        data = client.post('/batch', params={'requests': self._requests}).json()
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


