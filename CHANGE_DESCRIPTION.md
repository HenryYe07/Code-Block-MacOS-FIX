# Fix macOS code completion startup and encoding conversion crashes

Code::Blocks can crash while attaching the legacy codecompletion plugin when clangd_client is also loaded. Both plugins define weak C++ methods with identical names but incompatible class layouts, allowing dyld to bind an accessor to the other plugin's implementation. The resulting parser pointer is invalid during class-browser setup.

Move the legacy plugin implementation into `CodeCompletionInternals` and hide its defined symbols on Darwin. Preserve static SDK plugin registration. Split attachment into state reset, event registration, and guarded session initialization; create the class browser after application startup, and initialize immediately when enabling the plugin in an already-running application. Adapt the parser test sources to the namespace.

A separate file-opening failure occurs in the SDK's legacy `wxEncodingConverter` path with the system encoding in the tested macOS environment. Use one length-aware `wxCSConv` conversion path for all encodings, retain the existing configured fallback behavior, and report conversion failures. Validate file length and complete reads, manage the byte buffer with RAII, handle empty files, and preserve embedded NUL characters.

Validation:

- Built optimized x86_64 plugin and SDK against the application's wxWidgets 3.2.6 runtime; verified signatures and required SDK imports.
- All 15 focused encoding regression cases passed, covering Unicode byte orders/BOMs, empty input/files, embedded NUL, invalid UTF-8, CP1252, and GB2312.
- All 14 parser-test translation units passed compilation checks.
- On macOS Sequoia 15.7.3, the repaired application starts, opens a C++ project and source file, displays class members in the symbol browser, and inserts `member_method` through member completion.

Validation used the Code::Blocks 25.03 Intel application under Rosetta on Apple Silicon. Large projects and other binary distributions have not been validated.

The source retains the upstream licenses. The two patches contain the functional changes; the optional `macos-fix` directory supplies local build helpers and regression-test source.

The separately supplied `henryye-splash.patch` adds the local build label “HenryYe修复版 支持新的MacOS” below the release number on the macOS splash screen. It is optional branding and independent of the two crash fixes.

The independent `macos-light-appearance.patch` sets `NSRequiresAquaSystemAppearance` to true in the macOS bundle template. The packaged build always uses the light Aqua appearance, regardless of the system appearance preference. This does not change macOS settings or editor color schemes selected separately by the user.
