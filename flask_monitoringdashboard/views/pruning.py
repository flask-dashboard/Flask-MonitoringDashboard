from datetime import datetime, timedelta

from flask import request
from flask.json import jsonify

from flask_monitoringdashboard import blueprint, scheduler
from flask_monitoringdashboard.core.auth import secure
from flask_monitoringdashboard.core.custom_graph import get_custom_graphs
from flask_monitoringdashboard.core.telemetry import post_to_back_if_telemetry_enabled
from flask_monitoringdashboard.database import session_scope
from flask_monitoringdashboard.database.pruning import prune_database_older_than_weeks


@blueprint.route('/database_pruning/prune_on_demand', methods=['POST'])
def prune_database_on_demand():
    """
    Endpoint for pruning the database of Request and optionally CustomGraph data older than the specified number of weeks
    """
    data = request.json
    weeks = data.get('age_threshold_weeks')
    delete_custom_graphs = data.get('delete_custom_graphs')

    # Validation
    if not isinstance(weeks, int) or weeks < 0:
        return jsonify({'error': 'age_threshold_weeks must be a natural number'}), 400
    if not isinstance(delete_custom_graphs, bool):
        return jsonify({'error': 'delete_custom_graphs must be a boolean'}), 400

    # Prune database
    prune_database_older_than_weeks(weeks, delete_custom_graphs)

    # Post info to telemetry if enabled
    post_data = {'age_threshold_weeks': weeks, 'delete_custom_graphs': delete_custom_graphs}
    post_to_back_if_telemetry_enabled('DatabasePruning', **post_data)

    return jsonify({'message': 'Database pruning complete'}), 200


@blueprint.route('/database_pruning/submit_database_prune_schedule', methods=['POST'])
def submit_database_prune_schedule():
    """
    Endpoint for scheduling a database prune task
    request params:
    day_of_the_month: int -- which day of the month to run the task
    months_between_runs: int -- how many months between each run
    age_threshold_weeks: int -- how many weeks old data should be pruned
    delete_custom_graphs: bool -- whether to delete custom graphs or not
    hour: int -- which hour of the day to run the task
    """
    data = request.json

    day_of_the_month = data.get('day_of_the_month')
    months_between_runs = data.get('months_between_runs')
    age_threshold_weeks = data.get('age_threshold_weeks')
    delete_custom_graphs = data.get('delete_custom_graphs')
    hour = data.get('hour')

    # Validation
    if not isinstance(day_of_the_month, int) or not isinstance(months_between_runs, int):
        return jsonify({'error': 'day_of_the_month and months must be integers'}), 400
    if not 1 <= day_of_the_month <= 31:
        return jsonify({'error': 'day_of_the_month must be between 1 and 31'}), 400
    if months_between_runs not in [1, 2, 3, 4, 6, 12]:  # Months should divide a year evenly for regular intervals
        return jsonify({'error': 'months must be 1, 2, 3, 4, 6, or 12'}), 400
    if not isinstance(age_threshold_weeks, int):
        return jsonify({'error': 'age_threshold must be an integer'}), 400
    if not isinstance(delete_custom_graphs, bool):
        return jsonify({'error': 'delete_custom_graphs must be a boolean'}), 400
    if not 0 <= hour <= 23:
        return jsonify({'error': 'hour must be between 0 and 23'}), 400

    # Define the scheduled task
    job_id = 'database_pruning_schedule'
    scheduler.add_job(
        id=job_id,
        func=prune_database_older_than_weeks,
        args=[age_threshold_weeks, delete_custom_graphs],  # These are arguments passed to the prune function
        trigger='cron',
        day=day_of_the_month,
        month=f'*/{months_between_runs}',
        hour=hour,
        minute=0,
        replace_existing=True  # This will replace an existing job
    )

    # Post info to telemetry if enabled
    post_data = {'age_threshold_weeks': age_threshold_weeks, 'delete_custom_graphs': delete_custom_graphs}
    post_to_back_if_telemetry_enabled('DatabasePruning', **post_data)

    return jsonify({'message': f'Scheduled task {job_id} created'}), 200
