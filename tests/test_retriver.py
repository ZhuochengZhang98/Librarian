import os
import tempfile
import uuid
from dataclasses import dataclass, field

import pytest
from omegaconf import OmegaConf

from flexrag.datasets import RAGCorpusDataset, RAGCorpusDatasetConfig
from flexrag.retriever import (
    BM25SRetriever,
    BM25SRetrieverConfig,
    DenseRetriever,
    DenseRetrieverConfig,
    ElasticRetriever,
    ElasticRetrieverConfig,
    TypesenseRetriever,
    TypesenseRetrieverConfig,
)


@dataclass
class RetrieverTestConfig(RAGCorpusDatasetConfig):
    file_paths: list[str] = field(
        default_factory=lambda: [
            os.path.join(os.path.dirname(__file__), "testcorp", "testcorp.jsonl")
        ]
    )
    typesense_config: TypesenseRetrieverConfig = field(default_factory=TypesenseRetrieverConfig)  # fmt: skip
    bm25s_config: BM25SRetrieverConfig = field(default_factory=BM25SRetrieverConfig)
    elastic_config: ElasticRetrieverConfig = field(default_factory=ElasticRetrieverConfig)  # fmt: skip
    dense_config: DenseRetrieverConfig = field(default_factory=DenseRetrieverConfig)


@pytest.fixture
def setup_elastic():
    TestRetrievers.cfg.elastic_config.index_name = str(uuid.uuid4())
    retriever = ElasticRetriever(TestRetrievers.cfg.elastic_config)
    yield retriever
    retriever.clean()
    return


@pytest.fixture
def setup_typesense():
    TestRetrievers.cfg.typesense_config.index_name = str(uuid.uuid4())
    retriever = TypesenseRetriever(TestRetrievers.cfg.typesense_config)
    yield retriever
    retriever.clean()
    return


class TestRetrievers:
    cfg: RetrieverTestConfig = OmegaConf.merge(
        OmegaConf.structured(RetrieverTestConfig),
        OmegaConf.load(
            os.path.join(os.path.dirname(__file__), "configs", "retriever.yaml")
        ),
    )
    query = [
        "Who is Bruce Wayne?",
        "What is the capital of China?",
    ]

    def test_dense_retriever(self):
        with tempfile.TemporaryDirectory() as tempdir:
            # load retriever
            self.cfg.dense_config.database_path = tempdir
            retriever = DenseRetriever(self.cfg.dense_config)

            # build index
            corpus = RAGCorpusDataset(self.cfg)
            retriever.add_passages(corpus)

            # search
            r = retriever.search(self.query, disable_cache=True)
            assert len(r) == 2
            assert len(r[0]) == 10
            assert len(r[1]) == 10
        return

    def test_bm25s_retriever(self):
        with tempfile.TemporaryDirectory() as tempdir:
            # load retriever
            self.cfg.bm25s_config.database_path = tempdir
            retriever = BM25SRetriever(self.cfg.bm25s_config)

            # build index
            corpus = RAGCorpusDataset(self.cfg)
            retriever.add_passages(corpus)

            # search
            r = retriever.search(self.query, disable_cache=True)
            assert len(r) == 2
            assert len(r[0]) == 10
            assert len(r[1]) == 10
        return

    def test_elastic_retriever(self, setup_elastic):
        # load retriever
        retriever: ElasticRetriever = setup_elastic

        # build index
        corpus = RAGCorpusDataset(self.cfg)
        retriever.add_passages(corpus)

        # search
        r = retriever.search(self.query, disable_cache=True)
        assert len(r) == 2
        assert len(r[0]) == 10
        assert len(r[1]) == 10
        return

    def test_typesense_retriever(self, setup_typesense):
        # load retriever
        retriever: TypesenseRetriever = setup_typesense

        # build index
        corpus = RAGCorpusDataset(self.cfg)
        retriever.add_passages(corpus)

        # search
        r = retriever.search(self.query, disable_cache=True)
        assert len(r) == 2
        return
