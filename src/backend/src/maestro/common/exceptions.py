"""Custom exceptions for MAESTRO backend."""

from typing import Any


class MaestroError(Exception):
    """Base exception for MAESTRO backend."""

    def __init__(self, message: str, *, code: str = "INTERNAL_ERROR", detail: Any = None) -> None:
        self.message = message
        self.code = code
        self.detail = detail
        super().__init__(message)


class NotFoundError(MaestroError):
    """Raised when a requested entity does not exist."""

    def __init__(self, entity_type: str, entity_id: str) -> None:
        super().__init__(
            message=f"{entity_type} con id '{entity_id}' non trovato",
            code=f"{entity_type.upper()}_NOT_FOUND",
            detail={"entity_type": entity_type, "entity_id": entity_id},
        )


class ForbiddenError(MaestroError):
    """Raised when the user does not have permission for the requested action."""

    def __init__(self, message: str = "Accesso non autorizzato") -> None:
        super().__init__(message=message, code="FORBIDDEN")


class ConsentRequiredError(MaestroError):
    """Raised when required consents are missing for an operation."""

    def __init__(self, missing_consents: list[str]) -> None:
        super().__init__(
            message="Consensi richiesti mancanti: " + ", ".join(missing_consents),
            code="CONSENT_MISSING",
            detail={"missing_consents": missing_consents},
        )


class TransitionIllegalError(MaestroError):
    """Raised when a KMM state transition is not permitted."""

    def __init__(self, node_id: str, current_state: str, target_state: str) -> None:
        super().__init__(
            message=(
                f"Transizione non permessa per nodo '{node_id}': "
                f"{current_state} -> {target_state}"
            ),
            code="TRANSITION_ILLEGAL",
            detail={
                "node_id": node_id,
                "current_state": current_state,
                "target_state": target_state,
            },
        )


class SafeguardingBlockedError(MaestroError):
    """Raised when content is blocked by the safeguarding agent."""

    def __init__(self, violations: list[str]) -> None:
        super().__init__(
            message="Contenuto bloccato dal controllo safeguarding",
            code="SAFEGUARDING_BLOCKED",
            detail={"violations": violations},
        )


class OverrideMotivationError(MaestroError):
    """Raised when override motivation is too short."""

    def __init__(self) -> None:
        super().__init__(
            message="La motivazione dell'override deve contenere almeno 20 caratteri",
            code="OVERRIDE_MOTIVATION_SHORT",
        )


class LLMUnavailableError(MaestroError):
    """Raised when all LLM providers are unavailable."""

    def __init__(self) -> None:
        super().__init__(
            message="Servizio LLM non disponibile",
            code="LLM_UNAVAILABLE",
        )
