"""Versioned, server-owned compatibility rules for DIY configurations.

The browser can use the same rule-shaped fields for immediate feedback, but
this module is the source of truth at the order boundary.  A rule set has its
own version so that a later change can be introduced without making old order
snapshots ambiguous.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
import re
from typing import Any, Literal, Mapping

from ..models.product import Product


DIY_COMPATIBILITY_RULES_VERSION = 1
MIN_PSU_HEADROOM_W = 150

CompatibilityStatus = Literal["compatible", "incompatible", "unverified"]


@dataclass(frozen=True)
class DiyCompatibilityRuleSet:
    configuration_id: str
    configuration_version: int
    version: int
    min_psu_headroom_w: int


@dataclass(frozen=True)
class DiyCompatibilityCheck:
    rule_id: str
    key: str
    title: str
    status: CompatibilityStatus
    message: str
    remediation: str
    parts: tuple[str, ...]

    @property
    def level(self) -> str:
        """Keep the existing frontend snapshot vocabulary intact."""
        return "ok" if self.status == "compatible" else "warn" if self.status == "incompatible" else "pending"

    def as_dict(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "key": self.key,
            "title": self.title,
            "status": self.status,
            "level": self.level,
            "severity": "critical",
            "message": self.message,
            "remediation": self.remediation,
            "parts": list(self.parts),
        }


@dataclass(frozen=True)
class DiyCompatibilityResult:
    rules: DiyCompatibilityRuleSet
    checks: tuple[DiyCompatibilityCheck, ...]
    total_power_w: int | None
    psu_headroom_w: int | None
    gpu_space_headroom_mm: int | None

    @property
    def status(self) -> str:
        if any(check.status == "incompatible" for check in self.checks):
            return "incompatible"
        if any(check.status == "unverified" for check in self.checks):
            return "unverified"
        return "compatible"

    @property
    def issues(self) -> tuple[DiyCompatibilityCheck, ...]:
        return tuple(check for check in self.checks if check.status != "compatible")

    @property
    def blocked(self) -> bool:
        return bool(self.issues)

    def checks_as_dicts(self) -> list[dict[str, Any]]:
        return [check.as_dict() for check in self.checks]

    def as_payload(self) -> dict[str, Any]:
        """Return the stable API shape used for blocked order responses."""
        return {
            "configuration_id": self.rules.configuration_id,
            "configuration_version": self.rules.configuration_version,
            "rules_version": self.rules.version,
            "status": self.status,
            "issues": [issue.as_dict() for issue in self.issues],
        }


def get_diy_compatibility_rules(
    configuration_id: str,
    configuration_version: int,
) -> DiyCompatibilityRuleSet | None:
    """Resolve the compatibility rule set for a configuration version."""
    # The current catalog has one configuration version.  Keeping this lookup
    # explicit makes future rule changes additive instead of silently changing
    # the meaning of an existing order snapshot.
    if configuration_id != "diy-pc" or configuration_version != 1:
        return None
    return DiyCompatibilityRuleSet(
        configuration_id=configuration_id,
        configuration_version=configuration_version,
        version=DIY_COMPATIBILITY_RULES_VERSION,
        min_psu_headroom_w=MIN_PSU_HEADROOM_W,
    )


_NUMBER_RE = re.compile(r"(\d+(?:\.\d+)?)")
_MEMORY_RE = re.compile(r"DDR\s*([2345])", re.IGNORECASE)


def _specs(product: Product | None) -> Mapping[str, Any]:
    specs = getattr(product, "specs", None)
    return specs if isinstance(specs, Mapping) else {}


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _number(value: Any) -> Decimal | None:
    match = _NUMBER_RE.search(_text(value))
    return Decimal(match.group(1)) if match else None


def _socket(product: Product | None) -> str | None:
    value = _text(_specs(product).get("socket"))
    return value.upper().replace(" ", "") or None


def _memory_types(value: Any) -> set[str]:
    return {f"DDR{match.group(1)}" for match in _MEMORY_RE.finditer(_text(value))}


def _form_factors(value: Any) -> set[str]:
    aliases = {
        "EATX": "E-ATX",
        "E-ATX": "E-ATX",
        "EXTENDEDATX": "E-ATX",
        "EXTENDED-ATX": "E-ATX",
        "ATX": "ATX",
        "MATX": "M-ATX",
        "M-ATX": "M-ATX",
        "MICROATX": "M-ATX",
        "MICRO-ATX": "M-ATX",
        "ITX": "ITX",
        "MINIITX": "ITX",
        "MINI-ITX": "ITX",
    }
    values = re.split(r"[/,|;]+", _text(value).upper())
    result: set[str] = set()
    for raw_value in values:
        compact = raw_value.strip().replace(" ", "")
        if compact in aliases:
            result.add(aliases[compact])
    return result


def _is_liquid_cooler(product: Product | None) -> bool:
    text = " ".join(
        _text(_specs(product).get(key)).lower()
        for key in ("type", "radiator")
    )
    return any(marker in text for marker in ("水冷", "liquid", "aio", "radiator"))


def _rule(
    *,
    rule_id: str,
    key: str,
    title: str,
    status: CompatibilityStatus,
    message: str,
    remediation: str,
    parts: tuple[str, ...],
) -> DiyCompatibilityCheck:
    return DiyCompatibilityCheck(
        rule_id=rule_id,
        key=key,
        title=title,
        status=status,
        message=message,
        remediation=remediation,
        parts=parts,
    )


def _socket_check(products: Mapping[str, Product]) -> DiyCompatibilityCheck:
    cpu_socket = _socket(products.get("cpu"))
    motherboard_socket = _socket(products.get("motherboard"))
    if not cpu_socket or not motherboard_socket:
        return _rule(
            rule_id="DIY-CPU-MOTHERBOARD-SOCKET",
            key="cpu-mobo",
            title="CPU / motherboard socket",
            status="unverified",
            message=f"CPU socket {cpu_socket or 'missing'}; motherboard socket {motherboard_socket or 'missing'}.",
            remediation="Choose parts with verified socket data, or refresh the catalog before ordering.",
            parts=("cpu", "motherboard"),
        )
    if cpu_socket != motherboard_socket:
        return _rule(
            rule_id="DIY-CPU-MOTHERBOARD-SOCKET",
            key="cpu-mobo",
            title="CPU / motherboard socket",
            status="incompatible",
            message=f"CPU socket {cpu_socket} does not match motherboard socket {motherboard_socket}.",
            remediation="Replace the CPU or motherboard so both parts use the same socket.",
            parts=("cpu", "motherboard"),
        )
    return _rule(
        rule_id="DIY-CPU-MOTHERBOARD-SOCKET",
        key="cpu-mobo",
        title="CPU / motherboard socket",
        status="compatible",
        message=f"CPU and motherboard both use socket {cpu_socket}.",
        remediation="",
        parts=("cpu", "motherboard"),
    )


def _ram_check(products: Mapping[str, Product]) -> DiyCompatibilityCheck:
    ram_type = _memory_types(_specs(products.get("ram")).get("type"))
    motherboard_types = _memory_types(_specs(products.get("motherboard")).get("memory"))
    if not ram_type or not motherboard_types:
        return _rule(
            rule_id="DIY-RAM-MOTHERBOARD-TYPE",
            key="ram-mobo",
            title="RAM / motherboard memory type",
            status="unverified",
            message=f"RAM type {sorted(ram_type) or ['missing']}; motherboard support {sorted(motherboard_types) or ['missing']}.",
            remediation="Choose RAM and a motherboard with verified matching DDR type data.",
            parts=("ram", "motherboard"),
        )
    if not ram_type.intersection(motherboard_types):
        return _rule(
            rule_id="DIY-RAM-MOTHERBOARD-TYPE",
            key="ram-mobo",
            title="RAM / motherboard memory type",
            status="incompatible",
            message=f"RAM type {', '.join(sorted(ram_type))} is not supported by the motherboard ({', '.join(sorted(motherboard_types))}).",
            remediation="Replace the RAM or motherboard so they share a DDR type.",
            parts=("ram", "motherboard"),
        )
    return _rule(
        rule_id="DIY-RAM-MOTHERBOARD-TYPE",
        key="ram-mobo",
        title="RAM / motherboard memory type",
        status="compatible",
        message=f"RAM type {', '.join(sorted(ram_type))} is supported by the motherboard.",
        remediation="",
        parts=("ram", "motherboard"),
    )


def _form_factor_check(products: Mapping[str, Product]) -> DiyCompatibilityCheck:
    motherboard_form = _form_factors(_specs(products.get("motherboard")).get("form_factor"))
    case_support = _form_factors(_specs(products.get("case")).get("mb_support"))
    if not motherboard_form or not case_support:
        return _rule(
            rule_id="DIY-MOTHERBOARD-CASE-FORM-FACTOR",
            key="mobo-case",
            title="Motherboard / case form factor",
            status="unverified",
            message=f"Motherboard form factor {sorted(motherboard_form) or ['missing']}; case support {sorted(case_support) or ['missing']}.",
            remediation="Choose parts with verified motherboard form-factor and case-support data.",
            parts=("motherboard", "case"),
        )
    if not motherboard_form.intersection(case_support):
        return _rule(
            rule_id="DIY-MOTHERBOARD-CASE-FORM-FACTOR",
            key="mobo-case",
            title="Motherboard / case form factor",
            status="incompatible",
            message=f"Motherboard form factor {', '.join(sorted(motherboard_form))} is not supported by the case ({', '.join(sorted(case_support))}).",
            remediation="Replace the motherboard or case so the case supports the motherboard form factor.",
            parts=("motherboard", "case"),
        )
    return _rule(
        rule_id="DIY-MOTHERBOARD-CASE-FORM-FACTOR",
        key="mobo-case",
        title="Motherboard / case form factor",
        status="compatible",
        message=f"Case supports motherboard form factor {', '.join(sorted(motherboard_form))}.",
        remediation="",
        parts=("motherboard", "case"),
    )


def _gpu_length_check(products: Mapping[str, Product]) -> DiyCompatibilityCheck:
    gpu_length = _number(_specs(products.get("gpu")).get("length"))
    case_limit = _number(_specs(products.get("case")).get("gpu_length"))
    if gpu_length is None or case_limit is None:
        return _rule(
            rule_id="DIY-GPU-CASE-LENGTH",
            key="gpu-case",
            title="GPU / case length",
            status="unverified",
            message=f"GPU length {gpu_length or 'missing'}mm; case limit {case_limit or 'missing'}mm.",
            remediation="Choose a GPU and case with verified length limits before ordering.",
            parts=("gpu", "case"),
        )
    remaining = case_limit - gpu_length
    if remaining < 0:
        return _rule(
            rule_id="DIY-GPU-CASE-LENGTH",
            key="gpu-case",
            title="GPU / case length",
            status="incompatible",
            message=f"GPU length {gpu_length}mm exceeds the case limit of {case_limit}mm by {-remaining}mm.",
            remediation="Choose a shorter GPU or a case with at least the GPU's length clearance.",
            parts=("gpu", "case"),
        )
    return _rule(
        rule_id="DIY-GPU-CASE-LENGTH",
        key="gpu-case",
        title="GPU / case length",
        status="compatible",
        message=f"GPU fits with {remaining}mm of case length clearance.",
        remediation="",
        parts=("gpu", "case"),
    )


def _cooler_height_check(products: Mapping[str, Product]) -> DiyCompatibilityCheck:
    cooler_specs = _specs(products.get("cooler"))
    case_specs = _specs(products.get("case"))
    cooler_height = _number(cooler_specs.get("height"))
    case_limit = _number(case_specs.get("cooler_height"))

    # AIO products in the catalog do not have a tower height.  For those, the
    # same critical rule verifies the radiator size against the case's
    # radiator support; an absent dimension remains unverified.
    if cooler_height is None and _is_liquid_cooler(products.get("cooler")):
        radiator_size = _number(cooler_specs.get("radiator"))
        radiator_support = _text(case_specs.get("radiator_support"))
        supported_sizes = {
            Decimal(raw_value)
            for raw_value in _NUMBER_RE.findall(radiator_support)
        }
        if radiator_size is not None and radiator_size in supported_sizes:
            return _rule(
                rule_id="DIY-COOLER-CASE-HEIGHT",
                key="cooler-case",
                title="Cooler / case clearance",
                status="compatible",
                message=f"Liquid cooler radiator {radiator_size}mm is listed in the case radiator support.",
                remediation="",
                parts=("cooler", "case"),
            )
        return _rule(
            rule_id="DIY-COOLER-CASE-HEIGHT",
            key="cooler-case",
            title="Cooler / case clearance",
            status="unverified",
            message="Liquid cooler height is not applicable, but radiator fit could not be verified from catalog data.",
            remediation="Choose a cooler and case with matching verified radiator or height clearance data.",
            parts=("cooler", "case"),
        )

    if cooler_height is None or case_limit is None:
        return _rule(
            rule_id="DIY-COOLER-CASE-HEIGHT",
            key="cooler-case",
            title="Cooler / case clearance",
            status="unverified",
            message=f"Cooler height {cooler_height or 'missing'}mm; case limit {case_limit or 'missing'}mm.",
            remediation="Choose a cooler and case with verified height clearance data before ordering.",
            parts=("cooler", "case"),
        )
    if cooler_height > case_limit:
        return _rule(
            rule_id="DIY-COOLER-CASE-HEIGHT",
            key="cooler-case",
            title="Cooler / case clearance",
            status="incompatible",
            message=f"Cooler height {cooler_height}mm exceeds the case limit of {case_limit}mm.",
            remediation="Choose a shorter cooler or a case with more CPU-cooler clearance.",
            parts=("cooler", "case"),
        )
    return _rule(
        rule_id="DIY-COOLER-CASE-HEIGHT",
        key="cooler-case",
        title="Cooler / case clearance",
        status="compatible",
        message=f"Cooler fits with {case_limit - cooler_height}mm of height clearance.",
        remediation="",
        parts=("cooler", "case"),
    )


def _power_for_product(product: Product | None) -> Decimal:
    specs = _specs(product)
    if _text(specs.get("wattage")):
        return Decimal("0")
    tdp = _number(specs.get("tdp"))
    if tdp is not None:
        return tdp
    tdp_support = _number(specs.get("tdp_support"))
    if tdp_support is not None:
        return tdp_support * Decimal("0.15")
    # Preserve the existing frontend's conservative baseline for low-power
    # parts whose catalog entries do not expose a TDP.
    return Decimal("8")


def _power_check(
    products: Mapping[str, Product],
    rules: DiyCompatibilityRuleSet,
) -> tuple[DiyCompatibilityCheck, int | None, int | None]:
    psu_wattage = _number(_specs(products.get("psu")).get("wattage"))
    cpu_tdp = _number(_specs(products.get("cpu")).get("tdp"))
    gpu_tdp = _number(_specs(products.get("gpu")).get("tdp"))
    if psu_wattage is None or cpu_tdp is None or gpu_tdp is None:
        return (
            _rule(
                rule_id="DIY-PSU-HEADROOM",
                key="psu-power",
                title="PSU / system power headroom",
                status="unverified",
                message=f"PSU wattage {psu_wattage or 'missing'}W; CPU/GPU power data must be verified before calculating headroom.",
                remediation="Choose a PSU and CPU/GPU with verified wattage/TDP data before ordering.",
                parts=("cpu", "gpu", "psu"),
            ),
            None,
            None,
        )

    base_power = Decimal("60")
    for slot_id in ("cpu", "gpu", "motherboard", "ram", "ssd", "cooler", "case"):
        base_power += _power_for_product(products.get(slot_id))
    total_power = int(base_power.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    headroom = int((psu_wattage - total_power).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    if headroom < rules.min_psu_headroom_w:
        return (
            _rule(
                rule_id="DIY-PSU-HEADROOM",
                key="psu-power",
                title="PSU / system power headroom",
                status="incompatible",
                message=f"PSU headroom is {headroom}W; at least {rules.min_psu_headroom_w}W is required for an estimated {total_power}W system load.",
                remediation=f"Choose a PSU that provides at least {rules.min_psu_headroom_w}W of headroom over the estimated system load.",
                parts=("cpu", "gpu", "psu"),
            ),
            total_power,
            headroom,
        )
    return (
        _rule(
            rule_id="DIY-PSU-HEADROOM",
            key="psu-power",
            title="PSU / system power headroom",
            status="compatible",
            message=f"PSU headroom is {headroom}W for an estimated {total_power}W system load.",
            remediation="",
            parts=("cpu", "gpu", "psu"),
        ),
        total_power,
        headroom,
    )


def evaluate_diy_compatibility(
    products: Mapping[str, Product],
    *,
    configuration_id: str,
    configuration_version: int,
) -> DiyCompatibilityResult:
    """Evaluate all critical rules for one fully resolved DIY selection."""
    rules = get_diy_compatibility_rules(configuration_id, configuration_version)
    if rules is None:
        raise ValueError("Unsupported DIY compatibility configuration version")

    checks = [
        _socket_check(products),
        _ram_check(products),
        _form_factor_check(products),
        _gpu_length_check(products),
        _cooler_height_check(products),
    ]
    power_check, total_power_w, psu_headroom_w = _power_check(products, rules)
    checks.append(power_check)

    gpu_length = _number(_specs(products.get("gpu")).get("length"))
    case_gpu_limit = _number(_specs(products.get("case")).get("gpu_length"))
    gpu_space_headroom_mm = (
        int((case_gpu_limit - gpu_length).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        if gpu_length is not None and case_gpu_limit is not None
        else None
    )

    return DiyCompatibilityResult(
        rules=rules,
        checks=tuple(checks),
        total_power_w=total_power_w,
        psu_headroom_w=psu_headroom_w,
        gpu_space_headroom_mm=gpu_space_headroom_mm,
    )
