# ruff: noqa: I001 — import order is intentional: lsp.handlers must precede command_core to trigger sys.path setup in lsp/__init__.py
import pathlib as pl
import sys

### bundled libraries
bundled_path = pl.Path(__file__).parent.parent.absolute() / "bundled" / "libs"
## preprend the path to include bundled libraries
#### Becareful, we prepend the path to ensure that bundled libraries are found first in place of system libraries
sys.path.insert(0, str(bundled_path))


from pygls.server import LanguageServer  # noqa: E402
from lsp.handlers import register_handlers  # noqa: E402

from command_core import CommandCore  # noqa: E402

ls = LanguageServer(name="aster-lsp", version="0.1.0")


def main():
    CommandCore().store_ls(ls)
    register_handlers(ls)
    ls.start_io()


if __name__ == "__main__":
    main()
