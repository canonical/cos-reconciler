import ops

from cos_reconciler.main import DEFAULT_SETUP_EVENTS, DEFAULT_TEARDOWN_EVENTS


def get_observed_events(observe_mock):
    return {call.args[0].event_type for call in observe_mock.call_args_list}


def assert_maintenance_events_observed(observe_mock):
    observed = get_observed_events(observe_mock)
    assert ops.StartEvent in observed
    assert ops.ConfigChangedEvent in observed
    assert ops.RelationBrokenEvent in observed
    assert ops.RelationChangedEvent in observed
    assert ops.PebbleReadyEvent in observed
    assert ops.PebbleCheckRecoveredEvent in observed
    assert ops.PebbleCustomNoticeEvent in observed


def assert_setup_events_observed(observe_mock):
    assert set(DEFAULT_SETUP_EVENTS).issubset(get_observed_events(observe_mock))


def assert_teardown_events_observed(observe_mock):
    assert set(DEFAULT_TEARDOWN_EVENTS).issubset(get_observed_events(observe_mock))


def assert_maintenance_events_not_observed(observe_mock):
    assert not get_observed_events(observe_mock).intersection(
        {ops.ActionEvent, ops.CollectStatusEvent}
    )


def assert_setup_events_not_observed(observe_mock):
    assert not get_observed_events(observe_mock).intersection(set(DEFAULT_SETUP_EVENTS))


def assert_teardown_events_not_observed(observe_mock):
    assert not get_observed_events(observe_mock).intersection(
        set(DEFAULT_TEARDOWN_EVENTS)
    )


def assert_action_events_not_observed(observe_mock):
    assert ops.ActionEvent not in get_observed_events(observe_mock)


def assert_collect_status_events_not_observed(observe_mock):
    assert ops.CollectStatusEvent not in get_observed_events(observe_mock)


def assert_framework_events_not_observed(observe_mock):
    assert ops.framework.CommitEvent not in get_observed_events(observe_mock)
    assert ops.framework.PreCommitEvent not in get_observed_events(observe_mock)
