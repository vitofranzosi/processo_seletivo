from dataclasses import dataclass, field


@dataclass(frozen=True)
class Actor:
    subject: str
    institution_scope: str
    permissions: frozenset[str] = field(default_factory=frozenset)

    @property
    def is_authenticated(self) -> bool:
        return True

    def can(self, permission: str) -> bool:
        return permission in self.permissions
