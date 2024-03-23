from pathlib import Path

__all__: list[str] = ["package_path"]

package_path: Path = Path(__file__).parent
