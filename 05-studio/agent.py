import os
from langchain_openai import AzureChatOpenAI
from langchain.prompts import ChatPromptTemplate

# Setup Azure OpenAI model


llm = AzureChatOpenAI(
    azure_deployment="gpt-4o",
    api_version="2024-02-01",
    temperature=0
)

#Real-time example tools: Shopping Cart with Indian prices

def check_price(item: str) -> float:
    """Check the price of an item in the store (in INR).

    Args:
        item: name of the item (e.g., 'apple', 'milk')

    Returns:
        Price of the item in INR
    """
    prices_inr = {
        "apple": 30.0,      # ₹30 per apple
        "milk": 60.0,       # ₹60 per litre
        "bread": 40.0,      # ₹40 per loaf
        "chocolate": 100.0  # ₹100 per bar
    }
    return prices_inr.get(item.lower(), 0.0)


def add_to_cart(item: str, quantity: int) -> str:
    """Add an item to the cart with given quantity.

    Args:
        item: name of the item
        quantity: number of items to add

    Returns:
        Confirmation message
    """
    return f"Added {quantity} x {item} to your cart."


def calculate_total(prices: list[float]) -> str:
    """Calculate total bill in INR.

    Args:
        prices: list of item prices

    Returns:
        Total price formatted in INR
    """
    total = sum(prices)
    return f"Total bill: ₹{total:.2f}"


# --- Bind tools to LLM ---
tools = [check_price, add_to_cart, calculate_total]

llm_with_tools = llm.bind_tools(tools)


from IPython.display import Image, display

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

# System message (updated for shopping agent)
sys_msg = SystemMessage(content="You are a helpful shopping agent that helps users check prices, add items to their cart, and calculate the total bill in INR.")

# Node
def agent(state: MessagesState):
    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

# Graph
builder = StateGraph(MessagesState)

# Define nodes: these do the work
builder.add_node("agent", agent)
builder.add_node("tools", ToolNode(tools))

# Define edges: these determine the control flow
builder.add_edge(START, "agent")
builder.add_conditional_edges(
    "agent",
    # If the latest message (result) from agent is a tool call -> tools_condition routes to tools
    # If the latest message (result) from agent is a not a tool call -> tools_condition routes to END
    tools_condition,
)
builder.add_edge("tools", "agent")

graph = builder.compile()
