from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

import numpy as np

from kylin.retriever import RetrievedContext
from kylin.utils import Register


Rankers = Register("Rankers")


@dataclass
class RankerConfig:
    reserve_num: int = -1


@dataclass
class RankingResult:
    query: str
    candidates: list[RetrievedContext]
    scores: Optional[list[float]] = None


class RankerBase(ABC):
    def __init__(self, cfg: RankerConfig) -> None:
        self.reserve_num = cfg.reserve_num
        return

    def rank(
        self, query: str, candidates: list[RetrievedContext | str]
    ) -> RankingResult:
        if isinstance(candidates[0], RetrievedContext):
            texts = [ctx.full_text for ctx in candidates]
        else:
            texts = candidates
        indices, scores = self._rank(query, texts)
        if indices is None:
            assert scores is not None
            indices = np.argsort(scores)[::-1]
        if self.reserve_num > 0:
            indices = indices[: self.reserve_num]

        result = RankingResult(query=query, candidates=[])
        for idx in indices:
            result.candidates.append(candidates[idx])
        if scores is not None:
            result.scores = [scores[idx] for idx in indices]
        return result

    @abstractmethod
    def _rank(self, query: str, candidates: list[str]) -> tuple[np.ndarray, np.ndarray]:
        """Rank the candidates based on the query.

        Args:
            query (str): query string.
            candidates (list[str]): list of candidate strings.

        Returns:
            tuple[np.ndarray, np.ndarray]: indices and scores of the ranked candidates.
        """
        return