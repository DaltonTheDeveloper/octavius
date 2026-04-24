from .shell import register as register_shell
from .filesystem import register as register_fs
from .ue5 import register as register_ue5
from .chrome import register as register_chrome
from .app import register as register_app
from .discover import register as register_discover
from .volume import register as register_volume
from .epic import register as register_epic
from .legendary import register as register_legendary
from .ui import register as register_ui


def register_all(bus) -> None:
    register_shell(bus)
    register_fs(bus)
    register_ue5(bus)
    register_chrome(bus)
    register_app(bus)
    register_discover(bus)
    register_volume(bus)
    register_epic(bus)
    register_legendary(bus)
    register_ui(bus)
