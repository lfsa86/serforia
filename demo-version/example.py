# InstantNeo Example
from instantneo import InstantNeo, SkillManager, SkillManagerOperations, skill
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Skills
@skill()
def greet(name: str) -> str:
    """ This skill allows you to greets a person by name. """
    return f"Hello, {name}!"

@skill()
def add(a: int, b: int) -> int:
    """ This skill allows you to add two numbers. """
    return a + b

# Skill Manager
skills = SkillManager()
skills.register_skill(greet)
skills.register_skill(add)

# Initialize InstantNeo
agent = InstantNeo(
    provider="openai",
    api_key=os.getenv("OPENAI_API_KEY"),
    model="gpt-4o-mini",
    skills= skills,
    role_setup="You are a helpful assistant that can greet people and perform basic arithmetic operations.",
)

# Example usage
response = agent.run(prompt="Greet John and add 5 and 10.")
print(response)