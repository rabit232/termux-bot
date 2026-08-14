# Module-Harmony Catalog

This catalog turns the supplied Python collection into a coherent architecture rather than a single unmaintainable import directory. The complete static file-by-file list is in [MODULE_INVENTORY.md](MODULE_INVENTORY.md). This document records the **integration disposition** for the modules that form the supplied system designs.

> **Interpretation of “add everything together”:** Every source module has been audited and assigned to a core implementation, optional adapter, reference boundary, duplicate set, or blocked capability. This branch integrates compatible behavior into a small Termux runtime; it does not activate every capability merely because code exists in an archive.

## NewTermux archive: cognitive and memory modules

| Source modules | Harmonized role | Disposition in 0.2 |
| --- | --- | --- |
| `mock_model.py`, `mock_generator.py`, `embedding_engine.py`, `embedding_cache.py`, `tensor_memory.py`, `semantic_search.py` | Lightweight local semantic retrieval and ranking | **Integrated by behavior** in `cognition.semantic`, `cognition.reasoning`, and SQLite cognitive records. The new implementation uses stable SHA-256 projection rather than process-random Python hashes. |
| `knowledge_graph.py`, `knowledge_graph_v2.py`, `graph_reasoner.py`, `learning_engine.py`, `memory_manager.py`, `memory_consolidator.py`, `graph_memory_consolidator.py`, `knowledge_synthesizer.py` | Local graph learning and memory consolidation | **Integrated by behavior** in `cognition.knowledge`, `memory`, and `cognition.runtime`. Only local text associations are retained. |
| `context_manager.py`, `conversation_memory.py`, `working_memory.py`, `thought_stream.py`, `predictive_memory_engine.py` | Bounded message context | **Integrated by behavior** through `cognition.context`, message hydration, and a capped semantic index. No predictive prefetch or background task runs. |
| `attention_engine.py`, `attention_router.py`, `reasoning_engine.py`, `reasoning_engine_patched.py`, `reasoning_scheduler.py`, `inference_engine.py`, `hypothesis_engine.py`, `reflection_engine.py`, `response_ranker.py` | Explainable text reasoning | **Integrated by behavior** in `cognition.reasoning`. Reasoning produces diagnostics and context only; it cannot call tools. |
| `personality_engine.py`, `emotion_manager.py`, `concept_evolution.py`, `experience_engine.py`, `self_evaluation.py` | Tone and learning metadata | **Integrated by behavior** in `cognition.persona`; adaptation is bounded metadata and cannot override safety policy. |
| `planning_engine.py`, `goal_manager.py`, `workflow_engine.py`, `meta_controller.py` | User-visible planning | **Integrated narrowly** as `?plan`, which returns a text plan and creates no task queue or execution. |
| `blackboard_patched.py`, `event_bus.py`, `agent_communication_bus.py`, `agent_debate_engine.py`, `agent_manager.py`, `agent_registry.py`, `dynamic_agent_selector.py` | Multi-component coordination | **Reference-only** for now. The message-scoped runtime is intentionally simpler than a multi-agent service mesh. |
| `cognitive_cycle.py`, `cognitive_state.py`, `cognitive_orchestrator.py` | Cognitive-cycle coordination | **Reference-only**. Their responsibilities are represented by the deterministic `CognitiveRuntime` call order rather than an autonomous cycle. |
| `learning_scheduler.py`, `autonomous_loop.py` | Periodic and background processing | **Blocked by default.** The Termux bot performs no background or autonomous loop. |
| `cluster_coordinator.py`, `cluster_protocol.py`, `cluster_sync.py`, `distributed_agent_runtime.py`, `distributed_manager.py`, `distributed_memory_manager.py` | Multi-device/distributed execution | **Blocked by default.** These require a separate network and security design. |
| `matrix_bot.py`, `matrix_bot_patched.py`, `matrix_client.py`, `matrix_commands.py`, `matrix_events.py`, `matrix_login.py` | Matrix transport | **Replaced by the canonical** `ribit_termux.matrix_bot`, preserving authorized text-only commands. |
| `ribit_termux_enhanced.py`, `ribit_termux_enhanced (1).py`, `ribit_termux_ribit_compat.py` | Earlier monolithic Termux implementations | **Replaced and deduplicated.** Application-opening, dynamic module loading, and hard-coded defaults are not carried forward. |
| `robotics_interface.py`, `robotics_interface (1).py`, `tool_router.py`, `plugin_manager.py`, `web_search.py` | Device, dynamic plug-in, and web capabilities | **Blocked by policy.** Process, web, GUI, and robot capabilities remain false. |
| `config.py`, `configuration_loader.py`, `storage_manager.py`, `sqlite_storage.py`, `crystal_adapter.py`, `crystal_importer.py`, `system_monitor.py`, `main.py`, `main_patched.py` | Configuration, persistence, assembly, and monitoring | **Superseded** by the existing environment-only `config.py`, SQLite `memory.py`, and `engine.py`. |
| `mock_model_v2_part1.py` through `mock_model_v2_part7.py`, `mock_model_v2_final.py` | Fragmented second mock-model path | **Reference-only.** It duplicates reasoning/agent concepts already unified in the cognitive runtime and needs a single versioned API before direct use. |

## Canonical Ribit 2.0 package

