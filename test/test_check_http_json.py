#!/usr/bin/env python3


import json
import unittest
from unittest.mock import patch
import sys

sys.path.append('..')

from check_http_json import *


OK_CODE = 0
WARNING_CODE = 1
CRITICAL_CODE = 2
UNKNOWN_CODE = 3


class RulesHelper:
    separator = '.'
    debug = False
    key_threshold_warning = None
    key_value_list = None
    key_value_list_not = None
    key_list = None
    key_threshold_critical = None
    key_value_list_critical = None
    key_value_list_not_critical = None
    key_value_list_unknown = None
    key_list_critical = None
    metric_list = None

    def dash_m(self, data):
        self.metric_list = data
        return self

    def dash_e(self, data):
        self.key_list = data
        return self

    def dash_E(self, data):
        self.key_list_critical = data
        return self

    def dash_q(self, data):
        self.key_value_list = data
        return self

    def dash_Q(self, data):
        self.key_value_list_critical = data
        return self

    def dash_y(self, data):
        self.key_value_list_not = data
        return self

    def dash_Y(self, data):
        self.key_value_list_not_critical = data
        return self

    def dash_w(self, data):
        self.key_threshold_warning = data
        return self

    def dash_c(self, data):
        self.key_threshold_critical = data
        return self


class UtilTest(unittest.TestCase):
    """
    Tests for the util fucntions
    """

    rules = RulesHelper()

    def check_data(self, args, jsondata, code):
        data = json.loads(jsondata)
        nagios = NagiosHelper()
        processor = JsonRuleProcessor(data, args)
        nagios.append_warning(processor.checkWarning())
        nagios.append_critical(processor.checkCritical())
        nagios.append_metrics(processor.checkMetrics())
        self.assertEqual(code, nagios.getCode())

    def test_metrics(self):
        self.check_data(RulesHelper().dash_m(['metric,,1:4,1:5']),
                        '{"metric": 5}', WARNING_CODE)
        self.check_data(RulesHelper().dash_m(['metric,,1:5,1:4']),
                        '{"metric": 5}', CRITICAL_CODE)
        self.check_data(RulesHelper().dash_m(['metric,,1:5,1:5,6,10']),
                        '{"metric": 5}', CRITICAL_CODE)
        self.check_data(RulesHelper().dash_m(['metric,,1:5,1:5,1,4']),
                        '{"metric": 5}', CRITICAL_CODE)
        self.check_data(RulesHelper().dash_m(['metric,s,@1:4,@6:10,1,10']),
                        '{"metric": 5}', OK_CODE)
        self.check_data(RulesHelper().dash_m(['(*).value,s,1:5,1:5']),
                        '[{"value": 5},{"value": 100}]', CRITICAL_CODE)

    def test_exists(self):
        self.check_data(RulesHelper().dash_e(['nothere']),
                        '{"metric": 5}', WARNING_CODE)
        self.check_data(RulesHelper().dash_E(['nothere']),
                        '{"metric": 5}', CRITICAL_CODE)
        self.check_data(RulesHelper().dash_e(['metric']),
                        '{"metric": 5}', OK_CODE)

    def test_equality(self):
        self.check_data(RulesHelper().dash_q(['metric,6']),
                        '{"metric": 5}', WARNING_CODE)
        self.check_data(RulesHelper().dash_Q(['metric,6']),
                        '{"metric": 5}', CRITICAL_CODE)
        self.check_data(RulesHelper().dash_q(['metric,5']),
                        '{"metric": 5}', OK_CODE)

    def test_non_equality(self):
        self.check_data(RulesHelper().dash_y(['metric,6']),
                        '{"metric": 6}', WARNING_CODE)
        self.check_data(RulesHelper().dash_Y(['metric,6']),
                        '{"metric": 6}', CRITICAL_CODE)
        self.check_data(RulesHelper().dash_y(['metric,5']),
                        '{"metric": 6}', OK_CODE)

    def test_warning_thresholds(self):
        self.check_data(RulesHelper().dash_w(['metric,5']),
                        '{"metric": 5}', OK_CODE)
        self.check_data(RulesHelper().dash_w(['metric,5:']),
                        '{"metric": 5}', OK_CODE)
        self.check_data(RulesHelper().dash_w(['metric,~:5']),
                        '{"metric": 5}', OK_CODE)
        self.check_data(RulesHelper().dash_w(['metric,1:5']),
                        '{"metric": 5}', OK_CODE)
        self.check_data(RulesHelper().dash_w(['metric,@5']),
                        '{"metric": 6}', OK_CODE)
        self.check_data(RulesHelper().dash_w(['metric,@5:']),
                        '{"metric": 4}', OK_CODE)
        self.check_data(RulesHelper().dash_w(['metric,@~:5']),
                        '{"metric": 6}', OK_CODE)
        self.check_data(RulesHelper().dash_w(['metric,@1:5']),
                        '{"metric": 6}', OK_CODE)
        self.check_data(RulesHelper().dash_w(['metric,5']),
                        '{"metric": 6}', WARNING_CODE)
        self.check_data(RulesHelper().dash_w(['metric,5:']),
                        '{"metric": 4}', WARNING_CODE)
        self.check_data(RulesHelper().dash_w(['metric,~:5']),
                        '{"metric": 6}', WARNING_CODE)
        self.check_data(RulesHelper().dash_w(['metric,1:5']),
                        '{"metric": 6}', WARNING_CODE)
        self.check_data(RulesHelper().dash_w(['metric,@5']),
                        '{"metric": 5}', WARNING_CODE)
        self.check_data(RulesHelper().dash_w(['metric,@5:']),
                        '{"metric": 5}', WARNING_CODE)
        self.check_data(RulesHelper().dash_w(['metric,@~:5']),
                        '{"metric": 5}', WARNING_CODE)
        self.check_data(RulesHelper().dash_w(['metric,@1:5']),
                        '{"metric": 5}', WARNING_CODE)
        self.check_data(RulesHelper().dash_w(['(*).value,@1:5']),
                        '[{"value": 5},{"value": 1000}]', WARNING_CODE)

    def test_critical_thresholds(self):
        self.check_data(RulesHelper().dash_c(['metric,5']),
                        '{"metric": 5}', OK_CODE)
        self.check_data(RulesHelper().dash_c(['metric,5:']),
                        '{"metric": 5}', OK_CODE)
        self.check_data(RulesHelper().dash_c(['metric,~:5']),
                        '{"metric": 5}', OK_CODE)
        self.check_data(RulesHelper().dash_c(['metric,1:5']),
                        '{"metric": 5}', OK_CODE)
        self.check_data(RulesHelper().dash_c(['metric,@5']),
                        '{"metric": 6}', OK_CODE)
        self.check_data(RulesHelper().dash_c(['metric,@5:']),
                        '{"metric": 4}', OK_CODE)
        self.check_data(RulesHelper().dash_c(['metric,@~:5']),
                        '{"metric": 6}', OK_CODE)
        self.check_data(RulesHelper().dash_c(['metric,@1:5']),
                        '{"metric": 6}', OK_CODE)
        self.check_data(RulesHelper().dash_c(['metric,5']),
                        '{"metric": 6}', CRITICAL_CODE)
        self.check_data(RulesHelper().dash_c(['metric,5:']),
                        '{"metric": 4}', CRITICAL_CODE)
        self.check_data(RulesHelper().dash_c(['metric,~:5']),
                        '{"metric": 6}', CRITICAL_CODE)
        self.check_data(RulesHelper().dash_c(['metric,1:5']),
                        '{"metric": 6}', CRITICAL_CODE)
        self.check_data(RulesHelper().dash_c(['metric,@5']),
                        '{"metric": 5}', CRITICAL_CODE)
        self.check_data(RulesHelper().dash_c(['metric,@5:']),
                        '{"metric": 5}', CRITICAL_CODE)
        self.check_data(RulesHelper().dash_c(['metric,@~:5']),
                        '{"metric": 5}', CRITICAL_CODE)
        self.check_data(RulesHelper().dash_c(['metric,@1:5']),
                        '{"metric": 5}', CRITICAL_CODE)
        self.check_data(RulesHelper().dash_c(['(*).value,@1:5']),
                        '[{"value": 5},{"value": 1000}]', CRITICAL_CODE)

    def test_separator(self):
        rules = RulesHelper()
        rules.separator = '_'
        self.check_data(
            rules.dash_q(
                ['(0)_gauges_jvm.buffers.direct.capacity(1)_value,1234']),
            '''[{ "gauges": { "jvm.buffers.direct.capacity": [
            {"value": 215415},{"value": 1234}]}}]''',
            OK_CODE)
        self.check_data(
            rules.dash_q(
                ['(*)_gauges_jvm.buffers.direct.capacity(1)_value,1234']),
            '''[{ "gauges": { "jvm.buffers.direct.capacity": [
            {"value": 215415},{"value": 1234}]}},
            { "gauges": { "jvm.buffers.direct.capacity": [
            {"value": 215415},{"value": 1235}]}}]''',
            WARNING_CODE)