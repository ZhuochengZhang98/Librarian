import hydra
from hydra.core.config_store import ConfigStore
from omegaconf import OmegaConf

from librarian.retriever import DenseRetriever, DenseRetrieverConfig
from librarian.utils import LOGGER_MANAGER

logger = LOGGER_MANAGER.get_logger("librarian.rebuild_index")


cs = ConfigStore.instance()
cs.store(name="default", node=DenseRetrieverConfig)


@hydra.main(version_base="1.3", config_path=None, config_name="default")
def main(cfg: DenseRetrieverConfig):
    default_cfg = OmegaConf.structured(DenseRetrieverConfig)
    cfg = OmegaConf.merge(default_cfg, cfg)

    # rebuild index
    retriever = DenseRetriever(
        cfg, no_check=True
    )  # do not check the index-retriever consistency
    retriever.build_index()
    return


if __name__ == "__main__":
    main()