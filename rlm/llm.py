from __future__ import annotations

from dataclasses import dataclass
import json
import re
import requests
from typing import Any, Dict, Optional, Sequence, Tuple
from tenacity import (
    retry, 
    retry_if_exception_type,
    stop_after_attempt, 
    wait_fixed
)



class OpenRouterChatAPI:

    def __init__(self, api_key: str, model_name: str) -> None:
        self.url = "https://openrouter.ai/api/v1/chat/completions"
        self.headers = {"Authorization": f"Bearer {api_key}"}
        self.model_name = model_name


    def _extract_repl(self, text: str) -> Tuple[bool, str]:
        is_code = '```repl' in text
        pattern = rf"```repl(.*?)```"
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        return (
            is_code,
            match.group(1).strip() if match else ""
        )


    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(1),
        retry=retry_if_exception_type(
            requests.exceptions.RequestException
        ),
        reraise=True
    )
    def _api_request(
        self,
        body: Dict, 
        headers: Optional[Dict] = None,
        timeout: Optional[float] = None
    ) -> requests.Response:
        headers_ = self.headers
        if type(headers) == dict:
            headers_.update(headers)

        response = requests.post(
            url=self.url,
            headers=headers_,
            data=json.dumps(body),
            timeout=timeout
        )
        response.raise_for_status()
        
        return response
    

    def call(
        self,
        body: Dict, 
        headers: Optional[Dict] = None,
        timeout: Optional[float] = None
    ) -> Tuple[str, str, str, str]:
        response = self._api_request(body, headers, timeout)
        if response.status_code == 200:
            response_json = response.json()
            content = response_json["choices"][0]["message"]["content"]
            is_code, code = self._extract_repl(content)
            message = content.split('```repl')[0].strip()
            message = message.split('FINAL(')[0].strip()
            return content, message, is_code, code
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
    content: str
    message: str
    is_code: bool
    code: str



class LLMBackend:
    
    def __init__(
        self, 
        model_provider: str, 
        model_api_key: str, 
        model_name: str
    ) -> None:
        self.model_provider = model_provider
        self.model_api_key = model_api_key
        self.model_name = model_name
        self.provider = self._select_provider()


    def _select_provider(self) -> OpenRouterChatAPI:
        if self.model_provider == 'openrouter':
            return OpenRouterChatAPI(
                api_key=self.model_api_key,
                model_name=self.model_name
            )


    def generate(self, prompt: LLMPrompt) -> LLMResponse:
        body = {
            "model": self.model_name,
            "messages": prompt.messages,
            "temperature": 0
        }
        # print(f"> Body:\n{json.dumps(body, indent=4)}")
        content, message, is_code, code = self.provider.call(body)
        return LLMResponse(
            content=content,
            message=message, 
            is_code=is_code,
            code=code
        )