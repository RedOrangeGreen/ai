#!/usr/bin/env python3
"""LangChain app using llama.cpp via llama-cpp-python."""

import sys
import argparse
from pathlib import Path

from langchain_community.llms import LlamaCpp
from langchain_core.callbacks import CallbackManager, StreamingStdOutCallbackHandler
from langchain_core.prompts import PromptTemplate


def build_llm(model_path: str, n_gpu_layers: int = 0, n_ctx: int = 2048):
    return LlamaCpp(
        model_path=model_path,
        temperature=0.7,
        max_tokens=512,
        n_ctx=n_ctx,
        n_gpu_layers=n_gpu_layers,
        n_threads=8,
        n_batch=512,
        f16_kv=True,
        verbose=False,
        callbacks=CallbackManager([StreamingStdOutCallbackHandler()]),
    )


def main():
    parser = argparse.ArgumentParser(description="LangChain + llama.cpp")
    parser.add_argument("model", type=str, help="Path to GGUF model file")
    parser.add_argument("--gpu-layers", type=int, default=0, help="GPU offload layers")
    parser.add_argument(
        "--prompt",
        type=str,
        default="Explain quantum computing in one sentence.",
        help="Prompt to send to the model",
    )
    parser.add_argument("--ctx", type=int, default=2048, help="Context window size")
    args = parser.parse_args()

    if not Path(args.model).exists():
        print(f"Error: model file not found: {args.model}", file=sys.stderr)
        sys.exit(1)

    llm = build_llm(args.model, args.gpu_layers, args.ctx)

    prompt = PromptTemplate.from_template(
        "You are a helpful assistant.\n\nUser: {question}\nAssistant:"
    )
    chain = prompt | llm

    print(f"\n--- Prompt ---\n{args.prompt}\n--- Response ---")
    chain.invoke({"question": args.prompt})


if __name__ == "__main__":
    main()
