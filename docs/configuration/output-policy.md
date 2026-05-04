# Output Policy

## Purpose
Output policy controls default mode, max output tokens, and preservation of code, commands, paths, symbols, warnings, and numbers.

## Current Status
Output policy is implemented through default output mode, max output tokens, and preservation rules.
The output budget controller uses these settings to reduce low-signal prose while preserving code,
commands, paths, symbols, warnings, numbers, errors, and test results.

## Related Commands
```bash
opencontext init --template generic
opencontext init --template enterprise
opencontext doctor security
opencontext provider simulate --provider openai --classification confidential
```

## Planned Contents
More examples for organization baselines, provider adapters, and signed workflow packs.
