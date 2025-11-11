import gradio as gr
import hashlib
from typing import List, Dict
import os
import sys

print("📦 Loading imports...")
try:
    from document_processor.file_handler import DocumentProcessor
    print("✅ Imported DocumentProcessor")
except Exception as e:
    print(f"❌ Failed to import DocumentProcessor: {e}")
    sys.exit(1)

try:
    from retriever.builder import RetrieverBuilder
    print("✅ Imported RetrieverBuilder")
except Exception as e:
    print(f"❌ Failed to import RetrieverBuilder: {e}")
    sys.exit(1)

try:
    from agents.workflow import AgentWorkflow
    print("✅ Imported AgentWorkflow")
except Exception as e:
    print(f"❌ Failed to import AgentWorkflow: {e}")
    sys.exit(1)

try:
    from config import constants, settings
    print("✅ Imported config (constants, settings)")
except Exception as e:
    print(f"❌ Failed to import config: {e}")
    sys.exit(1)

try:
    from utils.logging import logger
    print("✅ Imported logger")
except Exception as e:
    print(f"❌ Failed to import logger: {e}")
    sys.exit(1)

print("✅ All imports loaded successfully!\n")

# 1) Define some example data 
#    (i.e. question + paths to documents relevant to that question).
EXAMPLES = {
    "Google 2024 Environmental Report": {
        "question": "Retrieve the data center PUE efficiency values in Singapore 2nd facility in 2019 and 2022. Also retrieve regional average CFE in Asia pacific in 2023",
        "file_paths": ["examples/google-2024-environmental-report.pdf"]  
    },
    "DeepSeek-R1 Technical Report": {
        "question": "Summarize DeepSeek-R1 model's performance evaluation on all coding tasks against OpenAI o1-mini model",
        "file_paths": ["examples/DeepSeek Technical Report.pdf"]
    }
}

