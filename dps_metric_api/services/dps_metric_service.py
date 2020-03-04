import logging
from sqlalchemy.exc import SQLAlchemyError
from common_utilities import errors

from dps_metric_api.models import User, Activity
from dps_metric_api.exceptions import ApplicationError
from dps_metric_api.extensions import db

log = logging.getLogger(__name__)


def handle_errors(is_get):
    def wrapper(func):
        def run_and_handle(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except SQLAlchemyError as error:
                log.error(str(error))
                error_code = 500 if is_get else 422
                error_def = errors.get('dps_metric_api', 'SQLALCHEMY_ERROR', filler=str(error))
                raise ApplicationError(*error_def, http_code=error_code)
            except ApplicationError as error:
                raise error
            finally:
                if not is_get:
                    db.session.rollback()
                db.session.close()
        return run_and_handle
    return wrapper


@handle_errors(is_get=True)
def retrieve_all_metrics():
    log.info('retrieve all metrics')
    rows = {
        'user_metrics': _extract_rows(User.select_all()),
        'activity_metrics': _extract_rows(Activity.select_all())
    }
    return rows


@handle_errors(is_get=True)
def retrieve_metrics_by_id(ckan_id):
    log.info('retrieve metrics for ckan_id: {}'.format(ckan_id))
    result = {
        'user_metrics': _extract_rows(User.select_metric_by_ckan_id(ckan_id)),
        'activity_metrics': _extract_rows(Activity.select_metric_by_ckan_id(ckan_id))
    }
    if result['user_metrics'] or result['activity_metrics']:
        return result
    else:
        log.error("User '{}' not found".format(ckan_id))
        raise ApplicationError(*errors.get('dps_metric_api', 'CASE_NOT_FOUND', filler=ckan_id), http_code=404)


@handle_errors(is_get=False)
def insert_metric(user_details):
    log.info('insert metric')
    user_data = user_details['user']
    activity_data = user_details['activity']

    # check if user present
    user = _extract_rows(User.select_metric_by_ckan_id(user_data['ckan_user_id']))
    user_status = _extract_status(user)

    if not user or user_data['status'] not in user_status:
        log.info('user - {}, not present or status change so adding new row'.format(user_data['ckan_user_id']))
        user = User(user_data)
        db.session.add(user)

    if 'ckan_user_id' not in activity_data:
        activity_data['ckan_user_id'] = user_data['ckan_user_id']

    activity = Activity(activity_data)
    db.session.add(activity)
    db.session.commit()
    return user_data['ckan_user_id']


def _extract_rows(rows):
    return [row.as_dict() for row in rows]


def _extract_status(rows):
    return [row['status'] for row in rows]
