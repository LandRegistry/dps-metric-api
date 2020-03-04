import unittest
import os
import json
from dps_metric_api.main import app
from dps_metric_api.exceptions import ApplicationError
from unittest.mock import patch
from common_utilities import errors


@patch('dps_metric_api.views.v1.dps_metric.service')
class TestDpsMetric(unittest.TestCase):
    directory = os.path.dirname(__file__)
    get_all_data = json.loads(open(os.path.join(directory, 'data/get_all.json'), 'r').read())
    get_metric_by_id = json.loads(open(os.path.join(directory, 'data/get_metric_by_id.json'), 'r').read())
    create_metric = json.loads(open(os.path.join(directory, 'data/create_metric.json'), 'r').read())

    def setUp(self):
        self.app = app.test_client()
        self.headers = {'Accept': 'application/json',
                        'Content-Type': 'application/json'}
        self.sql_error = ('dps_metric_api', 'SQLALCHEMY_ERROR', 'SQL ERROR')
        self.test_error = ('dps_metric_api', 'CASE NOT FOUND', 'TEST ERROR')

    def test_get_all_metrics_ok(self, mock_service):
        mock_service.retrieve_all_metrics.return_value = self.get_all_data

        response = self.app.get('/v1/metric', headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, self.get_all_data)

    def test_get_all_metrics_error(self, mock_service):
        mock_service.retrieve_all_metrics.side_effect = ApplicationError(*errors.get(*self.sql_error))
        expected_err_msg = errors.get_message(*self.sql_error)

        response = self.app.get('/v1/metric', headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual("Failed to retrieve metrics - " + expected_err_msg, response_body['error'])

    def test_get_metric_by_user_ok(self, mock_service):
        mock_service.retrieve_metrics_by_id.return_value = self.get_metric_by_id

        response = self.app.get('/v1/metric/123-456-789-abc', headers=self.headers)

        self.assertEqual(200, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, self.get_metric_by_id)

    def test_get_metric_by_user_id_error(self, mock_service):
        mock_service.retrieve_metrics_by_id.side_effect = ApplicationError(*errors.get(*self.sql_error))
        expected_err_msg = errors.get_message(*self.sql_error)

        response = self.app.get('/v1/metric/123-456-789-abc', headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual("Failed to retrieve metrics for user: 123-456-789-abc with error: " + expected_err_msg,
                         response_body['error'])

    def test_create_metric_ok(self, mock_service):
        mock_service.insert_metric.return_value = self.create_metric['user']['ckan_user_id']
        expected_response = {
            "ckan_user_id": self.create_metric['user']['ckan_user_id'],
            "message": "metric created successfully"
        }

        response = self.app.post('/v1/metric', json=self.create_metric, headers=self.headers)

        self.assertEqual(201, response.status_code)
        response_body = response.get_json()
        self.assertEqual(response_body, expected_response)

    def test_create_metric_error(self, mock_service):
        mock_service.insert_metric.side_effect = ApplicationError(*errors.get(*self.sql_error))
        expected_err_msg = errors.get_message(*self.sql_error)

        response = self.app.post('/v1/metric', json=self.create_metric, headers=self.headers)

        self.assertEqual(500, response.status_code)
        response_body = response.get_json()
        self.assertEqual("Failed to create a metric with error: " + expected_err_msg, response_body['error'])
