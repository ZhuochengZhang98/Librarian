import logging
from dataclasses import dataclass
from omegaconf import MISSING

from kylin.prompt import ChatPrompt
from kylin.utils import TimeMeter

from .model_base import Generators, GeneratorBase, GeneratorBaseConfig, GenerationConfig


logger = logging.getLogger("OllamaGenerator")


@dataclass
class OllamaGeneratorConfig(GeneratorBaseConfig):
    model_name: str = MISSING
    base_url: str = MISSING
    verbose: bool = False


@Generators("ollama", config_class=OllamaGeneratorConfig)
class OllamaGenerator(GeneratorBase):
    def __init__(self, cfg: OllamaGeneratorConfig) -> None:
        from ollama import Client

        self.client = Client(host=cfg.base_url)
        self.model_name = cfg.model_name
        if not cfg.verbose:
            logger = logging.getLogger("httpx")
            logger.setLevel(logging.WARNING)
        self._check()
        return

    @TimeMeter("ollama_generate")
    def chat(
        self,
        prompts: list[ChatPrompt],
        generation_config: GenerationConfig = GenerationConfig(),
    ) -> list[list[str]]:
        responses: list[list[str]] = []
        options = self._get_options(generation_config)
        for prompt in prompts:
            # as ollama does not support sample_num, we sample multiple times
            prompt = prompt.to_list()
            responses.append([])
            for _ in range(generation_config.sample_num):
                response = self.client.chat(
                    model=self.model_name,
                    messages=prompt,
                    options=options,
                )
                responses[-1].append(response["message"]["content"])
        return responses

    @TimeMeter("ollama_generate")
    def generate(
        self,
        prefixes: list[str],
        generation_config: GenerationConfig = GenerationConfig(),
    ) -> list[list[str]]:
        responses: list[list[str]] = []
        options = self._get_options(generation_config)
        for prefix in prefixes:
            # as ollama does not support sample_num, we sample multiple times
            responses.append([])
            for _ in range(generation_config.sample_num):
                response = self.client.generate(
                    model=self.model_name,
                    prompt=prefix,
                    raw=True,
                    options=options,
                )
                responses[-1].append(response["message"]["content"])
        return responses

    def _get_options(self, generation_config: GenerationConfig) -> dict:
        return {
            "top_k": generation_config.top_k,
            "top_p": generation_config.top_p,
            "temperature": generation_config.temperature,
            "num_predict": generation_config.max_new_tokens,
        }

    def _check(self) -> None:
        models = [i["name"] for i in self.client.list()["models"]]
        if self.model_name not in models:
            raise ValueError(f"Model {self.model_name} not found in {models}")
        return
