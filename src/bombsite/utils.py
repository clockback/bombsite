"""utils.py provides universal functionality to the entire codebase of the game.

Copyright © 2024 - Elliot Simpson
"""

from pathlib import Path

__all__: list[str] = ["package_path"]

package_path: Path = Path(__file__).parent
fonts_path: Path = package_path / "fonts"
images_path: Path = package_path / "images"


def return_system_exit() -> SystemExit:
    """Exits the game.

    Returns:
        A SystemExit with a return code of zero.
    """
    return SystemExit(0)
