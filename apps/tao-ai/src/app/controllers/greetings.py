from dataclasses import dataclass
from blacksheep.server.controllers import Controller, get


@dataclass
class Sentence:
    text: str
    url: str


@dataclass
class HelloModel:
    name: str
    sentences: list[Sentence]


class Greetings(Controller):

    @get("/hello-view")
    def hello(self):
        return self.view(
            model=HelloModel(
                "World!",
                sentences=[
                    Sentence(
                        "Check this out!",
                        "https://github.com/RobertoPrevato/BlackSheep",
                    )
                ],
            )
        )
