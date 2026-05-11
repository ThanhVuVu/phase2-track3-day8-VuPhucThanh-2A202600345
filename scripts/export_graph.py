from langgraph_agent_lab.graph import build_graph
import os

def export():
    graph = build_graph()
    mermaid_text = graph.get_graph().draw_mermaid()
    
    output_dir = "docs/images"
    os.makedirs(output_dir, exist_ok=True)
    
    with open(os.path.join(output_dir, "graph.mermaid"), "w", encoding="utf-8") as f:
        f.write(mermaid_text)
    
    print(f"Mermaid diagram exported to {output_dir}/graph.mermaid")
    print("\nMermaid Content:\n")
    print(mermaid_text)

if __name__ == "__main__":
    export()
