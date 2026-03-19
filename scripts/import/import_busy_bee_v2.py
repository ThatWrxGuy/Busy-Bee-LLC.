# Copyright (c) Busy Bee Holdings LLC
# All Rights Reserved

from pathlib import Path
import shutil

def main() -> None:
    src = Path('vendor/source_busy_bee_v2_snapshot/src/busy_bee')
    dst = Path('src/busy_bee')
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    print(f'Imported Busy Bee V2 into {dst}')

if __name__ == '__main__':
    main()
