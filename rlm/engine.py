from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from colorama import Fore, Style, init
from .config import RLMConfig
from .environment import RLMEnvironment
from .llm import LLMBackend, LLMPrompt
from prompts import BASE_PROMPT



init(autoreset=True)



@dataclass
class IterationTrace:
    iteration: int
    message: str
    code: str
    exec_ok: bool
    exec_error: Optional[str] = None



@dataclass
class RecursiveLanguageModel:

    def __init__(
        self, 
        prompt: str, 
        model_provider: str,
        model_api_key: str,
        model_name: str,
        max_iterations: int
    ) -> None:
        self.backend: LLMBackend = LLMBackend(
            model_provider=model_provider,
            model_api_key=model_api_key, 
            model_name=model_name
        )
        self.config: RLMConfig = RLMConfig(max_iterations=max_iterations)
        self.system_prompt: str = BASE_PROMPT.strip()
        
        self.env = RLMEnvironment(prompt, sub_rlm=lambda p: self.run(p))
        self.history: List[Dict] = []
        self.traces: List[IterationTrace] = []


    def reset_answer(self) -> None:
        self.env.repl


    def reset_prompt(self, prompt: str) -> None:
        self.env.reset_prompt(prompt)
        self.system_prompt: str = BASE_PROMPT.strip().format(
            context_total_length=len(prompt)
        )
        if not self.history:
            self.history.append({
                "role": "system",
                "content": self.system_prompt
            })
        else:
            self.history.append({
                "role": "system",
                "content": f"User has changed the 'context', it now contains {len(prompt)} chars."
            })


    def run(self) -> Tuple[bool, str]:
        for iteration in range(self.config.max_iterations):
            print(
                f"\n{Style.BRIGHT}{Fore.CYAN}"
                f"{'='*20} ITERATION {iteration+1} {'='*20}"
            )

            response = self.backend.generate(LLMPrompt(history=self.history))

            if response.message:
                print(f"\n{Fore.BLUE}{Style.BRIGHT}🧠 Message:")
                print(f"{Fore.WHITE}{response.message}")

            if response.code:
                print(f"\n{Fore.YELLOW}{Style.BRIGHT}⚙ Running Code:")
                print(f"{Fore.YELLOW}{response.code}")

            # if response.content:
            #     print(f"\n{Fore.MAGENTA}{Style.BRIGHT}📦 Raw Content:")
            #     print(f"{Fore.WHITE}{response.content}")

            exec_result = self.env.run(response.code)

            if response.code:
                if exec_result.ok:
                    print(f"\n{Fore.GREEN}✅ Code executed successfully.")
                else:
                    print(f"\n{Fore.RED}❌ Code execution failed.")
                    if exec_result.error:
                        print(f"{Fore.RED}{exec_result.error}")

            self.traces.append(
                IterationTrace(
                    iteration=iteration,
                    message=response.message,
                    code=response.code,
                    exec_ok=exec_result.ok,
                    exec_error=exec_result.error,
                )
            )

            if response.content:
                self.history.append({
                    "role": "assistant",
                    "content": response.content
                })

            if response.is_code:
                self.history.append({
                    "role": "system",
                    "content": self.env.metadata_snapshot()
                })

            final_value = self.env.extract_final(response.content)
            if final_value is not None:
                # print(
                #     f"\n{Style.BRIGHT}{Fore.GREEN}"
                #     f"{'='*20} FINAL DETECTED {'='*20}"
                # )
                # print(f"{Fore.GREEN}{Style.BRIGHT}{final_value}")
                # print(f"{Fore.GREEN}{'='*60}\n")
                return True, str(final_value)

        return (
            False,
            f"❌ RLM terminated without FINAL result after {self.config.max_iterations} iterations."
        )