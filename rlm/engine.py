from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .config import RLMConfig
from .environment import RLMEnvironment
from .llm import LLMBackend, LLMPrompt
from prompts import BASE_PROMPT


@dataclass
class IterationTrace:
    iteration: int
    message: str
    code: str
    exec_ok: bool
    exec_error: Optional[str] = None


@dataclass
class RecursiveLanguageModel:

    def __init__(self, prompt: str) -> None:
        self.backend: LLMBackend = LLMBackend()
        self.config: RLMConfig = RLMConfig
        self.system_prompt: str = BASE_PROMPT.strip()
        
        self.env = RLMEnvironment(prompt, sub_rlm=lambda p: self.run(p))
        self.history: List[Dict] = [
            {
                "role": "system", 
                "content": BASE_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ]
        self.traces: List[IterationTrace] = []

    def reset_answer(self) -> None:
        self.env.repl

    def reset_prompt(self, prompt: str) -> None:
        self.env.reset_prompt(prompt)
        self.system_prompt: str = BASE_PROMPT.strip() #.format(
        #     context_total_length=len(prompt)
        # )

    def run(self) -> str:
        for iteration in range(self.config.max_iterations):
            # print(f"History: {history}")
            response = self.backend.generate(LLMPrompt(history=self.history))
            if response.message:
                print(f"> Message:\n{response.message}")
            if response.code:
                print(f"> Running:\n{response.code}")
            exec_result = self.env.run(response.code)
            if response.code:
                # print(f"> Code running complete.\n{exec_result}")
                print(f"> Code running complete.")
            print("----------------------------------------------------------------------------------------")
            self.traces.append(
                IterationTrace(
                    iteration=iteration,
                    message=response.message,
                    code=response.code,
                    exec_ok=exec_result.ok,
                    exec_error=exec_result.error,
                )
            )
            if response.message:
                self.history.append({
                    "role": "assistant",
                    "content": response.message
                })
            if response.code:
                self.history.append(response.ai_msg_data)
                self.history.append({
                    "role": "tool",
                    "tool_call_id": response.tool_id,
                    "content": self.env.metadata_snapshot()
                })
            else:
                self.history.append({
                    "role": "system",
                    "content": self.env.metadata_snapshot()
                })

            final_value = self.env.final_value
            if final_value is not None:
                return str(final_value)

        raise RuntimeError(
            "RLM terminated without FINAL value after "
            f"{self.config.max_iterations} iterations."
        )
