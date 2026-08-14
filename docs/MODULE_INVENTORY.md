# Static Python Module Inventory

> This inventory was built with Python AST parsing only. None of the listed source modules was imported or executed.

## Scope summary

| Metric | Count |
| --- | ---: |
| Python files analyzed | 629 |
| Successfully parsed | 628 |
| Parse failures | 1 |
| Duplicate-content groups | 5 |

## Modules by source

| Source | Python files |
| --- | ---: |
| `ghostos_core` | 457 |
| `ghostos_ribit_addon` | 13 |
| `molequla` | 5 |
| `newtermux_archive` | 89 |
| `ribit_2_0` | 56 |
| `termux_0_2` | 9 |

## Modules by architectural role

| Role | Modules |
| --- | ---:
| `actuation` | 6 |
| `cognition` | 27 |
| `media` | 7 |
| `memory_learning` | 36 |
| `model` | 28 |
| `orchestration` | 44 |
| `policy_or_adapter` | 7 |
| `support` | 444 |
| `transport` | 23 |
| `web` | 7 |

## Candidate integration register

| Source | Module | Role | Classes | Capability indicators |
| --- | --- | --- | --- | --- |
| `newtermux_archive` | `agent_communication_bus.py` | `orchestration` | AgentCommunicationBus, AgentMessage | — |
| `newtermux_archive` | `agent_debate_engine.py` | `orchestration` | AgentDebateEngine | — |
| `newtermux_archive` | `agent_manager (1).py` | `orchestration` | Agent, AgentManager | — |
| `newtermux_archive` | `agent_manager.py` | `orchestration` | Agent, AgentManager | — |
| `newtermux_archive` | `agent_registry.py` | `orchestration` | AgentDescriptor, AgentRegistry | — |
| `newtermux_archive` | `attention_engine.py` | `cognition` | AttentionEngine, AttentionItem | — |
| `newtermux_archive` | `attention_router.py` | `cognition` | AgentContext, AttentionRouter | — |
| `newtermux_archive` | `autonomous_loop.py` | `orchestration` | AutonomousLoop, LoopStats | threading.Event (1), threading.Thread (1) |
| `newtermux_archive` | `blackboard_patched.py` | `support` | Blackboard, BlackboardEntry | — |
| `newtermux_archive` | `cluster_coordinator.py` | `orchestration` | ClusterCoordinator, ClusterNodeStatus, ClusterTask | — |
| `newtermux_archive` | `cluster_protocol.py` | `orchestration` | ClusterMessage, ClusterProtocol | — |
| `newtermux_archive` | `cluster_sync.py` | `orchestration` | ClusterSync, SyncJob | — |
| `newtermux_archive` | `cognitive_cycle.py` | `cognition` | CognitiveCycle, CognitiveState | — |
| `newtermux_archive` | `cognitive_orchestrator.py` | `cognition` | CognitiveOrchestrator | — |
| `newtermux_archive` | `cognitive_state.py` | `cognition` | CognitiveState | — |
| `newtermux_archive` | `concept_evolution.py` | `support` | Concept, ConceptEvolution | — |
| `newtermux_archive` | `config.py` | `support` | AppConfig, LearningConfig, MatrixConfig, ModelConfig, PersonalityConfig | — |
| `newtermux_archive` | `configuration_loader.py` | `support` | ConfigurationLoader | — |
| `newtermux_archive` | `context_manager.py` | `orchestration` | ContextManager, ContextPackage | — |
| `newtermux_archive` | `conversation_memory.py` | `memory_learning` | ConversationMemory, Message | — |
| `newtermux_archive` | `crystal_adapter.py` | `support` | CrystalAdapter | — |
| `newtermux_archive` | `crystal_importer.py` | `support` | CrystalImporter | — |
| `newtermux_archive` | `distributed_agent_runtime.py` | `orchestration` | AgentNode, DistributedAgentRuntime | — |
| `newtermux_archive` | `distributed_manager.py` | `orchestration` | DistributedManager, Node | — |
| `newtermux_archive` | `distributed_memory_manager.py` | `memory_learning` | DistributedMemoryManager, MemoryUpdate | — |
| `newtermux_archive` | `dynamic_agent_selector.py` | `orchestration` | DynamicAgentSelector, SelectedAgent | — |
| `newtermux_archive` | `embedding_cache.py` | `memory_learning` | EmbeddingCache | — |
| `newtermux_archive` | `embedding_engine.py` | `memory_learning` | EmbeddingEngine, EmbeddingResult | — |
| `newtermux_archive` | `emotion_manager.py` | `cognition` | EmotionManager, EmotionState | — |
| `newtermux_archive` | `event_bus.py` | `orchestration` | Event, EventBus | — |
| `newtermux_archive` | `experience_engine.py` | `support` | Experience, ExperienceEngine | — |
| `newtermux_archive` | `gemma_fallback.py` | `support` | GemmaFallback, GenerationResult | — |
| `newtermux_archive` | `goal_manager.py` | `orchestration` | Goal, GoalManager | — |
| `newtermux_archive` | `graph_memory_consolidator.py` | `memory_learning` | ConsolidationReport, GraphMemoryConsolidator | — |
| `newtermux_archive` | `graph_reasoner.py` | `memory_learning` | GraphReasoner, Inference | — |
| `newtermux_archive` | `hypothesis_engine.py` | `cognition` | Hypothesis, HypothesisEngine | — |
| `newtermux_archive` | `inference_engine.py` | `support` | InferenceEngine, InferenceResult, InferenceStep | — |
| `newtermux_archive` | `knowledge_graph.py` | `memory_learning` | Edge, KnowledgeGraph, Node | — |
| `newtermux_archive` | `knowledge_graph_v2.py` | `memory_learning` | Edge, KnowledgeGraphV2, Node | — |
| `newtermux_archive` | `knowledge_synthesizer.py` | `memory_learning` | KnowledgeSynthesizer, SynthesizedConcept | — |
| `newtermux_archive` | `learning_engine.py` | `support` | LearningEngine, LearningEvent | — |
| `newtermux_archive` | `learning_engine_patched.py` | `support` | SharedLearningEngine | — |
| `newtermux_archive` | `learning_scheduler.py` | `orchestration` | LearningScheduler, ScheduledJob | — |
| `newtermux_archive` | `main.py` | `support` | RibitApplication | — |
| `newtermux_archive` | `main_patched.py` | `support` | RibitApplication | — |
| `newtermux_archive` | `matrix_bot.py` | `transport` | MatrixBot | — |
| `newtermux_archive` | `matrix_bot_patched.py` | `transport` | MatrixBot | — |
| `newtermux_archive` | `matrix_client.py` | `transport` | MatrixClientWrapper | — |
| `newtermux_archive` | `matrix_commands.py` | `transport` | MatrixCommandHandler | — |
| `newtermux_archive` | `matrix_events.py` | `transport` | MatrixEventRouter, RibitBrainInterface | — |
| `newtermux_archive` | `matrix_login.py` | `transport` | MatrixLoginManager | — |
| `newtermux_archive` | `memory_consolidator.py` | `memory_learning` | ConsolidationReport, MemoryConsolidator | — |
| `newtermux_archive` | `memory_manager.py` | `memory_learning` | MemoryManager, MemoryRecord | — |
| `newtermux_archive` | `meta_controller.py` | `actuation` | ExecutionPlan, MetaController | — |
| `newtermux_archive` | `mock_generator.py` | `model` | GenerationConfig, MockGenerator | — |
| `newtermux_archive` | `mock_model.py` | `model` | ConceptGraph, LearnedWord, MemoryVector, ResponseCandidate, RibitMockModel | — |
| `newtermux_archive` | `mock_model_v2_final.py` | `model` | RibitBrain | — |
| `newtermux_archive` | `mock_model_v2_part1.py` | `model` | AgentProfile, EnhancedMockModel, Thought | — |
| `newtermux_archive` | `mock_model_v2_part2.py` | `model` | Concept, ReasoningPipeline | — |
| `newtermux_archive` | `mock_model_v2_part3.py` | `model` | Evidence, KnowledgeReasoner | — |
| `newtermux_archive` | `mock_model_v2_part4.py` | `model` | AgentCoordinator, AgentResult, BaseAgent, CreativeAgent, LogicAgent | — |
| `newtermux_archive` | `mock_model_v2_part5.py` | `model` | ConsensusEngine, ConsensusResult | — |
| `newtermux_archive` | `mock_model_v2_part6.py` | `model` | AdaptiveLearning, ConceptState | — |
| `newtermux_archive` | `mock_model_v2_part7.py` | `model` | MockModelRuntime | — |
| `newtermux_archive` | `personality_engine.py` | `cognition` | PersonalityEngine, PersonalityTraits | — |
| `newtermux_archive` | `planning_engine.py` | `cognition` | PlanTask, PlanningEngine | — |
| `newtermux_archive` | `plugin_manager.py` | `orchestration` | PluginInfo, PluginManager | importlib.import_module (1) |
| `newtermux_archive` | `predictive_memory_engine.py` | `memory_learning` | Prediction, PredictiveMemoryEngine, PrefetchPlan | — |
| `newtermux_archive` | `reasoning_engine.py` | `cognition` | ReasoningEngine, ReasoningStep | — |
| `newtermux_archive` | `reasoning_engine_patched.py` | `cognition` | ReasoningEngine | — |
| `newtermux_archive` | `reasoning_scheduler.py` | `cognition` | ReasoningRound, ReasoningScheduler | — |
| `newtermux_archive` | `reflection_engine.py` | `cognition` | ReflectionEngine, ReflectionReport | — |
| `newtermux_archive` | `response_ranker.py` | `support` | Candidate, ResponseRanker | — |
| `newtermux_archive` | `ribit_termux_enhanced (1).py` | `support` | GemmaFallbackClient, GenerationResult, MockRibitModel, RibitBrain, RibitMemoryDB | aiohttp.ClientSession (1), aiohttp.ClientTimeout (1), subprocess.Popen (2) |
| `newtermux_archive` | `ribit_termux_enhanced.py` | `support` | GemmaFallbackClient, GenerationResult, MockRibitModel, RibitBrain, RibitMemoryDB | aiohttp.ClientSession (1), aiohttp.ClientTimeout (1), subprocess.Popen (2) |
| `newtermux_archive` | `ribit_termux_ribit_compat.py` | `support` | CompatRibitBrain, CompatRibitTermuxBot, ExternalHooks, RibitCompatBridge | importlib.import_module (1), importlib.util.module_from_spec (1), importlib.util.spec_from_file_location (1) |
| `newtermux_archive` | `robotics_interface (1).py` | `actuation` | DeviceInfo, RoboticsInterface | — |
| `newtermux_archive` | `robotics_interface.py` | `actuation` | DeviceInfo, RoboticsInterface | — |
| `newtermux_archive` | `self_evaluation.py` | `support` | Evaluation, SelfEvaluation | — |
| `newtermux_archive` | `semantic_search.py` | `web` | SemanticSearch | — |
| `newtermux_archive` | `sqlite_storage.py` | `memory_learning` | SQLiteStorage | — |
| `newtermux_archive` | `storage_manager.py` | `memory_learning` | JsonStorage, StorageBackend, StorageManager | — |
| `newtermux_archive` | `system_monitor.py` | `support` | HealthSnapshot, SystemMonitor | — |
| `newtermux_archive` | `tensor_memory.py` | `memory_learning` | TensorMemory, TensorRecord | — |
| `newtermux_archive` | `thought_stream.py` | `cognition` | Thought, ThoughtStream | — |
| `newtermux_archive` | `tool_router.py` | `orchestration` | ToolInfo, ToolRouter | — |
| `newtermux_archive` | `web_search.py` | `web` | DummySearchProvider, MemoryCache, SearchProvider, SearchResult, WebSearch | — |
| `newtermux_archive` | `workflow_engine.py` | `orchestration` | WorkflowEngine, WorkflowStep | — |
| `newtermux_archive` | `working_memory.py` | `memory_learning` | WorkingMemory, WorkingMemoryItem | — |
| `ribit_2_0` | `__init__.py` | `support` | — | — |
| `ribit_2_0` | `advanced_mock_llm.py` | `model` | AdvancedMockLLM | — |
| `ribit_2_0` | `advanced_settings_manager.py` | `orchestration` | AdvancedSettingsManager | — |
| `ribit_2_0` | `agent.py` | `orchestration` | Ribit20Agent | — |
| `ribit_2_0` | `autonomous_matrix.py` | `transport` | AutonomousMatrixInteraction | — |
| `ribit_2_0` | `bridge_controller.py` | `policy_or_adapter` | BridgeController, BridgeMessage | execute (13) |
| `ribit_2_0` | `bridge_relay.py` | `policy_or_adapter` | BridgeRelay | — |
| `ribit_2_0` | `controller.py` | `actuation` | VisionSystemController | subprocess.run (2) |
| `ribit_2_0` | `conversation_manager.py` | `orchestration` | AdvancedConversationManager, ConversationMessage, ConversationSummary | — |
| `ribit_2_0` | `conversation_memory.py` | `memory_learning` | ConversationMemory | — |
| `ribit_2_0` | `conversational_mode.py` | `support` | ConversationalMode | — |
| `ribit_2_0` | `deltachat_bot.py` | `transport` | DeltaChatBotConfig, DeltaChatRibotBot | — |
| `ribit_2_0` | `deltachat_matrix_bridge.py` | `policy_or_adapter` | DeltaChatMatrixBridge | asyncio.create_task (1) |
| `ribit_2_0` | `dual_llm_pipeline.py` | `model` | DualLLMPipeline, EmotionalModule, IntellectualModule | — |
| `ribit_2_0` | `emoji_expression.py` | `support` | EmojiExpression | — |
| `ribit_2_0` | `enhanced_autonomous_matrix_bot.py` | `transport` | AsyncClient, EnhancedAutonomousMatrixBot, InviteMemberEvent, MatrixRoom, RoomMessageText | asyncio.create_task (1) |
| `ribit_2_0` | `enhanced_e2ee_integration.py` | `support` | E2EEConfig, EnhancedE2EEIntegration | — |
| `ribit_2_0` | `enhanced_emotions.py` | `cognition` | EmotionDefinition, EnhancedEmotionalIntelligence | — |
| `ribit_2_0` | `enhanced_matrix_integration.py` | `transport` | EnhancedMatrixIntegration | asyncio.create_task (2) |
| `ribit_2_0` | `enhanced_mock_llm.py` | `model` | EnhancedMockLLM | — |
| `ribit_2_0` | `enhanced_web_search.py` | `web` | EnhancedWebSearch | aiohttp.ClientSession (2), aiohttp.ClientTimeout (2) |
| `ribit_2_0` | `history_responder.py` | `model` | HistoryResponder | — |
| `ribit_2_0` | `humor_engine.py` | `support` | HumorEngine | — |
| `ribit_2_0` | `image_generation.py` | `media` | ImageGeneration | requests.get (1), requests.post (2) |
| `ribit_2_0` | `image_generator.py` | `media` | ImageGenerator | requests.get (1) |
| `ribit_2_0` | `image_provider.py` | `media` | FallbackImageProvider, ImageAnalysisProvider, OfflineImageProvider, WebAIImageProvider | aiohttp.ClientSession (2), aiohttp.ClientTimeout (2) |
| `ribit_2_0` | `integrated_secure_matrix_bot.py` | `transport` | IntegratedBotConfig, IntegratedSecureMatrixBot | — |
| `ribit_2_0` | `intelligent_responder.py` | `model` | IntelligentResponder | — |
| `ribit_2_0` | `jina_integration.py` | `web` | ConversationTracker, JinaSearchEngine | aiohttp.ClientSession (1), aiohttp.ClientTimeout (1) |
| `ribit_2_0` | `knowledge_base.py` | `memory_learning` | KnowledgeBase | — |
| `ribit_2_0` | `linguistics_engine.py` | `support` | LinguisticsEngine | — |
| `ribit_2_0` | `llm_wrapper.py` | `model` | Ribit20LLM | subprocess.Popen (1) |
| `ribit_2_0` | `matrix_bot.py` | `transport` | InviteMemberEvent, MatrixRoom, RibitMatrixBot, RoomMessageImage, RoomMessageText | asyncio.create_task (1) |
| `ribit_2_0` | `matrix_command_handler.py` | `transport` | MatrixCommandHandler | subprocess.run (16) |
| `ribit_2_0` | `matrix_e2ee_protocol.py` | `transport` | EncryptedMessage, EncryptionKeys, EncryptionLevel, MatrixE2EEProtocol, MessageType | — |
| `ribit_2_0` | `matrix_history_tracker.py` | `transport` | MatrixHistoryTracker | — |
| `ribit_2_0` | `matrix_image_sender.py` | `transport` | — | — |
| `ribit_2_0` | `megabite_llm.py` | `model` | MegabiteLLM | — |
| `ribit_2_0` | `message_history_learner.py` | `support` | AsyncClient, MessageHistoryLearner, RoomMessagesResponse | — |
| `ribit_2_0` | `mock_controller.py` | `actuation` | MockVisionSystemController | — |
| `ribit_2_0` | `mock_llm_wrapper.py` | `model` | MockRibit20LLM | — |
| `ribit_2_0` | `multi_language_system.py` | `support` | CodeExecutionResult, LanguageConfig, MultiLanguageSystem | compile_cmd.extend (4), subprocess.run (2) |
| `ribit_2_0` | `offline_image_analyzer.py` | `media` | OfflineImageAnalyzer | — |
| `ribit_2_0` | `philosophical_reasoning.py` | `cognition` | PhilosophicalReasoning | — |
| `ribit_2_0` | `programming_assistant.py` | `support` | ProgrammingAssistant | — |
| `ribit_2_0` | `reasoning_engine.py` | `cognition` | ReasoningEngine | — |
| `ribit_2_0` | `response_samples.py` | `support` | — | — |
| `ribit_2_0` | `ribit_offline_features_demo.py` | `support` | — | — |
| `ribit_2_0` | `ros_controller.py` | `actuation` | MockNode, MockPublisher, MockSubscription, RibitROSController, VisionSystemController | — |
| `ribit_2_0` | `secure_matrix_bot.py` | `transport` | AsyncClient, Event, LoginResponse, MatrixRoom, Olm | — |
| `ribit_2_0` | `self_testing_system.py` | `support` | CodeAnalysis, SelfTestingSystem, TestResult | exec (1), subprocess.run (11) |
| `ribit_2_0` | `task_autonomy.py` | `support` | Task, TaskAutonomy, TaskPriority, TaskStatus | — |
| `ribit_2_0` | `user_engagement.py` | `support` | UserEngagementSystem | — |
| `ribit_2_0` | `web_knowledge.py` | `web` | WebKnowledge | requests.get (3) |
| `ribit_2_0` | `web_scraping_wikipedia.py` | `web` | WebScrapingWikipedia | aiohttp.ClientSession (1), requests.get (2) |
| `ribit_2_0` | `word_learning_system.py` | `memory_learning` | WordLearningSystem | eval (2) |
| `ghostos_ribit_addon` | `examples/pixel_art/generate_samples.py` | `support` | — | — |
| `ghostos_ribit_addon` | `src/ribit_ghostos/__init__.py` | `support` | — | — |
| `ghostos_ribit_addon` | `src/ribit_ghostos/bridge.py` | `policy_or_adapter` | RibitGhostBridge | — |
| `ghostos_ribit_addon` | `src/ribit_ghostos/conversation.py` | `support` | ConversationTurn, GhostOSSimulationPartner, RibitConversationAdapter | — |
| `ghostos_ribit_addon` | `src/ribit_ghostos/ghostos_adapter.py` | `policy_or_adapter` | RibitMossGhostMethods | — |
| `ghostos_ribit_addon` | `src/ribit_ghostos/knowledge.py` | `memory_learning` | LocalKnowledgeStore | — |
| `ghostos_ribit_addon` | `src/ribit_ghostos/local_llm.py` | `model` | LocalEndpointError, LocalOpenAICompatibleClient | — |
| `ghostos_ribit_addon` | `src/ribit_ghostos/pixels.py` | `media` | PixelAnimation, PixelCanvas | — |
| `ghostos_ribit_addon` | `src/ribit_ghostos/policy.py` | `policy_or_adapter` | CapabilityPolicy, PermissionDenied | — |
| `ghostos_ribit_addon` | `src/ribit_ghostos/ribit_import.py` | `support` | RibitImportSummary, RibitKnowledgeImporter | — |
| `ghostos_ribit_addon` | `src/ribit_ghostos/structured_code.py` | `policy_or_adapter` | GeneratedModule, JsonToPythonCompiler, StructuredCodeError | — |
| `ghostos_ribit_addon` | `src/ribit_ghostos/word_learning.py` | `memory_learning` | WordLearningRegistry | — |
| `ghostos_ribit_addon` | `tests/test_ribit_ghostos.py` | `support` | — | compile_json (2) |
| `molequla` | `ariannamethod/__init__.py` | `support` | — | — |
| `molequla` | `ariannamethod/method.py` | `support` | AM_HarmonicResult, AM_MethodSteering, Method, Organism | — |
| `molequla` | `ariannamethod/sentinel.py` | `support` | FileChange, Sentinel, WatchedFile | — |
| `molequla` | `mycelium.py` | `support` | DriftTracker, FieldMonitor, FieldPulse, HarmonicNet, Mycelium | threading.Thread (1) |
| `molequla` | `standalone-py/molequla.py` | `support` | Config, CooccurField, DeltaAdapter, EvolvingTokenizer, GPT | asyncio.create_subprocess_exec (1), asyncio.create_task (1), threading.Lock (2) |

