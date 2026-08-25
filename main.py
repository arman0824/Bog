import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types


def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    if len(sys.argv) < 2:
        print("I need a prompt")
        sys.exit(1)
    prompt = sys.argv[1]

    verbose_flag = False
    if len(sys.argv) == 3 and sys.argv[2] == "--verbose":
        verbose_flag = True

    messages = [
        types.Content(role="user", parts=[types.Part(text=prompt)]),
    ]

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=messages
    )

    print(("-")*80)
    print(response.text)
    print(("-")*80)
    if response is None or response.usage_metadata is None:
        print("Response is malformed")
        return

    if verbose_flag:
        print(f"User prompt: {prompt}")
        print(f"Response metadata: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


main()