def main():
    print("=" * 60)
    print("🚀 Starting DocuMind Application...")
    print("=" * 60)
    
    try:
        print("\n[1/3] Initializing DocumentProcessor...")
        processor = DocumentProcessor()
        print("✅ DocumentProcessor initialized successfully")
        
        print("\n[2/3] Initializing RetrieverBuilder...")
        retriever_builder = RetrieverBuilder()
        print("✅ RetrieverBuilder initialized successfully")
        
        print("\n[3/3] Initializing AgentWorkflow...")
        workflow = AgentWorkflow()
        print("✅ AgentWorkflow initialized successfully")
    except Exception as e:
        print(f"\n❌ ERROR during initialization: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return

    # Define custom CSS for styling
    css = """
    .title {
        font-size: 1.5em !important; 
        text-align: center !important;
        color: #FFD700; 
    }

    .subtitle {
        font-size: 1em !important; 
        text-align: center !important;
        color: #FFD700; 
    }

    .text {
        text-align: center;
    }
    """

    js = """
    function createGradioAnimation() {
        var container = document.createElement('div');
        container.id = 'gradio-animation';
        container.style.fontSize = '2em';
        container.style.fontWeight = 'bold';
        container.style.textAlign = 'center';
        container.style.marginBottom = '20px';
        container.style.color = '#eba93f';

        var text = 'Welcome to DocuMind 🧠!';
        for (var i = 0; i < text.length; i++) {
            (function(i){
                setTimeout(function(){
                    var letter = document.createElement('span');
                    letter.style.opacity = '0';
                    letter.style.transition = 'opacity 0.1s';
                    letter.innerText = text[i];

                    container.appendChild(letter);

                    setTimeout(function() {
                        letter.style.opacity = '0.9';
                    }, 50);
                }, i * 250);
            })(i);
        }

        var gradioContainer = document.querySelector('.gradio-container');
        gradioContainer.insertBefore(container, gradioContainer.firstChild);

        return 'Animation created';
    }
    """

    with gr.Blocks(theme=gr.themes.Citrus(), title="DocuMind 🧠", css=css, js=js) as demo:
        gr.Markdown("## 🧠 DocuMind: Intelligent Document Intelligence", elem_classes="subtitle")
        
        # Enhanced instructions section
        with gr.Row():
            with gr.Column():
                gr.Markdown("""
                ### 🚀 Quick Start Guide
                
                **Step 1:** Upload your document(s) using the file uploader below  
                **Step 2:** Enter your question in the text box  
                **Step 3:** Click the **Submit 🚀** button to get your answer
                
                ---
                
                ### 📚 Using Examples
                
                **Option 1:** Select an example from the dropdown menu  
                **Option 2:** Click **Load Example 🛠️** to populate the fields  
                **Option 3:** Click **Submit 🚀** to process
                
                ---
                
                ### ⚠️ Important Notes
                
                📄 **Supported Formats:** `.pdf`, `.docx`, `.txt`, `.md`  
                🔍 **Features:** Multi-document support, fact verification, relevance checking  
                ✨ **Powered by:** Advanced RAG with hybrid retrieval (BM25 + Vector Search)
                """)

        # 2) Maintain the session state for retrieving doc changes
        session_state = gr.State({
            "file_hashes": frozenset(),
            "retriever": None
        })

        # 3) Layout 
        with gr.Row():
            with gr.Column():
                # Section for Examples
                gr.Markdown("### Example 📂")
                example_dropdown = gr.Dropdown(
                    label="Select an Example 🐥",
                    choices=list(EXAMPLES.keys()),
                    value=None,  # initially unselected
                )
                load_example_btn = gr.Button("Load Example 🛠️")

                # Standard input components
                files = gr.Files(label="📄 Upload Documents", file_types=constants.ALLOWED_TYPES)
                question = gr.Textbox(label="❓ Question", lines=3)

                submit_btn = gr.Button("Submit 🚀")
                
            with gr.Column():
                answer_output = gr.Textbox(label="🐥 Answer", interactive=False)
                verification_output = gr.Textbox(label="✅ Verification Report")

        # 4) Helper function to load example into the UI
        def load_example(example_key: str):
            """
            Given a key like 'Example 1', 
            read the relevant docs from disk and return
            them as file-like objects, plus the example question.
            """
            if not example_key or example_key not in EXAMPLES:
                return [], ""  # blank if not found

            ex_data = EXAMPLES[example_key]
            question = ex_data["question"]
            file_paths = ex_data["file_paths"]

            # Prepare the file list to return. We read them from disk to
            # give Gradio something it can handle as "uploaded" files.
            loaded_files = []
            for path in file_paths:
                if os.path.exists(path):
                    # Gradio can accept a path directly, or a file-like object
                    loaded_files.append(path)
                else:
                    logger.warning(f"File not found: {path}")

            # The function can return lists matching the outputs we define below
            return loaded_files, question

        load_example_btn.click(
            fn=load_example,
            inputs=[example_dropdown],
            outputs=[files, question]
        )

        # 5) Standard flow for question submission
        def process_question(question_text: str, uploaded_files: List, state: Dict):
            """Handle questions with document caching."""
            try:
                if not question_text.strip():
                    raise ValueError("❌ Question cannot be empty")
                if not uploaded_files:
                    raise ValueError("❌ No documents uploaded")

                current_hashes = _get_file_hashes(uploaded_files)
                
                if state["retriever"] is None or current_hashes != state["file_hashes"]:
                    logger.info("Processing new/changed documents...")
                    chunks = processor.process(uploaded_files)
                    retriever = retriever_builder.build_hybrid_retriever(chunks)
                    
                    state.update({
                        "file_hashes": current_hashes,
                        "retriever": retriever
                    })
                
                result = workflow.full_pipeline(
                    question=question_text,
                    retriever=state["retriever"]
                )
                
                return result["draft_answer"], result["verification_report"], state
                    
            except Exception as e:
                logger.error(f"Processing error: {str(e)}")
                return f"❌ Error: {str(e)}", "", state

        submit_btn.click(
            fn=process_question,
            inputs=[question, files, session_state],
            outputs=[answer_output, verification_output, session_state]
        )

    print("\n" + "=" * 60)
    print("📦 Building Gradio interface...")
    print("=" * 60)
    
    try:
        print("\n🌐 Launching Gradio server...")
        print("   Server: 127.0.0.1")
        print("   Port: 5000")
        print("   Share: True")
        print("\n⏳ Please wait while the server starts...")
        print("📌 Look for the Gradio URL below (it will appear after 'Running on...')")
        print("=" * 60)
        print()
        
        demo.launch(server_name="127.0.0.1", server_port=5000, share=True)
        
        # Note: This line won't execute until the server is stopped
        # because demo.launch() is a blocking call
        print("\n✅ Gradio server launched successfully!")
        print("=" * 60)
    except Exception as e:
        print(f"\n❌ ERROR launching Gradio: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise

def _get_file_hashes(uploaded_files: List) -> frozenset:
    """Generate SHA-256 hashes for uploaded files."""
    hashes = set()
    for file in uploaded_files:
        with open(file.name, "rb") as f:
            hashes.add(hashlib.sha256(f.read()).hexdigest())
    return frozenset(hashes)

if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("🧠 DocuMind Application Starting...")
    print("=" * 60)
    print(f"Python version: {__import__('sys').version}")
    print(f"Working directory: {os.getcwd()}")
    print("=" * 60 + "\n")
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Application interrupted by user")
    except Exception as e:
        print(f"\n\n❌ FATAL ERROR: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        raise
