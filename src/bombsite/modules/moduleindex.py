"""moduleenum.py links module references to their modules.

Copyright © 2024 - Elliot Simpson
"""

from bombsite.modules.gameplay import GamePlay
from bombsite.modules.mainmenumodule import MainMenuModule
from bombsite.modules.module import Module
from bombsite.modules.moduleenum import ModuleEnum

get_module_type: dict[ModuleEnum, type[Module]] = {
    ModuleEnum.GAMEPLAY: GamePlay,
    ModuleEnum.MAIN_MENU: MainMenuModule,
}
