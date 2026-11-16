"""Copy the shared scoring UI into the iOS bundle. No firmware/code generation."""
from pathlib import Path
import json
import shutil

ROOT=Path(__file__).resolve().parents[1]

def prepare():
    destination=ROOT/'ios/freETargetIOS/Web'
    destination.mkdir(exist_ok=True)
    for source in [ROOT/'app/assets/index.html',ROOT/'ios/ios_bootstrap.js',ROOT/'ios/mobile.css']:
        shutil.copy2(source,destination/source.name)
    shutil.copytree(ROOT/'licenses',destination/'licenses',dirs_exist_ok=True)
    (destination/'PROVENANCE.json').write_text(json.dumps({'ui_base':'1.7.9','desktop_source':'0.3.10-beta.1','preview':'0.2.0-beta.1','target_build':'freETarget Minimalist'},indent=2)+'\n')
    print('iOS Web assets prepared:',destination)

if __name__=='__main__':prepare()
