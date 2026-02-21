"""Minimal entry point for exercising the recursive scaffold."""

from pathlib import Path

from rlm import RecursiveLanguageModel


def main() -> None:
    prompt = ''
    model = RecursiveLanguageModel(prompt=prompt)
    while True:
        prompt = input("> Prompt: ")
        if prompt != '/bye':
            model.reset_prompt(prompt)
            result = model.run()
            print(f"Result:\n{result}")
            model.env.repl.reset_final_answer()


if __name__ == "__main__":
    main()
