from .main import router as main_router
from .quiz import router as quiz_router
from .riddles import router as riddles_router
from .word_game import router as word_router
from .games import router as games_router

__all__ = ['main_router','quiz_router','riddles_router','word_router','games_router']