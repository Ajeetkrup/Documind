# onnx_embeddings.py

import numpy as np
from transformers import AutoTokenizer
from optimum.onnxruntime import ORTModelForFeatureExtraction
import onnxruntime as ort


class ONNXEmbeddings:
    def __init__(self, model_path="onnx_output"):
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)

        sess_options = ort.SessionOptions()
        sess_options.intra_op_num_threads = 2
        sess_options.inter_op_num_threads = 2

        self.model = ORTModelForFeatureExtraction.from_pretrained(
            model_path,
            session_options=sess_options,
            provider="CPUExecutionProvider",
        )

    def _embed(self, texts):
        inputs = self.tokenizer(
            texts,
            padding=True,
            truncation=True,
            return_tensors="np"
        )

        outputs = self.model(**inputs)

        token_embeddings = outputs.last_hidden_state
        attention_mask = inputs["attention_mask"]

        mask = np.expand_dims(attention_mask, axis=-1).astype(float)

        sum_embeddings = np.sum(token_embeddings * mask, axis=1)
        sum_mask = np.clip(np.sum(mask, axis=1), 1e-9, None)

        embeddings = sum_embeddings / sum_mask

        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        embeddings = embeddings / norms

        return embeddings.astype(np.float32)

    def embed_documents(self, texts):
        return self._embed(texts).tolist()

    def embed_query(self, text):
        return self._embed([text])[0].tolist()