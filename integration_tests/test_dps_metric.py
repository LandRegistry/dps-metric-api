import unittest
from integration_tests.utilities import helpers
from dps_metric_api.main import app


class TestDPSMetricAPI(unittest.TestCase):

    URL_DPS_METRIC = '/v1/metric'

    def setUp(self):
        helpers.teardown_metric_test_entry()

    def tearDown(self):
        helpers.teardown_metric_test_entry()

    def test_insert_metric(self):
        payload = {
            "user": {
                "ckan_user_id": "123-456-123-abc",
                "user_type": "oversea-individual",
                "status": "Pending"
            },
            "activity": {
                "activity_type": "application_received",
                "dataset": None,
                "filename": None
            }
        }

        headers = {'Accept': 'application/json', 'Content-type': 'application/json'}

        with app.test_client() as c:
            post_response = c.post(self.URL_DPS_METRIC, json=payload, headers=headers)
            get_response = c.get('{}/{}'.format(self.URL_DPS_METRIC, payload['user']['ckan_user_id']), headers=headers)

        self.assertEqual(post_response.status_code, 201)
        self.assertEqual(get_response.status_code, 200)

        get_response_body = get_response.get_json()

        self.assertTrue('activity_metrics' in get_response_body)
        self.assertTrue('user_metrics' in get_response_body)
