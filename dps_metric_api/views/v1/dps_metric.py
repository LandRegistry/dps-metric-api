from flask import request, Blueprint, jsonify
from flask_negotiate import consumes, produces

from dps_metric_api.app import app
from dps_metric_api.exceptions import ApplicationError
from dps_metric_api.services import dps_metric_service as service


dps_metric_bp = Blueprint('dps_metric_bp', __name__)


@dps_metric_bp.route('', methods=['GET'])
@produces('application/json')
def get_all_metrics():
    try:
        app.logger.info('Getting all dps metrics')
        result = service.retrieve_all_metrics()
        return jsonify(result)
    except ApplicationError as error:
        error_message = 'Failed to retrieve metrics - {}'.format(error.message)
        app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code


@dps_metric_bp.route('/<ckan_id>', methods=['GET'])
@produces('application/json')
def get_metric_by_user_id(ckan_id):
    try:
        app.logger.info('Getting metric for user id: {}'.format(ckan_id))
        result = service.retrieve_metrics_by_id(ckan_id)
        return jsonify(result)
    except ApplicationError as error:
        error_message = 'Failed to retrieve metrics for user: {} with error: {}'.format(ckan_id, error.message)
        app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code


@dps_metric_bp.route('', methods=['POST'])
@consumes('application/json')
@produces('application/json')
def create_metric():
    try:
        data = request.get_json(force=True)
        app.logger.info('Creating metric for ckan id: {}'.format(data['user']['ckan_user_id']))
        result = service.insert_metric(data)
        response = {
            'message': 'metric created successfully',
            'ckan_user_id': result
        }
        return jsonify(response), 201
    except ApplicationError as error:
        error_message = 'Failed to create a metric with error: {}'.format(error.message)
        app.logger.error(error_message)
        return jsonify(error=error_message), error.http_code
