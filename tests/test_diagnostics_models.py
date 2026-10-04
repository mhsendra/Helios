import pytest

from helios.core.diagnostics import DiagnosticResult


class TestDiagnosticResult:

    def test_creates_valid_result(self):
        result = DiagnosticResult(
            code="TEST_DIAGNOSTIC",
            category="energy",
            severity="warning",
            title="Test",
            description="Test diagnostic.",
            evidence={
                "value": 10.0,
            },
        )

        assert result.code == "TEST_DIAGNOSTIC"
        assert result.category == "energy"
        assert result.severity == "warning"
        assert result.title == "Test"
        assert result.description == (
            "Test diagnostic."
        )
        assert result.evidence["value"] == 10.0

    @pytest.mark.parametrize(
        "severity",
        [
            "info",
            "warning",
            "critical",
        ],
    )
    def test_accepts_valid_severity(
        self,
        severity,
    ):
        result = DiagnosticResult(
            code="TEST",
            category="energy",
            severity=severity,
            title="Test",
            description="Test",
            evidence={},
        )

        assert result.severity == severity

    def test_rejects_empty_code(self):
        with pytest.raises(
            ValueError,
            match="code cannot be empty",
        ):
            DiagnosticResult(
                code="",
                category="energy",
                severity="info",
                title="Test",
                description="Test",
                evidence={},
            )

    def test_rejects_invalid_severity(self):
        with pytest.raises(
            ValueError,
            match="severity must be",
        ):
            DiagnosticResult(
                code="TEST",
                category="energy",
                severity="invalid",
                title="Test",
                description="Test",
                evidence={},
            )

    def test_result_is_immutable(self):
        result = DiagnosticResult(
            code="TEST",
            category="energy",
            severity="info",
            title="Test",
            description="Test",
            evidence={},
        )

        with pytest.raises(
            AttributeError,
        ):
            result.code = "OTHER"