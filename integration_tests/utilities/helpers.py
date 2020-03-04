from dps_metric_api.models import User, Activity
from dps_metric_api.extensions import db
from dps_metric_api.main import app


def teardown_metric_test_entry():
    with app.app_context():
        ckan_user_id = '123-456-123-abc'

        user = User.query.filter_by(ckan_user_id=ckan_user_id)
        activity = Activity.query.filter_by(ckan_user_id=ckan_user_id)

        if user and activity:
            user.delete()
            activity.delete()
            db.session.commit()
            db.session.close()
