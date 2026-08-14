# Ribit Termux Test Run

| Field | Value |
| --- | --- |
| Started (UTC) | 2026-08-14T03:46:06Z |
| Git revision | 6ec45f6 |
| Python | Python 3.12.3 |

```text
$ python3 -m compileall -q ribit_termux vendor ribit_termux.py
$ python3 -m unittest discover -s tests -v
test_high_impact_capabilities_are_denied_by_default (test_core.CapabilityPolicyTests.test_high_impact_capabilities_are_denied_by_default) ... ok
test_automation_style_prompt_is_refused_before_provider_execution (test_core.EngineTests.test_automation_style_prompt_is_refused_before_provider_execution) ... ok
test_cognitive_runtime_builds_local_semantic_context_and_text_plan (test_core.EngineTests.test_cognitive_runtime_builds_local_semantic_context_and_text_plan) ... ok
test_local_mode_returns_safe_availability_message (test_core.EngineTests.test_local_mode_returns_safe_availability_message) ... ok
test_mock_provider_and_memory_are_local (test_core.EngineTests.test_mock_provider_and_memory_are_local) ... ok
test_linguistic_analysis_tracks_bounded_sender_style (test_core.LinguisticAndWorkingMemoryTests.test_linguistic_analysis_tracks_bounded_sender_style) ... ok
test_working_memory_evicts_low_importance_entries (test_core.LinguisticAndWorkingMemoryTests.test_working_memory_evicts_low_importance_entries) ... ok
test_command_parser_only_accepts_question_mark_commands (test_core.MatrixTransportTests.test_command_parser_only_accepts_question_mark_commands) ... ok
test_matrix_transport_dependency_is_available (test_core.MatrixTransportTests.test_matrix_transport_dependency_is_available) ... ok
test_mock_returns_text_and_retains_raw_decision_as_data (test_core.MockProviderTests.test_mock_returns_text_and_retains_raw_decision_as_data) ... ok
test_extracts_known_text_without_executing_anything (test_core.TextOnlyAdapterTests.test_extracts_known_text_without_executing_anything) ... ok
test_refuses_non_text_action_plan (test_core.TextOnlyAdapterTests.test_refuses_non_text_action_plan) ... ok
test_rejects_non_loopback_local_llm (test_core.TextOnlyAdapterTests.test_rejects_non_loopback_local_llm) ... ok

----------------------------------------------------------------------
Ran 13 tests in 0.035s

OK
$ python3 ribit_termux.py --self-test
2026-08-14 03:46:07,746 INFO vendor.ribit_2_0.knowledge_base: KnowledgeBase file created: /tmp/ribit-termux-self-test-2un5ccgt/mock_knowledge.txt
2026-08-14 03:46:07,746 INFO vendor.ribit_2_0.mock_llm_wrapper: Enhanced Mock Ribit 2.0 LLM initialized for production use
2026-08-14 03:46:07,746 INFO vendor.ribit_2_0.knowledge_base: Knowledge not found for key: identity
2026-08-14 03:46:07,746 INFO vendor.ribit_2_0.knowledge_base: Knowledge not found for key: purpose
2026-08-14 03:46:07,746 INFO vendor.ribit_2_0.knowledge_base: Knowledge not found for key: core_capabilities
2026-08-14 03:46:07,746 INFO vendor.ribit_2_0.knowledge_base: Knowledge not found for key: personality_summary
2026-08-14 03:46:07,749 INFO vendor.ribit_2_0.knowledge_base: Stored knowledge: [query_1] = Explain the safe local memory workflow.
2026-08-14 03:46:07,749 INFO vendor.ribit_2_0.mock_llm_wrapper: LLM Decision: type_text('As an AI, I experience something when processing information, but whether it's 'consciousness' is debatable...')
press_key('enter')
store_knowledge('thoughtful_response_given', 'true')
goal_achieved:Provided contextual response (from 150 diverse samples)
MODEL: ribit-2.0-mock
REPLY: As an AI, I experience something when processing information, but whether it's 'consciousness' is debatable...
STATUS: messages=3; facts=0; words=20; cognitive_records=3; provider=mock; local_llm=disabled; mock_fallback=ready
RAW_ACTION_PLAN: recorded as data only; not executed
$ git diff --check
```

**Result:** PASS

| Field | Value |
| --- | --- |
| Finished (UTC) | 2026-08-14T03:46:07Z |
| Exit status | 0 |
