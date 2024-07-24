import logging
import os
from copy import deepcopy
from dataclasses import dataclass, field

from kylin.prompt import ChatTurn, ChatPrompt
from kylin.retriever import DenseRetriever, DenseRetrieverConfig

from .searcher import BaseSearcher, SearcherConfig


logger = logging.getLogger("WebSearcher")


@dataclass
class DenseSearcherConfig(SearcherConfig):
    retriever_config: DenseRetrieverConfig = field(default_factory=DenseRetrieverConfig)
    rewrite_query: bool = False
    retriever_top_k: int = 10
    disable_cache: bool = False


class DenseSearcher(BaseSearcher):
    def __init__(self, cfg: DenseSearcherConfig) -> None:
        super().__init__(cfg)
        # setup Dense Searcher
        self.rewrite = cfg.rewrite_query
        self.feedback_depth = cfg.feedback_depth
        self.summary_context = cfg.summarize_context
        self.retriever_top_k = cfg.retriever_top_k
        self.disable_cache = cfg.disable_cache

        # load Dense Retrieve
        self.retriever = DenseRetriever(cfg.retriever_config)

        # load prompt
        self.rewrite_prompt = ChatPrompt.from_file(
            os.path.join(
                os.path.dirname(__file__),
                "searcher_prompts",
                "dense_rewrite_prompt.json",
            )
        )
        return

    def search(
        self, question: str
    ) -> tuple[list[dict[str, str]], list[dict[str, object]]]:
        if self.rewrite:
            query_to_search = self.rewrite_query(question)
        else:
            query_to_search = question
        ctxs = self.retriever.search(
            query=[query_to_search],
            top_k=self.retriever_top_k,
            disable_cache=self.disable_cache,
        )[0]
        return ctxs, []

    def rewrite_query(self, info: str) -> str:
        # Rewrite the query to be more informative
        user_prompt = f"Query: {info}"
        prompt = deepcopy(self.rewrite_prompt)
        prompt.update(ChatTurn(role="user", content=user_prompt))
        query = self.agent.chat([prompt], generation_config=self.gen_cfg)[0][0]
        return query

    def close(self) -> None:
        self.retriever.close()
        return