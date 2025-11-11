from typing import Dict, List, Optional
from langchain.schema import Document
from config.settings import settings
from huggingface_hub import InferenceClient
import base64
from pathlib import Path
import os


class ResearchAgent:
    """
    Multimodal Research Agent using Hugging Face Inference API.
    
    Uses Qwen2.5-VL-72B-Instruct model for vision-language tasks.
    Best overall performance with excellent multimodal capabilities.
    """
    
    def __init__(self):
        """
        Initialize the research agent with Qwen2.5-VL-72B-Instruct model.
        """
        # Set Hugging Face token
        self.hf_token = settings.HUGGINGFACE_API_TOKEN
        
        # Use Qwen2.5-VL-72B-Instruct model
        self.model_id = "Qwen/Qwen2.5-VL-72B-Instruct"
        
        # Initialize Hugging Face Inference Client
        print(f"Initializing ResearchAgent with Hugging Face Inference API...")
        self.client = InferenceClient(token=self.hf_token)
        
        print(f"✅ ResearchAgent initialized with {self.model_id}")
        
    def sanitize_response(self, response_text: str) -> str:
        """
        Sanitize the LLM's response by stripping unnecessary whitespace.
        """
        return response_text.strip()

    def generate_prompt(self, question: str, context: str) -> str:
        """
        Generate a structured prompt for the LLM to generate a precise and factual answer.
        """
        prompt = f"""You are an AI assistant designed to provide precise and factual answers based on the given context.

Instructions:
- Answer the following question using only the provided context.
- Be clear, concise, and factual.
- Return as much information as you can get from the context.

Question: {question}

Context:
{context}

Answer:"""
        return prompt

    def encode_image(self, image_path: str) -> str:
        """
        Encode an image file to base64 string.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Base64-encoded image string
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def get_image_url(self, image_path: str) -> str:
        """
        Convert image to data URI format for HF API.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            Data URI string
        """
        ext = Path(image_path).suffix.lower()
        mime_type = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }.get(ext, 'image/jpeg')
        
        image_data = self.encode_image(image_path)
        return f"data:{mime_type};base64,{image_data}"

    def generate(
        self, 
        question: str, 
        documents: List[Document],
        image_path: Optional[str] = None,
        max_tokens: int = 512
    ) -> Dict:
        """
        Generate an initial answer using the provided documents.
        Supports both text-only and multimodal (text + image) queries.
        
        Args:
            question: The user's question
            documents: List of retrieved documents
            image_path: Optional path to an image file for multimodal queries
            max_tokens: Maximum tokens to generate
        
        Returns:
            Dictionary with draft_answer, context_used, and multimodal flag
        """
        print(f"ResearchAgent.generate called with question='{question}' and {len(documents)} documents.")
        if image_path:
            print(f"Multimodal mode: Image provided at {image_path}")

        # Combine the top document contents into one string
        context = "\n\n".join([doc.page_content for doc in documents])
        print(f"Combined context length: {len(context)} characters.")

        # Create a prompt for the LLM
        prompt = self.generate_prompt(question, context)
        print("Prompt created for the LLM.")

        # Call the LLM to generate the answer
        try:
            print(f"Sending request to Hugging Face (Qwen2.5-VL-72B-Instruct)...")
            
            if image_path and Path(image_path).exists():
                # Multimodal query with image
                image_url = self.get_image_url(image_path)
                
                # Use chat completion for vision models
                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ]
                
                response = self.client.chat_completion(
                    model=self.model_id,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.3,
                )
                
                llm_response = response.choices[0].message.content
                
            else:
                # Text-only query - Use chat_completion API (model only supports conversational task)
                messages = [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
                
                response = self.client.chat_completion(
                    model=self.model_id,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=0.3,
                )
                
                llm_response = response.choices[0].message.content
            
            print("✅ Response received from Hugging Face")
            
        except Exception as e:
            print(f"❌ Error during model inference: {e}")
            raise RuntimeError(f"Failed to generate answer: {e}") from e

        # Process the response
        try:
            if isinstance(llm_response, str):
                llm_response = llm_response.strip()
            else:
                llm_response = str(llm_response).strip()
            print(f"Raw LLM response:\n{llm_response}")
        except Exception as e:
            print(f"Unexpected response structure: {e}")
            llm_response = "I cannot answer this question based on the provided documents."

        # Sanitize the response
        draft_answer = self.sanitize_response(llm_response) if llm_response else "I cannot answer this question based on the provided documents."

        print(f"Generated answer: {draft_answer[:200]}...")

        return {
            "draft_answer": draft_answer,
            "context_used": context,
            "multimodal": image_path is not None,
            "model_used": self.model_id
        }

    def generate_from_image(
        self,
        question: str,
        image_path: str,
        additional_context: str = "",
        max_tokens: int = 512
    ) -> Dict:
        """
        Generate an answer directly from an image with optional text context.
        Useful for document images, charts, diagrams, etc.
        
        Args:
            question: The question about the image
            image_path: Path to the image file
            additional_context: Optional additional text context
            max_tokens: Maximum tokens to generate
        
        Returns:
            Dictionary with draft_answer and image_path
        """
        print(f"Generating answer from image: {image_path}")
        
        if not Path(image_path).exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        try:
            # Prepare the prompt
            if additional_context:
                full_prompt = f"""Based on this image and the following context, answer the question.

Context: {additional_context}

Question: {question}

Answer:"""
            else:
                full_prompt = question
            
            # Prepare image
            image_url = self.get_image_url(image_path)
            
            # Use chat completion API
            messages = [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": full_prompt},
                        {"type": "image_url", "image_url": {"url": image_url}}
                    ]
                }
            ]
            
            response = self.client.chat_completion(
                model=self.model_id,
                messages=messages,
                max_tokens=max_tokens,
                temperature=0.3,
            )
            
            answer = response.choices[0].message.content
            
            return {
                "draft_answer": self.sanitize_response(answer),
                "image_path": image_path,
                "model_used": self.model_id
            }
            
        except Exception as e:
            print(f"❌ Error processing image: {e}")
            raise RuntimeError(f"Failed to process image: {e}") from e
    
    def batch_generate(
        self,
        questions: List[str],
        documents_list: List[List[Document]],
        image_paths: Optional[List[Optional[str]]] = None,
        max_tokens: int = 512
    ) -> List[Dict]:
        """
        Process multiple questions in batch.
        
        Args:
            questions: List of questions
            documents_list: List of document lists (one per question)
            image_paths: Optional list of image paths (one per question)
            max_tokens: Maximum tokens to generate per response
            
        Returns:
            List of response dictionaries
        """
        if image_paths is None:
            image_paths = [None] * len(questions)
        
        results = []
        for q, docs, img in zip(questions, documents_list, image_paths):
            try:
                result = self.generate(q, docs, img, max_tokens)
                results.append(result)
            except Exception as e:
                print(f"Error processing question '{q}': {e}")
                results.append({
                    "draft_answer": f"Error: {str(e)}",
                    "context_used": "",
                    "multimodal": False,
                    "model_used": self.model_id
                })
        
        return results
