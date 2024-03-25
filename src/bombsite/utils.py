"""utils.py provides universal functionality to the entire codebase of the game.

Copyright © 2024 - Elliot Simpson
"""

from pathlib import Path

__all__: list[str] = ["package_path"]

package_path: Path = Path(__file__).parent
