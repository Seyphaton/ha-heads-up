"""Interfaces the engine and `notify` validation call. H2 implements the audience and recipient
ones (`HubResolver`); H4 will implement policies, so the null catalog stands in until then.
"""

from __future__ import annotations

from typing import Protocol


class AudienceResolver(Protocol):
    def names(self) -> list[str]: ...


class RecipientResolver(Protocol):
    def known(self, channel: str) -> list[str]: ...
    def accepts(self, channel: str, name: str) -> bool: ...


class PolicyCatalog(Protocol):
    def names(self) -> list[str]: ...


class NoPolicies:
    def names(self) -> list[str]:
        return []
