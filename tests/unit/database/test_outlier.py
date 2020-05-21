"""
This file contains all unit tests for the monitor-rules-table in the database. (Corresponding
to the file: 'flask_monitoringdashboard/database/outlier.py')
"""

import pytest

from flask_monitoringdashboard.database import Outlier
from flask_monitoringdashboard.database.count import count_outliers
from flask_monitoringdashboard.database.outlier import add_outlier, get_outliers_sorted, get_outliers_cpus


def test_add_outlier(session, request_1):
    assert not request_1.outlier

    add_outlier(
        session,
        request_id=request_1.id,
        cpu_percent="cpu_percent",
        memory="memory",
        stacktrace="stacktrace",
        request=("headers", "environ", "url"),
    )
    session.commit()
    assert session.query(Outlier).filter(Outlier.request_id == request_1.id).one()


def test_get_outliers(session, outlier_1, endpoint):
    outliers = get_outliers_sorted(session, endpoint_id=endpoint.id, offset=0, per_page=10)
    assert len(outliers) == 1
    assert outliers[0].id == outlier_1.id


@pytest.mark.usefixtures('outlier_1', 'outlier_2')
def test_count_outliers(session, endpoint):
    assert count_outliers(session, endpoint.id) == 2


@pytest.mark.usefixtures('outlier_1', 'outlier_2')
@pytest.mark.parametrize('outlier_1__cpu_percent', ['[0, 1, 2, 3]'])
@pytest.mark.parametrize('outlier_2__cpu_percent', ['[1, 2, 3, 4]'])
def test_get_outliers_cpus(session, endpoint):
    expected_cpus = ['[{0}, {1}, {2}, {3}]'.format(i, i + 1, i + 2, i + 3) for i in range(2)]
    assert get_outliers_cpus(session, endpoint.id) == expected_cpus
