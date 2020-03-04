import unittest
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import ProgrammingError
from common_utilities import errors

from dps_metric_api.main import app
from dps_metric_api.services import dps_metric_service as service
from dps_metric_api.exceptions import ApplicationError


@patch('dps_metric_api.services.dps_metric_service.db')
@patch('dps_metric_api.services.dps_metric_service.User')
@patch('dps_metric_api.services.dps_metric_service.Activity')
@patch('dps_metric_api.services.dps_metric_service._extract_rows')
class TestService(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.error = ProgrammingError('stuff failed', 'Program', 'Error')

    def test_retrieve_all_metrics_ok(self, mock_extract, *_):
        mock_extract.return_value = [{'foo': 'bar'}]
        result = service.retrieve_all_metrics()
        self.assertEqual(result, {'activity_metrics': [{'foo': 'bar'}], 'user_metrics': [{'foo': 'bar'}]})

    def test_retrieve_all_metrics_error(self, mock_extract, *_):
        mock_extract.side_effect = ApplicationError('failed', 500)

        with self.assertRaises(ApplicationError) as context:
            service.retrieve_all_metrics()

        self.assertEqual(context.exception.message, 'failed')
        self.assertEqual(context.exception.code, 500)

    def test_retrieve_all_metrics_sql_error(self, mock_extract, mock_activity, *_):
        mock_extract.return_value = [{'foo': 'bar'}]
        with self.assertRaises(ApplicationError) as context:
            mock_activity.select_all.side_effect = self.error
            service.retrieve_all_metrics()

        self.assertEqual(context.exception.message, errors.get_message("dps_metric_api", "SQLALCHEMY_ERROR",
                                                                       filler=self.error))
        self.assertEqual(errors.get_code("dps_metric_api", "SQLALCHEMY_ERROR"), context.exception.code)

    def test_retrieve_metrics_by_id_ok(self, mock_extract, *_):
        mock_extract.return_value = [{'foo': 'bar'}]
        result = service.retrieve_metrics_by_id('123-123-123')
        self.assertEqual(result, {'activity_metrics': [{'foo': 'bar'}], 'user_metrics': [{'foo': 'bar'}]})

    def test_retrieve_metrics_by_id_no_row(self, mock_extract, *_):
        mock_extract.return_value = []
        with self.assertRaises(ApplicationError) as context:
            service.retrieve_metrics_by_id('123-123-123')

        expected_err = ('dps_metric_api', 'CASE_NOT_FOUND')
        expected_err_message = errors.get_message(*expected_err, filler='123-123-123')
        expected_err_code = errors.get_code(*expected_err)

        self.assertEqual(context.exception.message, expected_err_message)
        self.assertEqual(context.exception.code, expected_err_code)

    @patch('dps_metric_api.services.dps_metric_service._extract_status')
    def test_insert_metric_ok(self, mock_status, mock_extract, *_):
        mock_extract.return_value = [{'foo': 'bar'}]
        mock_status.return_value = ['Pending']
        result = service.insert_metric({'user': {'ckan_user_id': '123-123-123', 'status': 'Pending'},
                                        'activity': {'foo': 'bar'}})
        self.assertEqual(result, '123-123-123')

    @patch('dps_metric_api.services.dps_metric_service._extract_status')
    def test_insert_metric_ok_status_changed(self, mock_status, mock_extract, *_):
        mock_extract.return_value = [{'foo': 'bar'}]
        mock_status.return_value = ['Pending', 'Approved']
        result = service.insert_metric({'user': {'ckan_user_id': '123-123-123', 'status': 'Closed'},
                                        'activity': {'foo': 'bar'}})
        self.assertEqual(result, '123-123-123')


class TestServicePrivateFunctions(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_extract_rows_no_rows(self):
        result = service._extract_rows([])
        self.assertEqual(result, [])

    def test_extract_rows(self):
        mock_row = MagicMock()
        mock_row.as_dict.return_value = {'foo': 'bar'}
        result = service._extract_rows([mock_row, mock_row])
        self.assertEqual(result, [{'foo': 'bar'}, {'foo': 'bar'}])

    def test_extract_status_no_rows(self):
        result = service._extract_status([])
        self.assertEqual(result, [])

    def test_extract_status(self):
        rows = [
            {'ckan_user_id': '123-123', 'status': 'Pending'},
            {'ckan_user_id': '123-123', 'status': 'Approved'}
        ]

        result = service._extract_status(rows)
        self.assertEqual(result, ['Pending', 'Approved'])
