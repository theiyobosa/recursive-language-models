import argparse
from colorama import Fore, Style, init
from rlm import RecursiveLanguageModel



init(autoreset=True)


def main() -> None:
    # Argparse
    parser = argparse.ArgumentParser(description="Recursive Language Model Runner")

    parser.add_argument(
        "--model-provider",
        type=str,
        choices=["openrouter"],
        default="openrouter",
        help="LLM Provider"
    )

    parser.add_argument(
        "--model-api-key",
        type=str,
        required=True,
        help="LLM API key"
    )

    parser.add_argument(
        "--model-name",
        type=str,
        default="openai/gpt-4o-mini",
        help="OpenRouter model name, e.g 'openai/gpt-4o'"
    )

    parser.add_argument(
        "--max-iterations",
        type=int,
        default=10,
        help="Maximum number of recursive iterations per user input"
    )

    args = parser.parse_args()

    # Processing user input
    prompt = ''
    model = RecursiveLanguageModel(
        prompt=prompt,
        model_provider=args.model_provider,
        model_api_key=args.model_api_key,
        model_name=args.model_name,
        max_iterations=args.max_iterations
    )

    while True:
        print(f"\n{Fore.CYAN}{Style.BRIGHT}{'='*60}")
        prompt = input(f"{Fore.YELLOW}{Style.BRIGHT}> Prompt: {Style.RESET_ALL}")

        if prompt == '/bye':
            print(f"{Fore.RED}Goodbye 👋")
            break

        model.reset_prompt(prompt)

        is_complete, result = model.run()
        if not is_complete:
            print(
                f"\n{Fore.RED}{Style.BRIGHT}"
                f"{'='*20} NO ANSWER {'='*20}"
            )
            print(f"{Fore.RED}{Style.BRIGHT}{result}")
            print(f"{Fore.RED}{'='*48}\n")
            break

        print(
            f"\n{Fore.GREEN}{Style.BRIGHT}"
            f"{'='*20} ANSWER {'='*20}"
        )
        print(f"{Fore.GREEN}{Style.BRIGHT}{result}")
        print(f"{Fore.GREEN}{'='*48}\n")

        model.env.repl.reset_final_answer()


if __name__ == "__main__":
    main()