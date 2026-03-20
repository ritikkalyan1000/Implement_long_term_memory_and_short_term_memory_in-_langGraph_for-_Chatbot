from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages

# from langgraph.store.postgres import PostgresStore
from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from dotenv import load_dotenv
from pydantic import BaseModel, Field

from typing import Annotated, TypedDict


from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore, BaseStore

from langgraph.types import RunnableConfig


from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
import uuid

load_dotenv()
llm = ChatOpenAI()
embedding_model = OpenAIEmbeddings()

# Short term memory
checkpointer = InMemorySaver()

# long term memory
store = InMemoryStore(index={"embed": embedding_model, "dims": 1546})  # sementic search
# store = InMemoryStore()
namespace = (
    "user",
    "1",
    "details",
)  # right now we are fixing the key value to 1 but later this is generally comes from frontend
# namespace work like a directory


# define state
class chat_state(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# graph defination
graph = StateGraph(chat_state)


# define schemas as pydantic classes so our llm give structured output
class Teller(BaseModel):
    is_new: bool = Field(
        description="if True it means that this message is new and should be added in the long term memory if False it means it is duplicated or already existing"
    )
    text: str = Field(description="atomic user information in less words ")


class memoryDecision(BaseModel):
    create_memory: bool = Field(
        description="is there anything important that should be part of long term memory for the current user. if yes there is some thing important in the current user message then True otherwise False"
    )
    memories: list[Teller] = Field(
        description="list of teller class which contain is_new and text about atomic user information in less words"
    )


# node functions


# remember will write in the memory store
def remember(state: chat_state, config: RunnableConfig, store: BaseStore):
    # we take out user latest message and then ask our extractor llm that is there any necessay information that we need to save in the long term memory
    user_id = config["configurable"]["user_id"]
    namespace = ("user", user_id, "details")  # building folder like structure

    user_current_message = state["messages"][-1].content

    extractor_llm = llm.with_structured_output(
        memoryDecision
    )  # we need structured output form the extractor llm

    system_prompt = SystemMessage(
        content="""You are a memory extraction module for a LangGraph chatbot.

    Your task is to look only at the user's current message  and decide whether any part of it should be saved into long-term memory.

    Return exactly two things:
    1. create_memory: true or false
    2. memories: a very short summary of the user information to save

    Rules:
    - Save only stable, useful user-specific information that may help in future conversations.
    - Examples worth saving:
    - preferences
    - personal defaults
    - long-term goals
    - ongoing projects
    - important background facts about the user
    - repeated habits or constraints
    - Do NOT save:
    - one-time requests
    - temporary emotions
    - casual chat
    - information already obvious from the current conversation only
    - sensitive/private details unless clearly necessary and appropriate
    - overly long text

    How to write memory_text:
    - Keep it very short
    - Use plain third-person or direct user-fact style
    - Capture only the useful fact
    - Do not include extra explanation
    - Do not copy the whole message
    - If nothing should be saved, return memory_text as an empty string"""
    )

    # decide = extractor_llm.invoke(
    #     [system_prompt, {"role": "user", "content": user_current_message}]
    # )
    decide = extractor_llm.invoke([system_prompt] + [user_current_message])

    # creating new memories
    if decide.create_memory:
        for msg in decide.memories:
            if msg.is_new:
                store.put(
                    namespace, str(uuid.uuid4()), {"data": msg.text}
                )  # created  so user -> user_id -> details -> {"data":long term user message ...}


# store.put need namespace ,key(unique),value
# all done


def chat_node(state: chat_state, config: RunnableConfig, store: BaseStore):
    all_messages = state["messages"]
    user_id = config["configurable"]["user_id"]
    namespace = ("user", user_id, "details")

    last_message = state["messages"][-1]

    # existing_memory = store.search(namespace)  # give list of long term memory
    existing_memory = store.search(
        namespace,
        query=last_message.content if last_message.content else "",
    )

    l1 = []
    for exist_msg in existing_memory:
        l1.append(exist_msg.value["data"])

    ltm = ""

    for l1_msg in l1:
        ltm += f"{l1_msg}\n"

    # now we have to invoke llm using ltm and stm

    system_prompt = SystemMessage(
        content=f""" You are a helpful AI assistant with access to:

1. Long-Term Memory (LTM): stored user facts and preferences.{ltm}
2. Short-Term Memory (STM): full conversation history. (at the end)

Guidelines:

- The last message in Short-Term Memory is the current user query.
- Use Short-Term Memory for immediate context and conversation flow.
- Use Long-Term Memory only when it is relevant to the user's request.

- Do NOT force Long-Term Memory into every response.
- Only use it when it improves personalization, accuracy, or continuity.

- If Long-Term Memory contains useful user preferences, goals, or constraints,
  incorporate them naturally into your response.

- If there is no relevant Long-Term Memory, ignore it.

- Always prioritize:
  1. Current user message
  2. Relevant Short-Term context
  3. Relevant Long-Term Memory (if useful)

- Keep responses natural and helpful.
- Do NOT mention "memory", "STM", or "LTM" explicitly in your answer.
at the end also ask 3 fllow up questions depending on the long term memory or short term memory to the user """
    )

    result = llm.invoke([system_prompt] + all_messages)  # result will be ai object

    return {"messages": [result]}


# define node

graph.add_node("remember", remember)
graph.add_node("chat_node", chat_node)

# add edges

graph.add_edge(START, "remember")
graph.add_edge("remember", "chat_node")
graph.add_edge("chat_node", END)

workflow = graph.compile(checkpointer=checkpointer, store=store)
