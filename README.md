# LangGraph Chatbot with Short-Term Memory and Long-Term Memory

A chatbot built with **LangGraph**, **LangChain**, and **Streamlit** that uses both **short-term memory (STM)** and **long-term memory (LTM)** to create more context-aware and personalized conversations.

This project demonstrates how to:

- maintain conversation history inside a thread using short-term memory
- store useful user information as long-term memory
- retrieve relevant long-term memory using semantic search
- manage multiple conversations with different thread IDs
- build a simple chat interface using Streamlit

---

## Overview

This chatbot uses two different kinds of memory:

### 1. Short-Term Memory

Short-term memory stores the conversation history for a specific chat thread.  
It helps the chatbot remember what was said earlier in the same conversation.

In this project, STM is implemented using:

- `InMemorySaver()` as the checkpointer
- `thread_id` to separate one conversation from another

### 2. Long-Term Memory

Long-term memory stores useful user-specific information such as:

- preferences
- goals
- habits
- background facts
- ongoing work or projects

In this project, LTM is implemented using:

- `InMemoryStore()`
- `OpenAIEmbeddings()` for vector embeddings
- semantic search to retrieve only the most relevant memories for the current user query

---

## Features

- Chatbot built using **LangGraph**
- **Short-term memory** using conversation history
- **Long-term memory** using a memory store
- **Semantic search** over stored long-term memories
- **Structured memory extraction** using Pydantic schemas
- **Multiple conversation threads** using unique `thread_id`
- **User-based memory namespace** using `user_id`
- **Streamlit frontend** for interactive chatting
- Follow-up questions generated based on memory and current context

---

## How It Works

### Memory Extraction

Whenever the user sends a message, the chatbot first checks whether the message contains information worth saving in long-term memory.

A separate LLM step is used to decide:

- should memory be created or not
- what short, atomic information should be stored

This is done using the `memoryDecision` and `Teller` Pydantic models.

### Long-Term Memory Storage

If the extracted information is useful and marked as new, it is stored in the memory store under a namespace like:

`("user", user_id, "details")`

This allows the chatbot to organize memory by user.

### Semantic Search

When the user sends a new query, the chatbot performs semantic search on long-term memory using:

`store.search(namespace, query=last_message.content)`

This means the bot does not retrieve all stored memories every time.Instead, it retrieves only the memories that are most relevant to the current user query.

This helps keep the context more focused and useful.

### Short-Term Memory Retrieval

The full message history for a thread is maintained using LangGraph's checkpointer and a thread\_id.

This allows the chatbot to continue a conversation naturally inside the same thread.

### Response Generation

The chatbot combines:

*   current user message
    
*   short-term conversation history
    
*   relevant long-term memory
    

Then it generates a response using the LLM.

Architecture
------------

### Backend

The backend is responsible for:

*   defining the LangGraph state
    
*   extracting and storing long-term memory
    
*   retrieving relevant long-term memory using semantic search
    
*   combining STM and LTM for response generation
    

Main components:

*   StateGraph
    
*   InMemorySaver
    
*   InMemoryStore
    
*   ChatOpenAI
    
*   OpenAIEmbeddings
    
*   Pydantic schemas for structured output
    

### Frontend

The frontend is built using **Streamlit** and provides:

*   chat interface
    
*   conversation history display
    
*   multiple thread support
    
*   switching between old conversations
    
*   creating a new chat thread
    

Project Structure
-----------------

.
├── backend.py
├── frontend_streamlit.py
├── README.md
└── .env

Tech Stack
----------

*   Python
    
*   LangGraph
    
*   LangChain
    
*   OpenAI
    
*   Streamlit
    
*   Pydantic
    
*   python-dotenv
    

Installation
------------

### 1\. Clone the repository

`git clone https://github.com/ritikkalyan1000/Implement_long_term_memory_and_short_term_memory_in-_langGraph_for-_Chatbot.gitcd Implement_long_term_memory_and_short_term_memory_in-_langGraph_for-_Chatbot   `

### 2\. Create a virtual environment

#### Windows

