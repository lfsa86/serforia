"""
Prompts separados para cada agente del sistema SERFOR.

Este módulo contiene los prompts y conocimiento de dominio organizados
para facilitar su mantenimiento y modificación.

Estructura:
- domain_knowledge.py: Conocimiento del dominio SERFOR (sinónimos, relaciones, glosario)
- interpreter_prompt.py: Prompts para el Interpreter Agent
- planner_prompt.py: Prompts para el Planner Agent
- executor_prompt.py: Prompts para el Executor Agent
- response_prompt.py: Prompts para el Response Agent
- visualization_prompt.py: Prompts para el Visualization Agent
"""

from .domain_knowledge import (
    ENTITY_SYNONYMS,
    ENTITY_DESCRIPTIONS,
    VIEW_RELATIONSHIPS,
    IMPORTANT_NOTES,
    GLOSSARY
)

from .interpreter_prompt import (
    ROLE_SETUP as INTERPRETER_ROLE_SETUP,
    INTERPRETATION_PROMPT_TEMPLATE
)

from .planner_prompt import (
    ROLE_SETUP as PLANNER_ROLE_SETUP,
    PLANNING_PROMPT_TEMPLATE
)

from .executor_prompt import (
    ROLE_SETUP as EXECUTOR_ROLE_SETUP,
    TASK_PROMPT_BASE,
    RETRY_CONTEXT,
    TASK_PROMPTS
)

from .response_prompt import (
    ROLE_SETUP as RESPONSE_ROLE_SETUP,
    RESPONSE_PROMPT_TEMPLATE,
    TABLE_NAME_MAPPING
)

from .visualization_prompt import (
    ROLE_SETUP as VISUALIZATION_ROLE_SETUP,
    VISUALIZATION_PROMPT_TEMPLATE,
    VISUALIZATION_HEURISTICS
)
