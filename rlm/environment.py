from __future__ import annotations

from dataclasses import dataclass
import re
from textwrap import shorten
from typing import Callable, Optional
from repl import REPL



@dataclass
class ExecutionResult:
    ok: bool
    stdout: str
    stderr: str
    error: Optional[str] = None



class RLMEnvironment:
    def __init__(self, prompt: str, sub_rlm: Optional[Callable[[str], str]] = None):
        self.prompt = prompt
        self.repl = REPL()
        self.repl.ns["context"] = prompt
        if sub_rlm:
            self.repl.ns["sub_rlm"] = sub_rlm
        self._code: str = ""
        self._stdout_tail: str = ""
        self._stderr_tail: str = ""


    def reset_prompt(self, prompt: str) -> None:
        self.prompt = prompt
        self.repl.ns["context"] = prompt


    def run(self, code: str) -> ExecutionResult:
        raw = self.repl.run_cell(code)
        stdout, stderr = raw.get("stdout", ""), raw.get("stderr", "")
        self._stdout_tail = stdout[-512:]
        self._stderr_tail = stderr[-256:]
        self._code = code
        return ExecutionResult(
            ok=raw.get("ok", False),
            stdout=stdout,
            stderr=stderr,
            error=raw.get("error"),
        )


    def extract_final(self, text: str) -> Optional[str]:
        match = re.search(r'FINAL\s*\((.*?)\)', text, re.DOTALL)
        return match.group(1).strip() if match else None


    @property
    def final_value(self) -> Optional[str]:
        value = self.repl.ns.get("__final_answer__")
        if value in (None, ""):
            return None
        return value


    def metadata_snapshot(self) -> str:
        prompt_head = shorten(self.prompt, width=120, placeholder="...")
        final_state = "set" if self.final_value else "unset"
        return (
            f"<user_prompt_metadata prompt_len={len(self.prompt)} final={final_state} "
            f"last_code_ran=\"{self._repr_fragment(self._code)}\" "
            f"stdout_tail=\"{self._repr_fragment(self._stdout_tail)}\" "
            f"stderr_tail=\"{self._repr_fragment(self._stderr_tail)}\" "
            f"prompt_head=\"{self._repr_fragment(prompt_head)}\">"
        )


    @staticmethod
    def _repr_fragment(value: str) -> str:
        safe = value.replace("\n", " ")
        return shorten(safe, width=60, placeholder="…")