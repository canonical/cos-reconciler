from unittest.mock import MagicMock, patch

import pytest
from ops.testing import Context, State

from cos_reconciler import K8sCharm, MachineCharm
from tests.assertions import (
    assert_maintenance_events_observed,
    assert_setup_events_observed,
    assert_teardown_events_observed,
    assert_collect_status_events_not_observed,
    assert_framework_events_not_observed,
)


@pytest.fixture
def observe_mock():
    with patch("ops.framework.Framework.observe", MagicMock()) as mm:
        yield mm


def test_k8s_charm(observe_mock):
    class MyCharmType(K8sCharm):
        def reconcile(self) -> None:
            pass

    ctx = Context(
        MyCharmType,
        meta={
            "name": "luca",
            "requires": {"bax": {"interface": "bar"}},
            "containers": {"foo": {}},
        },
        actions={"foo": {}},
    )
    ctx.run(ctx.on.update_status(), state=State())
    assert_maintenance_events_observed(observe_mock)
    assert_setup_events_observed(observe_mock)
    assert_teardown_events_observed(observe_mock)
    assert_collect_status_events_not_observed(observe_mock)
    assert_framework_events_not_observed(observe_mock)


def test_machine_charm(observe_mock):
    class MyCharmType(MachineCharm):
        def reconcile(self) -> None:
            pass

        def setup(self) -> None:
            pass

        def teardown(self) -> None:
            pass

    ctx = Context(
        MyCharmType,
        meta={
            "name": "luca",
            "requires": {"bax": {"interface": "bar"}},
            "containers": {"foo": {}},
        },
        actions={"foo": {}},
    )
    ctx.run(ctx.on.update_status(), state=State())
    assert_maintenance_events_observed(observe_mock)
    assert_setup_events_observed(observe_mock)
    assert_teardown_events_observed(observe_mock)
    assert_collect_status_events_not_observed(observe_mock)
    assert_framework_events_not_observed(observe_mock)
