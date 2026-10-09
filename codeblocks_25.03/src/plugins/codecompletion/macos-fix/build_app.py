#!/usr/bin/env python3
"""Build the macOS main executable, including the HenryYe splash label."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re
import subprocess

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('--wx-source', type=Path, required=True)
p.add_argument('--wx-build', type=Path, required=True)
p.add_argument('--app', type=Path, default=Path('/Applications/CodeBlocks.app'))
p.add_argument('--output', type=Path, required=True)
a = p.parse_args()
source = Path(__file__).resolve().parents[3]
out = a.output.resolve()
out.mkdir(parents=True, exist_ok=True)
setup = next((a.wx_build / 'lib/wx/include').glob('*osx_cocoa-unicode-3.2'))
flags = ['clang++','-arch','x86_64','-mmacosx-version-min=11.0','-std=c++11','-O2','-g','-DNOPCH','-DTIXML_USE_STL=YES','-DwxDEBUG_LEVEL=0','-DWXUSINGDLL','-D__WXMAC__','-D__WXOSX__','-D__WXOSX_COCOA__','-D_FILE_OFFSET_BITS=64','-Wno-varargs']
flags += ['-I'+str(x) for x in [setup,a.wx_source/'include',source/'include',source/'include/tinyxml',source/'include/scripting/include',source/'sdk/wxscintilla/include']]
text = (source/'src/Makefile.am').read_text().split('codeblocks_SOURCES =',1)[1].split('\n\n',1)[0]
files = re.findall(r'[\w/]+\.cpp', text)
def compile_file(name):
    path = source/'src'/name
    obj = out/(name+'.o')
    subprocess.run(flags+['-c',str(path),'-o',str(obj)],check=True)
    print('Compiled '+name,flush=True)
    return obj
with ThreadPoolExecutor(max_workers=4) as pool:
    objects = list(pool.map(compile_file,files))
libs = a.app/'Contents/MacOS'
wx = list(libs.glob('libwx_*-3.2.0.3.0.dylib'))
subprocess.run(['clang++','-arch','x86_64','-mmacosx-version-min=11.0','-Wl,-headerpad_max_install_names','-framework','Cocoa','-framework','CoreFoundation','-o',str(out/'codeblocks')]+[str(x) for x in objects+[libs/'libcodeblocks.0.dylib']+wx],check=True)
subprocess.run(['codesign','--force','--sign','-',str(out/'codeblocks')],check=True)
