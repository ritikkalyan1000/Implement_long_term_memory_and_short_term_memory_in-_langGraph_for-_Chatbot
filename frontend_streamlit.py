import streamlit as st
from backend import workflow
from langchain_core.messages import HumanMessage
import uuid


# --------------------------------------- utility functions--------------------------------


def generate_thread_id():
    return uuid.uuid4()


def add_thread_id(thread_id):
    if thread_id not in st.session_state["chat_thread"]:
        st.session_state["chat_thread"].append(thread_id)


def reset_chat():
    st.session_state["message_history"] = []


def load_conversation(thread_id):
    state = workflow.get_state({"configurable": {"thread_id": thread_id}})
    messages = state.values.get(
        "messages", []
    )  # if we have chat then show chats otherwise empty list means no interactions

    temp_messages = []
    for msg in messages:
        if isinstance(msg, HumanMessage):
            role = "user"
        else:
            role = "assistant"

        temp_messages.append({"role": role, "content": msg.content})

    st.session_state["message_history"] = temp_messages


# ------------------------------ session state --------------------------------------------
if "message_history" not in st.session_state:
    st.session_state["message_history"] = []

if "thread_id" not in st.session_state:
    st.session_state["thread_id"] = (
        generate_thread_id()
    )  #  now when the page load first time we always have a thread id


if "chat_thread" not in st.session_state:
    st.session_state["chat_thread"] = []

add_thread_id(
    st.session_state["thread_id"]
)  # add thread id to the chat thread list if not exist already


# --------------------------------------- sidebar ui ---------------------------------------
with st.sidebar:
    st.title("chatbot history")

    if st.button(
        "New button"
    ):  # if somebody click on new chat -> create new thread_id , add that thread_id to the chat_thread and then empty the message history so main page get blank
        new_thread_id = generate_thread_id()
        st.session_state["chat_thread"].append(new_thread_id)
        st.session_state["thread_id"] = new_thread_id
        reset_chat()

    st.header("my conversations")

    for thread_id in st.session_state["chat_thread"]:
        if st.button(str(thread_id)):
            st.session_state["thread_id"] = thread_id
            load_conversation(thread_id)


# ---------------------------------------- main page ui ---------------------------------------

st.title("- CHATBOT -")

# this will print all teh messages in the message_history
for msg in st.session_state["message_history"]:
    with st.chat_message(msg["role"]):
        st.text(msg["content"])

user_input = st.chat_input("type here")

if user_input:
    # put user input into the message_history
    st.session_state["message_history"].append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.text(user_input)

    # now CONFIG
    CONFIG = {
        "configurable": {
            "thread_id": st.session_state["thread_id"],
            "user_id": "user_1",
        }
    }
    initial_state = {"messages": [HumanMessage(content=user_input)]}
    ai_response_object = workflow.invoke(initial_state, CONFIG)

    ai_message = ai_response_object["messages"][-1].content

    # store it into the message history
    st.session_state["message_history"].append(
        {"role": "assistant", "content": ai_message}
    )

    with st.chat_message("assistant"):
        st.text(ai_message)
