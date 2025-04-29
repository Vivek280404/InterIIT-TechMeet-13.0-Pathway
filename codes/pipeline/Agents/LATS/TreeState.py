from typing_extensions import TypedDict
from Agents.LATS.Reflection import Node

class TreeState(TypedDict):
    # The full tree
    root: Node
    # The original input
    input: str