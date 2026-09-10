from agents import build_reader_agent , build_search_agent , writer_chain , critic_chain
from langchain_core.messages import HumanMessage
from rich import print

def run_research_pipeline(topic : str) -> dict :
    state = {}

    # step 1 - search agent
    print("\n"+" ="*50)
    print("step 1 - search agent is working ...")
    print("="*50)

    search_agent = build_search_agent()
    search_result = search_agent.invoke({
        "messages": [
            HumanMessage(content=f"Search for recent and reliable information on {topic} . Do not replace URLs with citations or reference IDs .")
        ]
    })

    state["search_results"] = search_result['messages'][-1].content

    print("\n search result \n", state["search_results"])

    #step 2 - reader agent 

    print("\n"+" ="*50)
    print("step 2 - reader agent is scraping top resources...")
    print("="*50)

    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({
        "messages": [
            HumanMessage(
                content=(
                    f"Based on the following search results about '{topic}',"
                    f"Pick the most relevant URL and scrape it for deeper content . \n\n"
                    f"Search results:\n{state['search_results'][:1000]}"
                )
            )
        ]
    })
    state["scraped_content"] = reader_result['messages'][-1].content

    print("\n scraped content \n", state["scraped_content"])    

    # step 3 - writer chain

    print("\n"+" ="*50)
    print("step 3 - Writer is drafting a report...")
    print("="*50)

    research_combined = (
        f"Search Results:\n{state['search_results']}\n\n"
        f"Detailed Scraped Content:\n{state['scraped_content']}"
    )

    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })

    print("\n Final Report \n", state["report"])

    # step 4 - critic chain

    print("\n"+" ="*50)
    print("step 4 - Critic is evaluating the report...")
    print("="*50)

    state["critic"] = critic_chain.invoke({
        "report" : state["report"]
    })
    print("\n critic \n", state["critic"])

    return state


if __name__ == "__main__" :
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)