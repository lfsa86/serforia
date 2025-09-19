"""
Base Agent class for the SERFOR multi-agent system
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from instantneo import InstantNeo, SkillManager
from dotenv import load_dotenv
import os

load_dotenv()

class BaseAgent(ABC):
    """Base class for all agents in the SERFOR system"""

    def __init__(
        self,
        name: str,
        role_setup: str,
        provider: str = "openai",
        model: str = "gpt-4o-mini",
        temperature: float = 0.4,
        skills: Optional[SkillManager] = None
    ):
        self.name = name
        self.role_setup = role_setup

        # Initialize InstantNeo agent
        self.agent = InstantNeo(
            provider=provider,
            api_key=os.getenv("OPENAI_API_KEY"),
            model=model,
            temperature=temperature,
            role_setup=role_setup,
            skills=skills
        )

    @abstractmethod
    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process input and return structured output"""
        pass

    def run(self, prompt: str, **kwargs) -> str:
        """Direct interface to the underlying InstantNeo agent"""
        return self.agent.run(prompt, **kwargs)

    def get_info(self) -> Dict[str, str]:
        """Return agent information"""
        return {
            "name": self.name,
            "role": self.role_setup,
            "skills": len(self.agent.skills.skills) if self.agent.skills else 0
        }