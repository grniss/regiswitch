from regiswitch.core.backends import get_backend
from regiswitch.models.config import Registry


def init_registry() -> Registry:
    return get_backend().init()


def load_registry() -> Registry:
    return get_backend().load_registry()


def save_registry(registry: Registry) -> None:
    get_backend().save_registry(registry)


def is_initialized() -> bool:
    return get_backend().is_initialized()
