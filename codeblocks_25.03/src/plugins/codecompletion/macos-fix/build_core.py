#!/usr/bin/env python3
"""Build the companion SDK with the safe encoding reader, using bundled wx libraries."""
import argparse
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re
import subprocess

def sources(directory, variable):
    text = (directory / 'Makefile.am').read_text().split(variable + ' =', 1)[1]
    text = text.split('\n\n', 1)[0]
    return [directory / p for p in re.findall(r'[\w/-]+\.(?:cpp|cxx)', text)]

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--wx-source', type=Path, required=True)
    parser.add_argument('--wx-build', type=Path, required=True)
    parser.add_argument('--app', type=Path, default=Path('/Applications/CodeBlocks.app'))
    args = parser.parse_args()
    out = Path(__file__).resolve().parent / 'core'
    root = out.parents[3]
    sdk = root / 'sdk'
    generated = out / 'generated'
    generated.mkdir(exist_ok=True)
    revision = (root / 'include/autorevision.h.in').read_text().replace('@REVISION@', '13628').replace('@DATE@', '2025-03-25')
    (generated / 'autorevision.h').write_text(revision)
    objects = out / 'objects'
    objects.mkdir(exist_ok=True)
    setup = next((args.wx_build / 'lib/wx/include').glob('*osx_cocoa-unicode-3.2'))
    flags = ['clang++', '-arch', 'x86_64', '-mmacosx-version-min=11.0', '-std=c++11', '-O2', '-g', '-fPIC',
             '-DNOPCH', '-DTIXML_USE_STL=YES', '-DwxDEBUG_LEVEL=0', '-DWXUSINGDLL', '-D__WXMAC__',
             '-D__WXOSX__', '-D__WXOSX_COCOA__', '-D_FILE_OFFSET_BITS=64', '-DSCI_LEXER', '-DLINK_LEXERS', '-D__WX__', '-Wno-varargs']
    includes = [generated, setup, args.wx_source / 'include', root / 'include', root / 'include/tinyxml',
                root / 'include/scripting/include', sdk / 'wxscintilla/include', sdk / 'wxscintilla/src']
    includes += [sdk / 'wxscintilla/src/scintilla' / p for p in ['include', 'lexlib', 'src']]
    includes += [sdk / 'mozilla_chardet/include' / p for p in ['', 'mfbt', 'nsprpub/pr/include', 'xpcom', 'xpcom/base', 'xpcom/glue']]
    flags += ['-I' + str(p) for p in includes]
    cache = out / 'compiler-flags.json'
    latest_header = max(p.stat().st_mtime for directory in [root / 'include', sdk / 'wxscintilla']
                        for p in directory.rglob('*.h'))
    signature = {'flags': flags, 'latest_header': latest_header}
    if not cache.exists() or json.loads(cache.read_text()) != signature:
        for obj in objects.glob('*.o'):
            obj.unlink()
    cache.write_text(json.dumps(signature))
    files = sources(sdk, 'libcodeblocks_la_SOURCES')
    for directory, variable in [('wxscintilla', 'libwxscintilla_la_SOURCES'),
                                ('scripting/bindings', 'libsqbindings_la_SOURCES'),
                                ('scripting/squirrel', 'libsquirrel_la_SOURCES'),
                                ('scripting/sqstdlib', 'libsqstdlib_la_SOURCES')]:
        files += sources(sdk / directory, variable)
    files += sources(root / 'base/tinyxml', 'libtinyxml_la_SOURCES')
    def compile_file(path):
        obj = objects / (str(path.relative_to(root)).replace('/', '_') + '.o')
        actual = out / 'encodingdetector.cpp' if path == sdk / 'encodingdetector.cpp' else path
        if not obj.exists() or obj.stat().st_mtime < actual.stat().st_mtime:
            subprocess.run(flags + ['-c', str(actual), '-o', str(obj)], check=True)
        print('Compiled ' + str(path.relative_to(root)), flush=True)
        return obj
    with ThreadPoolExecutor(max_workers=4) as pool:
        compiled = list(pool.map(compile_file, files))
    libs = args.app / 'Contents/MacOS'
    wx = list(libs.glob('libwx_*-3.2.0.3.0.dylib'))
    result = out / 'libcodeblocks.0.dylib'
    subprocess.run(['clang++', '-arch', 'x86_64', '-dynamiclib', '-Wl,-undefined,error',
                    '-Wl,-install_name,@executable_path/libcodeblocks.0.dylib',
                    '-framework', 'CoreFoundation', '-framework', 'Cocoa', '-o', str(result)] +
                   [str(p) for p in compiled + wx], check=True)
    subprocess.run(['codesign', '--force', '--sign', '-', str(result)], check=True)
    print('Built ' + str(result))

if __name__ == '__main__':
    main()
