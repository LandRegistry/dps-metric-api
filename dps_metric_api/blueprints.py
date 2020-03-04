# Import every blueprint file
from dps_metric_api.views import general
from dps_metric_api.views.v1 import dps_metric


def register_blueprints(app):
    """Adds all blueprint objects into the app."""
    app.register_blueprint(general.general)
    app.register_blueprint(dps_metric.dps_metric_bp, url_prefix='/v1/metric')

    # All done!
    app.logger.info("Blueprints registered")
