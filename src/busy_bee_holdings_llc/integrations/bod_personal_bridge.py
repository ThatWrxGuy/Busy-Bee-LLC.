# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

from pathlib import Path

def bod_personal_import_available() -> bool:
    return (Path('vendor/source_bod_personal_snapshot') / 'psip.py').exists()
