from __future__ import annotations
from dataclasses import dataclass, field
from typing import Callable, Generator, Sequence, TYPE_CHECKING



MetadataFormatter = Callable[["RLMEnvironment"], str]


if TYPE_CHECKING:
    from .environment import RLMEnvironment


def _default_formatters() -> Sequence[MetadataFormatter]:
    return (lambda env: env.metadata_snapshot(),)



@dataclass
class RLMConfig:

    def __init__(self, max_iterations: int) -> None:
        self.max_iterations: int = max_iterations
        self.max_stdout_chars: int = 2_048
        self.metadata_formatters: Sequence[MetadataFormatter] = field(
            default_factory=_default_formatters
        )


    def iter_metadata(self, env: "RLMEnvironment") -> Generator[str]:
        for formatter in self.metadata_formatters:
            yield formatter(env)
