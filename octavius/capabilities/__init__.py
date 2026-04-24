from .shell import register as register_shell
from .filesystem import register as register_fs
from .ue5 import register as register_ue5
from .chrome import register as register_chrome


def register_all(bus) -> None:
    register_shell(bus)
    register_fs(bus)
    register_ue5(bus)
    register_chrome(bus)
