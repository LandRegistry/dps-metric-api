import datetime
from dps_metric_api.extensions import db
from sqlalchemy import asc


class User(db.Model):
    __tablename__ = 'dps_user'
    user_id = db.Column(db.Integer, primary_key=True)
    ckan_user_id = db.Column(db.String, nullable=False)
    user_type = db.Column(db.String, nullable=False)
    status = db.Column(db.String, nullable=False)
    date_added = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)

    def __init__(self, user_data):
        self.ckan_user_id = user_data['ckan_user_id']
        self.user_type = user_data['user_type']
        self.status = user_data['status']

    @staticmethod
    def select_all():
        return User.query.order_by(asc(User.date_added)).all()

    @staticmethod
    def select_metric_by_ckan_id(ckan_user_id):
        return User.query.filter_by(ckan_user_id=ckan_user_id).all()

    def as_dict(self):
        return {
            'user_id': self.user_id,
            'ckan_user_id': self.ckan_user_id,
            'user_type': self.user_type,
            'status': self.status,
            'date_added': str(self.date_added)
        }


class Activity(db.Model):
    __tablename__ = 'dps_activity'
    activity_id = db.Column(db.Integer, primary_key=True)
    activity_type = db.Column(db.String, nullable=False)
    dataset = db.Column(db.String, nullable=True)
    filename = db.Column(db.String, nullable=True)
    ckan_user_id = db.Column(db.String, nullable=False)
    date_added = db.Column(db.DateTime(timezone=True), default=datetime.datetime.utcnow)

    def __init__(self, activity_data):
        self.activity_type = activity_data['activity_type']
        self.dataset = activity_data['dataset']
        self.filename = activity_data['filename']
        self.ckan_user_id = activity_data['ckan_user_id']

    @staticmethod
    def select_all():
        return Activity.query.order_by(asc(Activity.date_added)).all()

    @staticmethod
    def select_metric_by_ckan_id(ckan_user_id):
        return Activity.query.filter_by(ckan_user_id=ckan_user_id).order_by(asc(Activity.date_added)).all()

    def as_dict(self):
        return {
            'activity_id': self.activity_id,
            'activity_type': self.activity_type,
            'dataset': self.dataset,
            'filename': self.filename,
            'ckan_user_id': self.ckan_user_id,
            'date_added': str(self.date_added)
        }
