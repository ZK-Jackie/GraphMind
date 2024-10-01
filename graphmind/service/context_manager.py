from contextvars import ContextVar


class ContextManager:
    _persistent_context = ContextVar("persistent_context", default={})
    _transient_context = ContextVar("transient_context", default={})

    @classmethod
    def set_persistent_context(cls, key, value):
        context = cls._persistent_context.get()
        context[key] = value
        cls._persistent_context.set(context)

    @classmethod
    def get_persistent_context(cls, key, default=None):
        context = cls._persistent_context.get()
        return context.get(key, default)

    @classmethod
    def set_transient_context(cls, key, value):
        context = cls._transient_context.get()
        context[key] = value
        cls._transient_context.set(context)

    @classmethod
    def get_transient_context(cls, key, default=None):
        context = cls._transient_context.get()
        return context.get(key, default)

    @classmethod
    def clear_transient_context(cls):
        cls._transient_context.set({})
