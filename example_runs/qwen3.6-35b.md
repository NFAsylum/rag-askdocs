# Example queries

Recorded output of the RAG pipeline over the default corpus (Babel's `docs/` + `examples/`). Every answer below is real pipeline output — nothing here is hand-written. Regenerate with `python examples.py`.

- **Generation model:** qwen3.6-35b (OpenAI-compatible @ http://127.0.0.1:8090/v1)
- **Generated on:** 2026-07-09

## What is Babel and what problem does it solve?

Based on the retrieved context, Babel (specifically the `babel-tcc` project) is a tool that translates programming keywords and identifiers into natural languages (such as Portuguese and Spanish). It addresses the need to localize code syntax by providing a structured system that parses code into tokens, generates an Abstract Syntax Tree (AST), and applies translations using a JSON-based data layer while preserving the original code structure. Additionally, it provides a framework for IDE integration and supports adding new programming languages and translation tables.

**Sources:** `faq.md`, `troubleshooting.md`, `plano-geral.txt`, `adding-new-language.md`

## Which programming languages does Babel support for translation?

Based on the retrieved context, the supported programming languages are **C#, Python, JavaScript, and Java** (listed under the `multilingual-translations/programming-languages/` directory structure).

**Sources:** `faq.md`, `plano-geral.txt`, `plano-geral.txt`, `repos.txt`

## How do I add support for a new IDE to Babel?

Based on the retrieved context, adding support for a new IDE involves the following steps:

1. **Spawn the Core Process:** Execute the Core Engine using: `dotnet /path/to/MultiLingualCode.Core.Host.dll --method ... --params ...`
2. **Parse the Response:** Read and parse the JSON response from the Core's `stdout`.
3. **Implement Basic Features:**
   - Open a view displaying the translated code
   - Intercept `save` events to translate code back to the original language
   - Add a toggle to enable/disable the feature
   - Implement a language selector
4. **Optional Features:**
   - Autocomplete with translated keywords
   - Hover tooltips showing the original keyword
   - Syntax highlighting

The Core Engine is IDE-independent and communicates via a JSON stdin/stdout protocol. For a complete reference implementation, review the existing VS Code adapter located in `packages/ide-adapters/vscode/`.

**Sources:** `adding-new-ide.md`, `adding-new-ide.md`, `plano-geral.txt`, `plano-geral.txt`

## How do I install and set up Babel?

Based on the provided documentation for the `babel-tcc` repository, here is the setup process:

1. **Prerequisites:** Ensure the .NET SDK is installed and in your PATH (verify with `dotnet --version`).
2. **Dependencies:** If `npm install` fails, clear the cache and reinstall:
   ```bash
   npm cache clean --force
   rm -rf node_modules
   npm install
   ```
3. **Core Binary:** Run `npm run publish-core` to populate the required Core binary (`bin/MultiLingualCode.Core.Host.dll`) relative to the extension directory.
4. **Launch:** Press `F5` (or select **Run > Start Debugging**) in VS Code.
5. **Test:** A new VS Code window will open with the extension loaded. Open a `.cs` file to test it.

**Notes:**
* No environment variables are required for local development.
* If the extension fails to activate, check the `babel-tcc` Output Channel in VS Code for error logs.
* For further issues, refer to the troubleshooting guide or open a GitHub issue at `https://github.com/NFAsylum/babel-tcc/issues`.

**Sources:** `setup-ambiente.md`, `faq.md`, `repos.txt`, `troubleshooting.md`

## What is Babel's architecture?

Based on the provided context, the architecture for the `babel-tcc` (MultiLingualCode) project is structured as a monorepo with the following core components:

* **Core Engine (`packages/core/`)**: A C# library that handles the main processing logic. It follows a 4-step pattern:
  1. Parses code into tokens (via native parser, subprocess, or Text Scan)
  2. Classifies each token as a keyword, identifier, or literal
  3. Creates AST nodes with `start`/`end` positions for reconstruction
  4. Runs a `Generate()` function that applies substitutions in reverse order of those positions
* **IDE Adapters (`packages/ide-adapters/`)**: Currently includes a VS Code extension that bridges to the Core engine via `CoreBridge.ts`. It contains services (configuration, language detection), UI components (language selector, status bar), and syntax definitions. Future adapters for Visual Studio and IntelliJ are planned.
* **CLI (`cli/`)**: An optional command-line tool featuring commands for translation and validation.
* **Language Data (`languages/`)**: Contains JSON tables defining keywords, metadata, and translation mappings for supported programming languages.

**Deployment/Integration Notes:**
* The VS Code extension locally loads the Core binary from `bin/MultiLingualCode.Core.Host.dll` (populated via `npm run publish-core`).
* No environment variables are required for local development or runtime.

**Sources:** `adding-new-language.md`, `setup-ambiente.md`, `plano-geral.txt`, `README.md`
