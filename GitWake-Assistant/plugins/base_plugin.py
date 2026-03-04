"""
base_plugin.py – Plugin Base Class
=====================================
Abstract base class for GitWake Assistant plugins.
Plugins extend the assistant's capabilities with a standardized interface.

Creating a plugin:
    1. Subclass BasePlugin
    2. Implement execute()
    3. Place the file in the plugins/ directory
    4. Register in plugins/__init__.py

Usage:
    class MyPlugin(BasePlugin):
        name = "my_plugin"
        description = "Does something cool"

        def execute(self, params):
            return "Done!"
"""

from abc import ABC, abstractmethod
from typing import Any
import logging

logger = logging.getLogger(__name__)


class BasePlugin(ABC):
    """Abstract base class for all GitWake plugins."""

    # Override these in subclasses
    name: str = "base_plugin"
    description: str = "Base plugin class"
    version: str = "1.0.0"

    @abstractmethod
    def execute(self, params: dict[str, Any]) -> str:
        """
        Execute the plugin's action.

        Args:
            params: Dictionary of parameters for the action.

        Returns:
            Human-readable result string.
        """
        ...

    def __repr__(self):
        return f"<Plugin: {self.name} v{self.version}>"


class PluginManager:
    """Discovers and manages plugins."""

    def __init__(self):
        self._plugins: dict[str, BasePlugin] = {}

    def register(self, plugin: BasePlugin) -> None:
        """Register a plugin instance."""
        self._plugins[plugin.name] = plugin
        logger.info(f"Registered plugin: {plugin.name}")

    def get(self, name: str) -> BasePlugin | None:
        """Get a plugin by name."""
        return self._plugins.get(name)

    def list_plugins(self) -> list[dict]:
        """List all registered plugins."""
        return [
            {"name": p.name, "description": p.description, "version": p.version}
            for p in self._plugins.values()
        ]

    def execute(self, name: str, params: dict[str, Any]) -> str:
        """Execute a plugin by name."""
        plugin = self._plugins.get(name)
        if not plugin:
            return f"❌ Plugin '{name}' not found."
        try:
            return plugin.execute(params)
        except Exception as e:
            logger.error(f"Plugin '{name}' error: {e}")
            return f"❌ Plugin error: {e}"
