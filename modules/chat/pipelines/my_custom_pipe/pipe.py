from typing import List, Union
from pydantic import BaseModel


class Piper:
    """
    A simple example of a pipe.
    """

    class Valves(BaseModel):
        pass

    def __init__(self):
        pass

    async def pipe(self, body: dict, __user__: dict) -> Union[str, List[dict]]:
        """
        A simple pipe that returns a static message.
        """
        return "Hello from my_custom_pipe!"
