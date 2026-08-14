# Supplied-Project Compatibility Record

This record explains how the supplied repositories and archives relate to the **Ribit Termux 0.2** prototype. The goal of the branch is a maintainable Android Termux bot, not a wholesale merge of unrelated runtimes. Every supplied file was treated as source data for review; none was executed merely because it was present in an archive.

| Source | Review finding | 0.2 disposition | Rationale |
| --- | --- | --- | --- |
| [`rabit232/termux-bot`](https://github.com/rabit232/termux-bot) | Existing Matrix/Termux entry point, SQLite memory, and local-model fallback | **Integration base** | Refactored into a smaller package and retained the `ribit_termux.py` launch path. |
| [`rabit232/ribit.2.0`](https://github.com/rabit232/ribit.2.0) | Canonical `MockRibit20LLM` returns action-plan strings as well as text | **Integrated narrowly** | Vendors the three minimal mock files and puts every decision behind a text-only extraction boundary. |
| `ghostOS-ribit.2.0-0.1.zip` | Contains the local-first `ribit_ghostos` add-on, including a loopback OpenAI-compatible client and a non-executing conversation adapter | **Integrated by design** | Ports the loopback-only endpoint policy and the display-text-only action-plan handling without importing the full GhostOS runtime. |
| `GhostOS-main.zip` | A larger multi-library GhostOS/MOSS source tree | **Not bundled** | The supplied add-on is purpose-built to be optional and local-first; a full GhostOS/MOSS deployment is outside the Android prototype’s dependency and resource boundary. |
| `newtemrux-bot-teat.zip` | Alternative Termux prototype and a dynamic external-module compatibility layer | **Reviewed, not copied** | It helped identify existing model and memory seams, but dynamic arbitrary-module loading and embedded runtime defaults were not retained in the 0.2 safety model. |
| `neural_memory.db` | Private SQLite runtime data | **Kept untracked** | It is never copied into Git. The README describes a manual, backed-up migration path only. |
| `molequla-main.zip` | A large multi-language autonomous ecology with CPU/GPU-oriented training and optional long-running evolution modes | **Not bundled** | Its architecture is not a small local chat-completion provider and would add a separate heavy training/runtime system beyond this Termux Matrix bot prototype. |

> **Key boundary:** Ribit 2.0 output is not a command channel. Even when `MockRibit20LLM` returns strings containing `run_command`, `type_text`, drawing, web, robot, or automation plans, 0.2 does not interpret or execute them.

## Included source provenance

The vendored fallback comes from the following Ribit 2.0 revision and files:

| Upstream revision | Files copied | Local destination |
| --- | --- | --- |
| `88f60d941a9b6a3aae57618025f04609f6faa69e` | `mock_llm_wrapper.py`, `knowledge_base.py`, `response_samples.py` | `vendor/ribit_2_0/` |

The Termux integration begins from Termux bot revision `3d3c253af21b658e557d166e04d0f61502af572d`. The GhostOS-related logic is a small adaptation of the supplied `ribit_ghostos` package’s `local_llm.py` and `conversation.py`; it is not a copy of the wider GhostOS codebase.

## Deliberate exclusions

The branch does not install or expose browser control, robot control, application launchers, shell-command execution, automatic external module discovery, remote LLM endpoints, or autonomous background loops. It also does not claim Matrix E2EE support. These exclusions are documented in the implementation and README so future development does not mistake the 0.2 prototype for a general-purpose device-control agent.

The Molequla archive remains a separate research runtime. If it is later desired as an inference backend, the appropriate next step is a separate Termux feasibility assessment that defines a stable, loopback-only text-completion interface and measurable device resource limits. It should not be merged directly into the Matrix bot.

## References

[1]: https://github.com/rabit232/termux-bot "Termux bot source repository"
[2]: https://github.com/rabit232/ribit.2.0 "Ribit 2.0 source repository"
