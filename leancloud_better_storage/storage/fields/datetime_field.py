from datetime import datetime

from .defaults import undefined
from .field import Field


class DateTimeField(Field):

    def __init__(self, name=None, nullable=True, default=undefined, auto_now=False, auto_now_add=False,
                 now_fn=datetime.now):
        super().__init__(name, nullable, default)
        self._auto_now = auto_now
        self._auto_now_add = auto_now_add
        self._now_fn = now_fn

    def _after_model_created(self, model, name):
        super()._after_model_created(model, name)

        def hook_fn(i):
            return i.lc_object.set(self.field_name, self._now_fn())

        if self._auto_now_add:
            model.register_pre_create_hook(hook_fn)
        if self._auto_now:
            model.register_pre_update_hook(hook_fn)
