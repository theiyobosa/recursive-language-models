"""Configuration objects for Recursive Language Models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Sequence, TYPE_CHECKING


MetadataFormatter = Callable[["RLMEnvironment"], str]

if TYPE_CHECKING:
    from .environment import RLMEnvironment


def _default_formatters() -> Sequence[MetadataFormatter]:
    return (lambda env: env.metadata_snapshot(),)


@dataclass
class RLMConfig:
    max_iterations: int = 10 # 128
    max_stdout_chars: int = 2_048
    metadata_formatters: Sequence[MetadataFormatter] = field(
        default_factory=_default_formatters
    )

    def iter_metadata(self, env: "RLMEnvironment") -> Sequence[str]:
        for formatter in self.metadata_formatters:
            yield formatter(env)
