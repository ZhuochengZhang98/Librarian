from argparse import ArgumentParser, Namespace
from .retriever_base import Retriever, LocalRetriever
from .bm25_retriever import BM25Retriever
from .dense_retriever import DenseRetriever
from .web_retriever import DuckDuckGoRetriever


def add_args_for_retriever(parser: ArgumentParser) -> ArgumentParser:
    parser.add_argument(
        "--retriever_type",
        type=str,
        nargs="+",
        default=["bm25"],
        choices=["bm25", "ddg", "dense"],
        help="The retrievers to use",
    )
    parser = Retriever.add_args(parser)
    parser = LocalRetriever.add_args(parser)
    parser = BM25Retriever.add_args(parser)
    parser = DenseRetriever.add_args(parser)
    parser = DuckDuckGoRetriever.add_args(parser)
    return parser


def load_retrievers(args: Namespace) -> list[Retriever]:
    retrievers = []
    for ret_type in args.retriever_type:
        match ret_type:
            case "bm25":
                retrievers.append(BM25Retriever(args))
            case "ddg":
                retrievers.append(DuckDuckGoRetriever(args))
            case "dense":
                retrievers.append(DenseRetriever(args))
            case _:
                raise ValueError(f"Invalid retriever type: {args.retriever_type}")
    return retrievers