# Example queries

Recorded output of the RAG pipeline over the default corpus (Babel's `docs/` + `examples/`). Every answer below is real pipeline output — nothing here is hand-written. Regenerate with `python examples.py`.

- **Generation model:** qwen2.5-coder-7b (OpenAI-compatible @ http://127.0.0.1:8090/v1)
- **Generated on:** 2026-07-09

## What is Babel and what problem does it solve?

Babel is a tool that helps in translating code between different programming languages. It solves the problem of code incompatibility across various programming languages by providing a way to convert code from one language to another, ensuring that it can be executed in different environments or by different tools that support different languages.

**Sources:** `faq.md`, `troubleshooting.md`, `plano-geral.txt`, `adding-new-language.md`

## Which programming languages does Babel support for translation?

Babel supports translation for the following programming languages: C#, Python, and JavaScript.

**Sources:** `faq.md`, `plano-geral.txt`, `plano-geral.txt`, `repos.txt`

## How do I add support for a new IDE to Babel?

To add support for a new IDE to Babel, you need to follow these steps:

1. **Spawn the Core Process**: Use the command to start the Core Engine, which is independent of the IDE. The command format is:
   ```
   dotnet /path/to/MultiLingualCode.Core.Host.dll --method ... --params ...
   ```

2. **Parse the JSON Response**: Implement logic to parse the JSON output from the Core Engine's stdout.

3. **Implement Basic Features**:
   - Open a view with translated code.
   - Intercept save operations to translate the code back.
   - Toggle the translation feature on and off.
   - Add a language selector.

4. **Optional Features**:
   - Implement autocomplete with translated keywords.
   - Provide hover information with the original keyword.
   - Add syntax highlighting for the translated code.

For a concrete example, you can refer to the implementation of the VS Code adapter in the `packages/ide-adapters/vscode/` directory. This directory contains TypeScript files that handle the integration between the Core Engine and the IDE, including the necessary commands, events, and UI components.

**Sources:** `adding-new-ide.md`, `adding-new-ide.md`, `plano-geral.txt`, `plano-geral.txt`

## How do I install and set up Babel?

To install and set up Babel, follow these steps:

1. **Clone the Repository**: First, clone the Babel repository to your local machine using Git.
   ```bash
   git clone https://github.com/NFAsylum/babel-tcc.git
   ```

2. **Navigate to the Project Directory**: Change your directory to the project folder.
   ```bash
   cd babel-tcc
   ```

3. **Install Dependencies**: Install the necessary dependencies using npm.
   ```bash
   npm install
   ```

4. **Build the Core**: Build the core engine using the provided script.
   ```bash
   npm run publish-core
   ```

5. **Open the Project in VS Code**: Open the project in Visual Studio Code.
   ```bash
   code .
   ```

6. **Start Debugging**: Press `F5` or use the Run > Start Debugging option to start debugging.

7. **Test with a C# File**: Open a `.cs` file to test the extension.

Ensure that the .NET SDK is installed and accessible in your PATH. If you encounter any issues, refer to the [troubleshooting guide](troubleshooting.md) for common problems and solutions.

**Sources:** `setup-ambiente.md`, `faq.md`, `repos.txt`, `troubleshooting.md`

## What is Babel's architecture?

Babel's architecture is designed to support multiple programming languages, with a focus on C#. The core engine is located in the `MultiLingualCode.Core` package, which includes libraries and tests. The VS Code extension is in the `vscode` directory under `ide-adapters`, with its source code in the `src` folder and a `package.json` file for configuration. The project also includes examples, documentation, and a README file.

**Sources:** `adding-new-language.md`, `setup-ambiente.md`, `plano-geral.txt`, `README.md`
