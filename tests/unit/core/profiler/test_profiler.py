import threading
import time

from flask import request
import pytest
from werkzeug.routing import Rule

from flask_monitoringdashboard.core.cache import memory_cache, init_cache
from flask_monitoringdashboard.core.profiler import (
    start_thread_last_requested,
    start_performance_thread,
    start_profiler_and_outlier_thread,
    start_outlier_thread,
)


def wait_until_threads_finished(num_threads):
    while threading.active_count() > num_threads:
        time.sleep(0.01)


@pytest.mark.usefixtures('request_context')
def test_start_thread_last_requested(endpoint, config):
    config.app.url_map.add(Rule('/', endpoint=endpoint.name))
    init_cache()
    num_threads = threading.active_count()
    start_thread_last_requested(endpoint)
    wait_until_threads_finished(num_threads)

    assert memory_cache.get(endpoint.name).last_requested


@pytest.mark.usefixtures('request_context')
def test_start_performance_thread(endpoint, config):
    config.app.url_map.add(Rule('/', endpoint=endpoint.name))
    init_cache()
    request.environ['REMOTE_ADDR'] = '127.0.0.1'
    num_threads = threading.active_count()
    start_performance_thread(endpoint, 1234, 200)
    assert threading.active_count() == num_threads + 1
    wait_until_threads_finished(num_threads)

    assert memory_cache.get(endpoint.name).average_duration > 0


@pytest.mark.usefixtures('request_context')
def test_start_outlier_thread(endpoint, config):
    config.app.url_map.add(Rule('/', endpoint=endpoint.name))
    init_cache()
    request.environ['REMOTE_ADDR'] = '127.0.0.1'
    num_threads = threading.active_count()
    outlier = start_outlier_thread(endpoint)
    assert threading.active_count() == num_threads + 1
    outlier.stop(duration=1, status_code=200)
    wait_until_threads_finished(num_threads)


@pytest.mark.usefixtures('request_context')
def test_start_profiler_and_outlier_thread(endpoint, config):
    config.app.url_map.add(Rule('/', endpoint=endpoint.name))
    init_cache()
    request.environ['REMOTE_ADDR'] = '127.0.0.1'
    num_threads = threading.active_count()
    thread = start_profiler_and_outlier_thread(endpoint)
    assert threading.active_count() == num_threads + 2
    thread.stop(duration=1, status_code=200)
    wait_until_threads_finished(num_threads)
