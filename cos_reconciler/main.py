"""Reconciler charm utilities for ops charms."""

import abc
from typing import Union, Tuple, Callable, Any, Final, Type, TypeVar

import ops

_eventTyp = TypeVar("_eventTyp", bound=ops.EventBase)
_IssubclassEventFilter = Union[Type[_eventTyp], Tuple[Type[_eventTyp]]]
DEFAULT_MAINTENANCE_EVENTS: Final[_IssubclassEventFilter] = ops.HookEvent
DEFAULT_SETUP_EVENTS: Final[_IssubclassEventFilter] = (
    ops.UpgradeCharmEvent,
    ops.InstallEvent,
    ops.StartEvent,
)
DEFAULT_TEARDOWN_EVENTS: Final[_IssubclassEventFilter] = (
    ops.StopEvent,
    ops.RemoveEvent,
)


def observe_all(
    charm: ops.CharmBase,
    callback: Callable[[Any], None],
    event_types: _IssubclassEventFilter = ops.EventBase,
    revert: bool = False,
):
    """Observe all events that are a subclass of the given event type filter(s).

    If called without `event_types`, will observe all events.
    Use `revert` to flip the polarity of the check
    """

    def predicate(bound_event: ops.BoundEvent):
        if revert:
            return not issubclass(bound_event.event_type, event_types)
        return issubclass(bound_event.event_type, event_types)

    for bound_evt in charm.on.events().values():
        if predicate(bound_evt):
            charm.framework.observe(bound_evt, callback)


def observe_maintenance_events(
    charm: ops.CharmBase,
    callback: Callable[[Any], None],
):
    """Observe all maintenance events on a charm."""
    observe_all(charm, callback, DEFAULT_MAINTENANCE_EVENTS)


def observe_setup_events(
    charm: ops.CharmBase,
    callback: Callable[[Any], None],
):
    """Observe all setup events on a charm."""
    observe_all(charm, callback, DEFAULT_SETUP_EVENTS)


def observe_teardown_events(
    charm: ops.CharmBase,
    callback: Callable[[Any], None],
):
    """Observe all teardown events on a charm."""
    observe_all(charm, callback, DEFAULT_TEARDOWN_EVENTS)


class ReconcilerCharm(ops.CharmBase, metaclass=abc.ABCMeta):
    """Generic reconciler Charm ABC."""

    def __init__(self, framework: ops.Framework):
        super().__init__(framework=framework)
        self._register_observers()

    @abc.abstractmethod
    def _register_observers(self) -> None: ...

    # OBSERVERS
    def _on_maintenance_evt(self, _: ops.EventBase):
        self.reconcile()

    # RECONCILERS
    @abc.abstractmethod
    def reconcile(self) -> None: ...


class K8sCharm(ReconcilerCharm):
    """K8s Charm reconciler ABC."""

    def _register_observers(self):
        observe_maintenance_events(self, self._on_maintenance_evt)


class MachineCharm(ReconcilerCharm):
    """Machine Charm reconciler ABC."""

    def _register_observers(self):
        # we split events in three categories:
        # events on which we need to set up things
        observe_setup_events(self, self._on_setup_evt)

        # events on which we need to remove things
        observe_teardown_events(self, self._on_teardown_evt)

        # events on which we may need to configure things
        observe_maintenance_events(self, self._on_maintenance_evt)

    # event handlers
    def _on_setup_evt(self, _: ops.EventBase):
        self.setup()

    def _on_teardown_evt(self, _: ops.EventBase):
        self.teardown()

    def _on_maintenance_evt(self, _: ops.EventBase):
        self.reconcile()

    # lifecycle managers
    @abc.abstractmethod
    def setup(self) -> None: ...

    @abc.abstractmethod
    def teardown(self) -> None: ...
