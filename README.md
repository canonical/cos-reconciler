# `cos-reconciler`

Package containing utilities for implementing reconciler charms.

# Imperative API

This package exposes a few utility functions whose task is to map a predefined set of observers to
a single event handler.

- `observe_setup_events`: observe `upgrade-charm`, `install` and `start`
- `observe_teardown_events`: observe `stop` and `remove`
- `observe_maintenance_events`: observe all hook events (`ops.HookEvent` subclasses), which includes most events except:
  - action events 
  - framework events
  - "lifecycle events" (`collect-*-status`)
- `observe_all`: observe all by default, else all subclasses of a configurable list of event classes

Usage:

```python
import ops
from cos_reconciler import observe_maintenance_events

class MyCharm(ops.CharmBase):
    """Charm the service."""
    def __init__(self, framework: ops.Framework):
        super().__init__(framework=framework)
        observe_maintenance_events(self, self._on_maintenance_evt)
        
    def _on_maintenance_evt(self, _:ops.EventBase):
        self.reconcile()
        
    def reconcile(self):
        pass
```

`observe_all` usage:

```python
import ops
from cos_reconciler import observe_all

class MyCharm(ops.CharmBase):
    """Charm the service."""
    def __init__(self, framework: ops.Framework):
        super().__init__(framework=framework)
        
        observe_all(self, self._on_any_relation_evt, event_types=ops.RelationEvent)
        observe_all(self, self._on_any_non_relation_evt, event_types=ops.RelationEvent, revert=True)
        
    def _on_any_non_relation_evt(self, _:ops.EventBase):
        pass
        
    def _on_any_relation_evt(self, _:ops.RelationEvent):
        pass
```

# Inheritance API

We offer a `K8sCharm` class that by default observes all maintenance events. 

Usage:
```python
import ops
from cos_reconciler import K8sCharm

class MyCharm(K8sCharm):
    """Charm the service."""
    def __init__(self, framework: ops.Framework):
        super().__init__(framework=framework)
        
    def reconcile(self):
        pass
```

We offer a `MachineCharm` that has three separate handlers for setup, teardown and maintenance events (note that maintenance events includes setup and teardown!).

Usage:
```python
import ops
from cos_reconciler import MachineCharm

class MyCharm(MachineCharm):
    """Charm the service."""
    def __init__(self, framework: ops.Framework):
        super().__init__(framework=framework)
        
    def reconcile(self):
        # e.g. configure snap
        pass
    
    def setup(self) -> None:
        # e.g. install snap
        pass

    def teardown(self) -> None:
        # e.g. remove snap
        pass
```

# DEVELOPERS

To release:
```bash
# obtain the current latest version out there
git tag | tail -n 1

new_tag="v0.5"  # for example!
git tag $new_tag -m "new fancy feature"
git push origin head --tag
```

Once the PR is merged, the release CI will kick in and put the tag in `cos_reconciler.version.py`