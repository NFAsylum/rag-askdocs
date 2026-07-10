# Example queries

Recorded output of the RAG pipeline over the default corpus (Babel's `docs/` + `examples/`). Every answer below is real pipeline output — nothing here is hand-written. Regenerate with `python examples.py`.

- **Generation model:** qwen2.5-coder-7b (OpenAI-compatible @ http://127.0.0.1:8090/v1)
- **Generated on:** 2026-07-09

## What is Babel and what problem does it solve?

I don't have enough information in the retrieved context to answer that.

**Sources:** `faq.md`, `troubleshooting.md`, `plano-geral.txt`, `adding-new-language.md`

## Which programming languages does Babel support for translation?

Babel supports translation for the following programming languages: C#, Python, JavaScript, and Java.

**Sources:** `faq.md`, `plano-geral.txt`, `plano-geral.txt`, `repos.txt`

## How do I add support for a new IDE to Babel?

To add support for a new IDE to Babel, follow these steps:

1. **Spawn the Core Process:**
   ```
   dotnet /path/to/MultiLingualCode.Core.Host.dll --method ... --params ...
   ```

2. **Parse the JSON Response from stdout.**

3. **Implement Basic Features:**
   - Open a view with translated code.
   - Intercept save events to translate code back.
   - Toggle on/off functionality.
   - Language selector.

4. **Optional Features:**
   - Autocomplete with translated keywords.
   - Hover to show original keywords.
   - Syntax highlighting.

For a detailed implementation, refer to the VS Code adapter in `packages/ide-adapters/vscode/`.

**Sources:** `adding-new-ide.md`, `adding-new-ide.md`, `plano-geral.txt`, `plano-geral.txt`

## How do I install and set up Babel?

I don't have enough information in the retrieved context to answer that.

**Sources:** `setup-ambiente.md`, `faq.md`, `repos.txt`, `troubleshooting.md`

## What is Babel's architecture?

I don't have enough information in the retrieved context to answer that.

**Sources:** `adding-new-language.md`, `setup-ambiente.md`, `plano-geral.txt`, `README.md`
