# macOS repair build helpers

Run these scripts from this source snapshot with Python 3 and Xcode Command Line Tools. Both target the Code::Blocks 25.03 Intel application and its bundled wxWidgets 3.2.6 libraries. Apple Silicon runs the resulting application through Rosetta.

```sh
python3 build_plugin.py --wx-source /path/to/wxWidgets-3.2.6 --wx-build /path/to/wx-build --app /Applications/CodeBlocks.app
python3 build_core.py --wx-source /path/to/wxWidgets-3.2.6 --wx-build /path/to/wx-build --app /Applications/CodeBlocks.app
```

The wx build directory must contain matching Cocoa/x86_64 configuration headers: non-debug, macOS minimum 11.0, wxUSE_STL=0, and the same image-library options as the bundled runtime. Do not use headers from a different wxWidgets version or an ARM64 Homebrew installation.

The SDK source at `src/sdk/encodingdetector.cpp` is already fixed. `core/encodingdetector.cpp` is an identical overlay used by the helper. Keep both copies synchronized when editing. The ordinary upstream build files remain available for normal builds on other platforms.

`core/encoding_regression.cpp` contains the focused encoding regression harness. These helper scripts produce build outputs locally; those outputs are excluded from the delivered source snapshot.

Build the main executable with the optional macOS splash label:

```sh
python3 build_app.py --wx-source /path/to/wxWidgets-3.2.6 --wx-build /path/to/wx-build --app /Applications/CodeBlocks.app --output /path/to/app-build
```

Copy the resulting `codeblocks` executable into the repaired application's `Contents/MacOS` and re-sign the complete bundle.
