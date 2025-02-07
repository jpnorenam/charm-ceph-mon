# Copyright 2016 Canonical Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
import unittest
import os
import yaml

from unittest.mock import patch


def load_config():
    '''
    Walk backwords from __file__ looking for config.yaml, load and return the
    'options' section'
    '''
    config = None
    f = __file__
    while config is None:
        d = os.path.dirname(f)
        if os.path.isfile(os.path.join(d, 'config.yaml')):
            config = os.path.join(d, 'config.yaml')
            break
        f = d

    if not config:
        logging.error('Could not find config.yaml in any parent directory '
                      'of {}. '.format(f))
        raise Exception

    return yaml.safe_load(open(config).read())['options']


def get_default_config():
    '''
    Load default charm config from config.yaml return as a dict.
    If no default is set in config.yaml, its value is None.
    '''
    default_config = {}
    config = load_config()
    for k, v in config.items():
        if 'default' in v:
            default_config[k] = v['default']
        else:
            default_config[k] = None
    return default_config


class CharmTestCase(unittest.TestCase):

    def setUp(self, obj=None, patches=None):
        super(CharmTestCase, self).setUp()
        self.patches = patches or []
        self.obj = obj or []
        self.test_config = TestConfig()
        self.test_relation = TestRelation()
        self.test_leader_settings = TestLeaderSettings()
        self.patch_all()

    def patch(self, method):
        _m = patch.object(self.obj, method)
        mock = _m.start()
        self.addCleanup(_m.stop)
        return mock

    def patch_all(self):
        for method in self.patches:
            setattr(self, method, self.patch(method))


class TestConfig(object):

    def __init__(self):
        self.config = get_default_config()
        self.config_changed = {}
        self.config_changed.setdefault(False)
        self._previous = get_default_config()

    def __call__(self, key=None):
        if key:
            return self[key]
        else:
            return self

    def get(self, attr=None):
        if not attr:
            # Return a copy of self to allow emulation closer to what
            # hookenv.config() returns (not a dict).
            return self
        try:
            return self.config[attr]
        except KeyError:
            return None

    def get_all(self):
        return self.config

    def set(self, attr, value):
        if attr not in self.config:
            raise KeyError
        self.config[attr] = value

    def __getitem__(self, item):
        return self.config[item]

    def changed(self, attr):
        return self.config_changed[attr]

    def set_changed(self, attr, changed=True):
        self.config_changed[attr] = changed

    def set_previous(self, key, value):
        self._previous[key] = value

    def previous(self, key):
        return self._previous[key]


class TestRelation(object):

    def __init__(self, relation_data={}):
        self.relation_data = relation_data

    def set(self, relation_data):
        self.relation_data = relation_data

    def get(self, attr=None, unit=None, rid=None):
        if attr is None:
            return self.relation_data
        elif attr in self.relation_data:
            return self.relation_data[attr]
        return None


class TestLeaderSettings(object):

    def __init__(self, settings={}):
        self.settings = settings

    def set(self, settings):
        self.settings = settings

    def get(self, attr=None):
        if attr is None:
            return self.settings
        elif attr in self.settings:
            return self.settings[attr]
        return None
