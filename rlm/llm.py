from __future__ import annotations

from dataclasses import dataclass
import json
import os
import re
import requests
from typing import Dict, Optional, Sequence, Tuple
from dotenv import load_dotenv


load_dotenv()



OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL")



class OpenRouterChatAPI:
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {OPENROUTER_API_KEY}"}


    def _extract(self, text: str, tag: str) -> str:
        pattern = rf"<{tag}>(.*?)</{tag}>"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return match.group(1).strip() if match else ""
    

    def _extract_repl(self, text: str) -> Tuple[bool, str]:
        is_code = '```repl' in text
        pattern = rf"```repl(.*?)```"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return (
            is_code,
            match.group(1).strip() if match else ""
        )


    def _api_request(
        self,
        body: Dict, 
        headers: Optional[Dict] = None,
        timeout: Optional[float] = None
    ) -> requests.Response:
        headers_ = OpenRouterChatAPI.headers
        if type(headers) == dict:
            headers_.update(headers)

        response = requests.post(
            url=OpenRouterChatAPI.url,
            headers=headers_,
            data=json.dumps(body),
            timeout=timeout
        )
        
        return response
    

    def call(
        self,
        body: Dict, 
        headers: Optional[Dict] = None,
        timeout: Optional[float] = None
    ) -> Tuple[Dict, str, str, str]:
        response = self._api_request(body, headers, timeout)
        if response.status_code == 200:
            response_json = response.json()
            ai_msg_data = response_json['choices'][0]['message']
            message = response_json["choices"][0]["message"]["content"]
            is_code, code = self._extract_repl(message)
            tool_calls = response_json["choices"][0]["message"].get("tool_calls")
            tool_id, code = '', ''
            if tool_calls and tool_calls[0]['function']['name'] == 'run_python':
                tool_id = tool_calls[0]['id']
                tool_arguments = json.loads(tool_calls[0]['function']['arguments'])
                code = tool_arguments.get('code', '')
            return ai_msg_data, message, code, tool_id
            # return message, is_code, code
        else:
            raise Exception(f"OpenRouter Exception: {response.status_code} | {response.content}")
                        


@dataclass
class LLMPrompt:
    history: Sequence[Dict]

    @property
    def messages(self) -> str:
        return self.history


@dataclass
class LLMResponse:
    ai_msg_data: Dict
    message: str
    # is_code: bool
    code: str
    tool_id: str


class LLMBackend:
    provider = OpenRouterChatAPI()

    def generate(self, prompt: LLMPrompt) -> LLMResponse:
        body = {
            "model": OPENROUTER_MODEL,
            "messages": prompt.messages,
            "tools": [
                {
                "type": "function",
                "function": {
                    "name": "run_python",
                    "description": "Execute Python code and return stdout (and optionally errors).",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "code": {"type": "string"}
                        },
                        "required": ["code"]
                    }
                }
                }
            ],
            "temperature": 0
        }
        print(f"> Body:\n{json.dumps(body, indent=4)}")
        ai_msg_data, message, code, tool_id = self.provider.call(body)
        # message, is_code, code = self.provider.call(body)
        return LLMResponse(
            ai_msg_data=ai_msg_data,
            message=message, 
            # is_code=is_code,
            code=code, 
            tool_id=tool_id
        )