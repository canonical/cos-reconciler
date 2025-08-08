import pytest
from unittest.mock import MagicMock, patch

import ops.framework
from ops.testing import Context, State
from cos_reconciler import (
    observe_all,
    observe_teardown_events,
    observe_maintenance_events,
    observe_setup_events,
)
from tests.assertions import (
    get_observed_events,
    assert_setup_events_observed,
    assert_maintenance_events_observed,
    assert_teardown_events_observed,
    assert_setup_events_not_observed,
    assert_maintenance_events_not_observed,
    assert_teardown_events_not_observed,
    assert_framework_events_not_observed,
    assert_collect_status_events_not_observed,
)


@pytest.fixture
def observe_mock():
    with patch("ops.framework.Framework.observe", MagicMock()) as mm:
        yield mm


@pytest.fixture
def charm(observe_mock):
    ctx = Context(
        ops.CharmBase,
        meta={
            "name": "luca",
            "requires": {"bax": {"interface": "bar"}},
            "containers": {"foo": {}},
        },
        actions={"foo": {}},
    )
    with ctx(ctx.on.update_status(), state=State()) as mgr:
        yield mgr.charm


def test_observe_all(charm, observe_mock):
    # GIVEN a regular luca charm
    # WHEN we observe_all with no custom filters
    observe_all(charm, lambda _: None)
    # then events from all categories are observed
    observed_events = get_observed_events(observe_mock)
    assert ops.RemoveEvent in observed_events
    assert ops.CollectStatusEvent in observed_events
    assert ops.InstallEvent in observed_events
    assert ops.UpdateStatusEvent in observed_events


def test_observe_lifecycle(charm, observe_mock):
    # GIVEN a regular luca charm
    # WHEN we observe_all lifecycle evts
    observe_all(charm, lambda _: None, event_types=(ops.LifecycleEvent,))
    # then only lifecycle events are observed
    observed_events = get_observed_events(observe_mock)
    assert ops.CollectStatusEvent in observed_events
    # FIXME: why are these not observed?
    # assert ops.framework.CommitEvent in observed_events
    # assert ops.framework.PreCommitEvent in observed_events

    assert ops.RemoveEvent not in observed_events
    assert ops.InstallEvent not in observed_events
    assert ops.UpdateStatusEvent not in observed_events


def test_observe_not_lifecycle(charm, observe_mock):
    # GIVEN a regular luca charm
    # WHEN we observe_all lifecycle evts with revert
    observe_all(charm, lambda _: None, event_types=(ops.LifecycleEvent,), revert=True)
    # then only non-lifecycle events are observed
    observed_events = get_observed_events(observe_mock)
    assert ops.CollectStatusEvent not in observed_events
    assert ops.framework.CommitEvent not in observed_events
    assert ops.framework.PreCommitEvent not in observed_events

    assert ops.RemoveEvent in observed_events
    assert ops.InstallEvent in observed_events
    assert ops.UpdateStatusEvent in observed_events


def test_observe_setup(charm, observe_mock):
    # GIVEN a regular luca charm
    # WHEN we observe_setup
    observe_setup_events(charm, lambda _: None)
    # THEN only setup events are observed
    assert_setup_events_observed(observe_mock)
    assert_teardown_events_not_observed(observe_mock)
    assert_maintenance_events_not_observed(observe_mock)
    assert_collect_status_events_not_observed(observe_mock)
    assert_framework_events_not_observed(observe_mock)


def test_observe_maintenance(charm, observe_mock):
    # GIVEN a regular luca charm
    # WHEN we observe_maintenance
    observe_maintenance_events(charm, lambda _: None)
    # THEN maintenance events are observed, which includes setup/teardown
    assert_maintenance_events_observed(observe_mock)
    assert_collect_status_events_not_observed(observe_mock)
    assert_framework_events_not_observed(observe_mock)


def test_observe_teardown(charm, observe_mock):
    # GIVEN a regular luca charm
    # WHEN we observe_teardown
    observe_teardown_events(charm, lambda _: None)
    # THEN only teardown events are observed
    assert_teardown_events_observed(observe_mock)
    assert_setup_events_not_observed(observe_mock)
    assert_maintenance_events_not_observed(observe_mock)
    assert_collect_status_events_not_observed(observe_mock)
    assert_framework_events_not_observed(observe_mock)
