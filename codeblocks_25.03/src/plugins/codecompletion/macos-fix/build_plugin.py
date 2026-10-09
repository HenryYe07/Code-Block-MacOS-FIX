#!/usr/bin/env python3
"""Build the 25.03 plugin against an existing Intel Mac application bundle."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import re
import subprocess
import zipfile


def run(command):
    subprocess.run(command, check=True)


def main():
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument('--app', type=Path, default=Path('/Applications/CodeBlocks.app'))
    args.add_argument('--wx-source', type=Path, required=True)
    args.add_argument('--wx-build', type=Path, required=True)
    args.add_argument('--output', type=Path, default=Path(__file__).resolve().parent)
    args.add_argument('--sanitize', action='store_true', help='Build with AddressSanitizer for diagnosis')
    opts = args.parse_args()
    plugin = Path(__file__).resolve().parents[1]
    source = plugin.parents[1]
    output = opts.output.resolve()
    output.mkdir(parents=True, exist_ok=True)
    objects = output / 'objects'
    objects.mkdir(exist_ok=True)
    app_libs = opts.app.resolve() / 'Contents/MacOS'
    setups = list((opts.wx_build.resolve() / 'lib/wx/include').glob('*osx_cocoa-unicode-3.2/wx/setup.h'))
    if len(setups) != 1:
        args.error('--wx-build must contain one configured Cocoa wxWidgets 3.2 setup.h')
    flags = ['clang++', '-arch', 'x86_64', '-mmacosx-version-min=11.0',
             '-std=c++11', '-O2', '-g', '-fPIC', '-DBUILDING_PLUGIN', '-DNOPCH',
             '-DTIXML_USE_STL=YES', '-D_FILE_OFFSET_BITS=64', '-DwxDEBUG_LEVEL=0',
             '-DWXUSINGDLL', '-D__WXMAC__', '-D__WXOSX__', '-D__WXOSX_COCOA__',
             '-Wno-varargs',
             '-I' + str(setups[0].parents[1]),
             '-I' + str(opts.wx_source.resolve() / 'include'),
             '-I' + str(source / 'include'), '-I' + str(source / 'include/tinyxml'),
             '-I' + str(source / 'sdk/wxscintilla/include')]
    if opts.sanitize:
        flags += ['-fsanitize=address', '-fno-omit-frame-pointer']
    makefile = (plugin / 'Makefile.am').read_text()
    section = makefile.split('libcodecompletion_la_SOURCES =', 1)[1].split('\n\n', 1)[0]
    sources = re.findall(r'[\w/]+\.cpp', section)

    def compile_file(filename):
        obj = objects / (filename.replace('/', '_') + '.o')
        run(flags + ['-c', str(plugin / filename), '-o', str(obj)])
        print('Compiled ' + filename, flush=True)
        return obj

    with ThreadPoolExecutor(max_workers=4) as executor:
        built = list(executor.map(compile_file, sources))
    library = output / 'libcodecompletion.dylib'
    wx_names = ['libwx_osx_cocoau_' + n + '-3.2.0.3.0.dylib'
                for n in ['aui', 'propgrid', 'richtext', 'xrc', 'html', 'qa', 'core']]
    wx_names += ['libwx_baseu' + n + '-3.2.0.3.0.dylib' for n in ['_xml', '_net', '']]
    libraries = [app_libs / 'libcodeblocks.0.dylib'] + [app_libs / n for n in wx_names]
    link = ['clang++', '-arch', 'x86_64', '-mmacosx-version-min=11.0', '-dynamiclib',
         '-Wl,-undefined,error', '-Wl,-headerpad_max_install_names',
         '-Wl,-unexported_symbols_list,' + str(plugin / 'macos-unexported-symbols.list'),
         '-Wl,-install_name,@loader_path/libcodecompletion.dylib',
         '-o', str(library)] + [str(p) for p in built + libraries]
    if opts.sanitize:
        link += ['-fsanitize=address']
    run(link)
    run(['codesign', '--force', '--sign', '-', str(library)])
    exports = subprocess.check_output(['xcrun', 'dyld_info', '-exports', str(library)], text=True)
    (output / 'exports.txt').write_text(exports)
    if re.search(r'^\s+0x[0-9A-Fa-f]+', exports, re.M):
        raise RuntimeError('Plugin still exports definitions: ' + exports)

    resource_text = (plugin / 'resources/Makefile.am').read_text()
    section = resource_text.split('resources_forZIP =', 1)[1].split('\ncodecompletion.zip', 1)[0]
    resources = [line.strip().rstrip('\\').strip() for line in section.splitlines()]
    resources = [name for name in resources if name and (plugin / 'resources' / name).is_file()]
    resource_zip = output / 'codecompletion.zip'
    with zipfile.ZipFile(resource_zip, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name in resources:
            archive.write(plugin / 'resources' / name, name)
    with zipfile.ZipFile(output / 'codecompletion-macos-x86_64-fixed.cbplugin', 'w',
                         zipfile.ZIP_DEFLATED) as archive:
        archive.write(library, library.name)
        archive.write(resource_zip, resource_zip.name)
        for name in ['codecompletion.png', 'codecompletion-off.png']:
            archive.write(opts.app / 'Contents/Resources/share/codeblocks/images/settings' / name, name)
        archive.comment = b'This is a redistributable plugin for the Code::Blocks IDE.'
    print('Built plugin and resources in ' + str(output))


if __name__ == '__main__':
    main()