## Duplicate-content groups

The following table lists groups with two or more identical Python files. They are candidates for a single canonical implementation rather than a merge of copies.

| Content hash | Copies | Paths |
| --- | ---: | --- |
| `e3b0c44298fc` | 36 | `ghostos_core/common/src/ghostos_common/__init__.py`<br>`ghostos_core/ghostos/ghostos/actions/__init__.py`<br>`ghostos_core/ghostos/ghostos/contracts/__init__.py`<br>`ghostos_core/ghostos/ghostos/core/__init__.py`<br>`ghostos_core/ghostos/ghostos/core/models/__init__.py`<br>`ghostos_core/ghostos/ghostos/core/models/text_to_speech.py`<br>… plus 30 more |
| `5111ffc61caa` | 5 | `ghostos_core/ghostos/ghostos/prototypes/streamlitapp/tests/reports/alerts.py`<br>`ghostos_core/ghostos/ghostos/prototypes/streamlitapp/tests/reports/bugs.py`<br>`ghostos_core/ghostos/ghostos/prototypes/streamlitapp/tests/reports/dashboard.py`<br>`ghostos_core/ghostos/ghostos/prototypes/streamlitapp/tests/slider.py`<br>`ghostos_core/ghostos/ghostos/prototypes/streamlitapp/tests/tools/search.py` |
| `58836ba0aca3` | 2 | `newtermux_archive/agent_manager (1).py`<br>`newtermux_archive/agent_manager.py` |
| `af19670cb400` | 2 | `newtermux_archive/ribit_termux_enhanced (1).py`<br>`newtermux_archive/ribit_termux_enhanced.py` |
| `b2653c17ac02` | 2 | `newtermux_archive/robotics_interface (1).py`<br>`newtermux_archive/robotics_interface.py` |
