from setuptools import setup, find_packages, Extension
import pybind11

ext_modules = [
    Extension(
        "kylin.metrics.lib_rel",
        ["kylin/metrics/lib_rel.cpp"],
        include_dirs=[pybind11.get_include()],
        language="c++",
    ),
]


setup(
    name="Librarian",
    version="0.0.1",
    author="Zhuocheng Zhang",
    author_email="zhuocheng_zhang@163.com",
    description="A package for information retrieval",
    packages=find_packages(),
    install_requires=[
        "pandas",
        "numpy",
        "transformers>=4.41.0",
        "tqdm",
        "elasticsearch>=8.14.0",
        "torch>=2.3.0",
        "sacrebleu>=2.4.2",
        "rouge",
        "unidecode",
        "vllm>=0.5.0",
        "cachetools",
        "tenacity",
        "tables",
        "hydra-core>=1.3",
        "omegaconf>=2.3.0",
    ],
    extras_require={
        "all": [
            "openai>=1.30.1",
            "ollama>=0.2.1",
            "faiss>=1.8.0",
            "scann>=1.3.2",
            "pymilvus>=2.4.3",
            "duckduckgo_search>=6.1.6",
            "PySocks>=1.7.1",
        ]
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    ext_modules=ext_modules,
)
