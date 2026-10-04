from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class DiagnosticResult:
    """
    Resultado de un diagnóstico energético.

    Un diagnóstico describe una situación detectada a partir
    de resultados ya calculados. No contiene recomendaciones
    de actuación.
    """

    code: str
    category: str
    severity: str
    title: str
    description: str
    evidence: Mapping[str, float | str]

    def __post_init__(self):
        if not self.code:
            raise ValueError(
                "Diagnostic code cannot be empty."
            )

        if not self.category:
            raise ValueError(
                "Diagnostic category cannot be empty."
            )

        if self.severity not in {
            "info",
            "warning",
            "critical",
        }:
            raise ValueError(
                "Diagnostic severity must be "
                "'info', 'warning' or 'critical'."
            )

        if not self.title:
            raise ValueError(
                "Diagnostic title cannot be empty."
            )

        if not self.description:
            raise ValueError(
                "Diagnostic description cannot be empty."
            )