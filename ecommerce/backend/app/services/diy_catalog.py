"""Server-owned DIY configuration catalog used during checkout.

The frontend may reference these stable identifiers, but names, slot/category
rules, and surcharges are authoritative here.  Changing the catalog requires a
new configuration version so historical order snapshots remain explainable.
"""
from __future__ import annotations
from dataclasses import dataclass
from types import MappingProxyType
from typing import Mapping
from uuid import UUID


DIY_CONFIGURATION_ID = "diy-pc"
DIY_CONFIGURATION_VERSION = 1


@dataclass(frozen=True)
class DiySlot:
    id: str
    label: str
    category_id: UUID


@dataclass(frozen=True)
class DiyOption:
    id: str
    name: str
    surcharge_minor: int = 0


@dataclass(frozen=True)
class DiyConfiguration:
    id: str
    version: int
    name: str
    slots: Mapping[str, DiySlot]
    variants: Mapping[str, DiyOption]
    materials: Mapping[str, DiyOption]


_slots = (
    DiySlot("cpu", "\u5904\u7406\u5668 CPU", UUID("d1000000-0000-0000-0000-000000000001")),
    DiySlot("gpu", "\u663e\u5361 GPU", UUID("d1000000-0000-0000-0000-000000000002")),
    DiySlot("motherboard", "\u4e3b\u677f", UUID("d1000000-0000-0000-0000-000000000003")),
    DiySlot("ram", "\u5185\u5b58 RAM", UUID("d1000000-0000-0000-0000-000000000004")),
    DiySlot("ssd", "\u56fa\u6001\u786c\u76d8 SSD", UUID("d1000000-0000-0000-0000-000000000005")),
    DiySlot("cooler", "\u6563\u70ed\u5668", UUID("d1000000-0000-0000-0000-000000000006")),
    DiySlot("psu", "\u7535\u6e90 PSU", UUID("d1000000-0000-0000-0000-000000000007")),
    DiySlot("case", "\u673a\u7bb1", UUID("d1000000-0000-0000-0000-000000000008")),
)

DIY_CONFIGURATION = DiyConfiguration(
    id=DIY_CONFIGURATION_ID,
    version=DIY_CONFIGURATION_VERSION,
    name="\u80d6\u866b DIY \u6574\u673a\u914d\u7f6e",
    slots=MappingProxyType({slot.id: slot for slot in _slots}),
    variants=MappingProxyType({
        option.id: option for option in (
            DiyOption("black", "\u80d6\u866b\u9ed1"),
            DiyOption("silver", "\u661f\u7a7a\u94f6"),
            DiyOption("green", "\u866b\u7ffc\u7eff", 50_000),
        )
    }),
    materials=MappingProxyType({
        option.id: option for option in (
            DiyOption("matte", "\u54d1\u5149\u91d1\u5c5e"),
            DiyOption("satin", "\u7ec6\u7802\u9633\u6781"),
            DiyOption("gloss", "\u9ad8\u4eae\u6d82\u5c42"),
        )
    }),
)


def get_diy_configuration(configuration_id: str, version: int) -> DiyConfiguration | None:
    if configuration_id != DIY_CONFIGURATION.id or version != DIY_CONFIGURATION.version:
        return None
    return DIY_CONFIGURATION