`   python -m venv venvvenv\Scripts\activate   `

#### Mac/Linux

`   python3 -m venv venvsource venv/bin/activate   `

### 3\. Install dependencies

`   pip install -r requirements.txt   `

If you do not have a requirements.txt yet, install the main packages manually:

`   pip install langgraph langchain langchain-openai streamlit python-dotenv pydantic   `

### 4\. Set up environment variables

Create a .env file and add your OpenAI API key:

`  OPENAI_API_KEY=your_api_key_here   `

Running the Project
-------------------

Run the Streamlit frontend:

`   streamlit run frontend_streamlit.py   `

Current Implementation Details
------------------------------

### Short-Term Memory

Short-term memory is implemented with:

`   checkpointer = InMemorySaver()   `

and conversation separation is handled through:

`   thread_id   `

Each thread keeps its own chat history.

### Long-Term Memory

Long-term memory is implemented with:

`   store = InMemoryStore(index={"embed": embedding_model, "dims": 1546})   `

and memories are stored under a user namespace such as:

`   ("user", user_id, "details")   `

### Semantic Search

Relevant long-term memory is retrieved using the current user message:

`   existing_memory = store.search(    namespace,    query=last_message.content if last_message.content else "",)   `

This allows the chatbot to retrieve only useful memories related to the current query instead of injecting all stored memory into the prompt.

### Structured Memory Extraction

The project uses two Pydantic models:

*   Teller
    
*   memoryDecision
    

These help the LLM return structured decisions for memory creation.

### Multiple Conversation Threads

The frontend generates a unique thread\_id for each new chat:

`   uuid.uuid4()   `

This allows the user to switch between different conversations in the sidebar.

Example Flow
------------

1.  User sends a message
    
2.  The remember node checks whether useful long-term memory should be created
    
3.  If useful memory exists, it is stored in the memory store
    
4.  The chat\_node retrieves relevant long-term memory using semantic search
    
5.  The full short-term chat history is also passed
    
6.  The LLM generates a response using both STM and relevant LTM
    
7.  The response is shown in the Streamlit interface
    

Why Semantic Search is Used
---------------------------

Without semantic search, the chatbot would either:

*   retrieve all long-term memories every time, or
    
*   rely on exact keyword matching
    

Semantic search improves the design because it helps the chatbot:

*   retrieve only relevant user memories
    
*   keep the prompt more focused
    
*   avoid adding unnecessary memory context
    
*   personalize answers more naturally
    

Limitations
-----------

This project currently uses in-memory storage:

*   InMemorySaver() for short-term memory
    
*   InMemoryStore() for long-term memory
    

This means memory is **not persisted permanently** after the application stops.

Other current limitations:

*   the user ID is fixed in the frontend as "user\_1"
    
*   the memory extraction logic can be improved further
    
*   there is no database or production deployment yet
    
*   there is no authentication or multi-user login system yet
    

Future Improvements
-------------------

Possible next improvements for this project:

*   replace InMemoryStore with a persistent store such as Postgres
    
*   replace InMemorySaver with a persistent checkpointer
    
*   support real multi-user login and dynamic user\_id
    
*   improve duplicate memory detection
    
*   add memory update and delete logic
    
*   add streaming responses
    
*   deploy the project on cloud infrastructure
    
*   improve the UI design
    
*   add conversation titles instead of raw thread IDs
    
*   store timestamps with memories
    

Learning Goals of This Project
------------------------------

This project was built to understand and implement:

*   LangGraph state management
    
*   graph-based chatbot workflow
    
*   short-term vs long-term memory in AI systems
    
*   memory extraction pipelines
    
*   vector-based semantic memory retrieval
    
*   multi-thread conversation handling
    
*   Streamlit-based chatbot UI
    

Notes
-----

This project is a learning-focused implementation of a memory-enabled chatbot architecture.It is useful for understanding how modern AI assistants can combine:

*   conversational context
    
*   persistent user memory
    
*   relevant retrieval
    
*   thread-based interaction
    

Author
------

**Ritik Kalyan**

GitHub: ritikkalyan1000
