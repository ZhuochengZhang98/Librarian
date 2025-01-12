from copy import deepcopy
from dataclasses import dataclass
from typing import Optional

from flexrag.prompt import ChatTurn, ChatPrompt
from flexrag.models import GenerationConfig, GENERATORS
from flexrag.utils import LOGGER_MANAGER, Choices

from .assistant import AssistantBase, ASSISTANTS

logger = LOGGER_MANAGER.get_logger("flexrag.assistant")


GeneratorConfig = GENERATORS.make_config()


@dataclass
class BasicAssistantConfig(GeneratorConfig, GenerationConfig):
    """The configuration for the basic assistant.

    :param response_type: The type of response to generate.
        Defaults to "short". Available options are: "short", "long", "original".
    :type response_type: str, optional
    :param prompt_path: The path to the prompt file. Defaults to None.
    :type prompt_path: str, optional
    :param use_history: Whether to use history prompt. Defaults to False.
    :type use_history: bool, optional
    """

    response_type: Choices(["short", "long", "original"]) = "short"  # type: ignore
    prompt_path: Optional[str] = None
    use_history: bool = False


@ASSISTANTS("basic", config_class=BasicAssistantConfig)
class BasicAssistant(AssistantBase):
    """A basic assistant that generates response without retrieval."""

    def __init__(self, cfg: BasicAssistantConfig):
        # set basic args
        self.gen_cfg = cfg
        if self.gen_cfg.sample_num > 1:
            logger.warning("Sample num > 1 is not supported for Assistant")
            self.gen_cfg.sample_num = 1

        # load generator
        self.generator = GENERATORS.load(cfg)

        # load prompts
        if cfg.prompt_path is not None:
            self.prompt = ChatPrompt.from_json(cfg.prompt_path)
        else:
            self.prompt = ChatPrompt()
        if cfg.use_history:
            self.history_prompt = deepcopy(self.prompt)
        else:
            self.history_prompt = None
        return

    def answer(self, question: str) -> tuple[str, None, dict[str, ChatPrompt]]:
        # prepare system prompt
        if self.history_prompt is not None:
            prompt = deepcopy(self.history_prompt)
        else:
            prompt = deepcopy(self.prompt)

        prompt.update(ChatTurn(role="user", content=question))

        # generate response
        response = self.generator.chat([prompt], generation_config=self.gen_cfg)[0][0]

        # update history prompt
        if self.history_prompt is not None:
            self.history_prompt.update(ChatTurn(role="user", content=question))
            self.history_prompt.update(ChatTurn(role="assistant", content=response))
        return response, None, {"prompt": prompt}

    def clear_history(self) -> None:
        if self.history_prompt is not None:
            self.history_prompt = deepcopy(self.prompt)
        return