| Module group | Harmonized role | Disposition in 0.2 |
| --- | --- | --- |
| `mock_llm_wrapper.py`, `knowledge_base.py`, `response_samples.py` | Offline Ribit response fallback | **Integrated directly** under `vendor/ribit_2_0`, with every returned action plan filtered to display text. |
| `enhanced_mock_llm.py`, `advanced_mock_llm.py`, `dual_llm_pipeline.py` | Parameter and response experimentation | **Reference-only.** They inherit the raw action-plan contract and need a text-only interface before being enabled. |
| `enhanced_emotions.py`, `linguistics_engine.py`, `humor_engine.py`, `conversational_mode.py`, `philosophical_reasoning.py`, `intelligent_responder.py`, `history_responder.py`, `user_engagement.py` | Response presentation | **Represented by** the local persona/context layer. They can become optional text-only providers later. |
| `conversation_manager.py`, `conversation_memory.py`, `message_history_learner.py`, `word_learning_system.py` | Learning and history | **Represented by** SQLite memory and the cognitive semantic/graph runtime. The source word-learning restore path is not used because it contains dynamic evaluation. |
| `matrix_bot.py`, `enhanced_matrix_integration.py`, `secure_matrix_bot.py`, `integrated_secure_matrix_bot.py`, `matrix_*`, `deltachat_*`, `bridge_*`, `autonomous_matrix.py` | Alternate transports and encryption experiments | **Reference-only.** The branch does not claim E2EE or bridge interoperability. |
| `controller.py`, `mock_controller.py`, `ros_controller.py`, `agent.py` | Vision, device, and robot control | **Blocked by policy.** |
| `enhanced_web_search.py`, `jina_integration.py`, `web_knowledge.py`, `web_scraping_wikipedia.py` | Web access | **Blocked by policy.** |
| `image_generation.py`, `image_generator.py`, `image_provider.py`, `offline_image_analyzer.py`, `matrix_image_sender.py`, `emoji_expression.py` | Media features | **Reference-only**; no media path is part of the chat prototype. |
| `multi_language_system.py`, `self_testing_system.py`, `programming_assistant.py` | Code generation and execution/testing | **Blocked by policy.** Generated text can be reviewed, but the bot cannot execute it. |
| `advanced_settings_manager.py`, `task_autonomy.py`, `megabite_llm.py`, `ribit_offline_features_demo.py` | Advanced runtime and demos | **Reference-only.** |

## GhostOS–Ribit and GhostOS core

| Source group | Disposition in 0.2 |
| --- | --- |
| `ribit_ghostos/policy.py` | **Integrated by design** as `ribit_termux.policy`, extended with GUI control denial. |
| `ribit_ghostos/bridge.py`, `knowledge.py`, `word_learning.py`, `conversation.py` | **Integrated by design** through local persistence, bounded context, and the text-only model-output boundary. |
| `ribit_ghostos/local_llm.py` | **Integrated by behavior** in `providers.LocalOpenAICompatibleClient`, restricted to loopback endpoints. |
| `ribit_ghostos/structured_code.py`, `ghostos_adapter.py`, `ribit_import.py`, `pixels.py` | **Reference-only.** Code artifacts require a separately enabled write policy and no full GhostOS/MOSS host is installed in Termux. |
| GhostOS core and MOSS libraries | **External optional ecosystem.** The static inventory records 457 modules; none is imported by the standard Termux bot. |

## Molequla

The five supplied Python modules remain a **separate research runtime**. The static inventory identifies background/thread and subprocess-oriented execution patterns in the standalone ecology and Mycelium coordination code. No Molequla trainer, organism, mycelium, or autonomous loop is imported into the Matrix process.

## Deduplication register

| Identical content group | Canonical treatment |
| --- | --- |
| `agent_manager.py` and `agent_manager (1).py` | One archive pattern only; neither is active in the Termux runtime. |
| `ribit_termux_enhanced.py` and `ribit_termux_enhanced (1).py` | Replaced by the package-based `ribit_termux` implementation. |
| `robotics_interface.py` and `robotics_interface (1).py` | Not activated; robot actuation is denied by policy. |
| Empty and repeated GhostOS package/test files | Recorded in the inventory; no copy is needed in the Termux package. |

## Subsequent 0.2 extensions

| Supplied source module | 0.2 implementation | Runtime behavior |
| --- | --- | --- |
| Ribit 2.0 `linguistics_engine.py` | `ribit_termux.cognition.linguistics.LinguisticAnalyzer` | Adds bounded intent, tone, formality, question-depth, key-phrase, and local sender-style metadata. It keeps at most the configured number of in-memory records per sender. |
| Ribit 2.0 `conversational_mode.py` | `ribit_termux.cognition.conversation.TextOnlyConversationGuard` | Classifies automation-style prompts and returns a text-only capability refusal before a provider is called. It never switches to automation mode. |
| NewTermux `working_memory.py` | `ribit_termux.cognition.working.WorkingMemory` | Provides a capacity-bounded, importance-aware local cache for active message context. |
| NewTermux `thought_stream.py` | `ribit_termux.cognition.working.ThoughtTrace` | Keeps short user-safe diagnostic event summaries, not hidden reasoning or executable task state. |
| NewTermux `conversation_memory.py`, Ribit history-learning patterns | `MemoryStore.room_history()` and `?history [1-200]` | Reads only the current room’s locally stored transcript, with hard message and output-size caps. |

The vendored `MockRibit20LLM` subset was also tightened: optional web, Matrix-enhancement, self-testing execution, multi-language execution, GUI, and robot integrations are not imported. Its text-only capability metadata now reflects the Termux runtime boundary.
