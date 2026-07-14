"""Small, dependency-free GLB validation helpers for catalog uploads."""
from dataclasses import asdict, dataclass
import json
import re
import struct
from typing import Any, Optional


DIY_CASE_CONTRACT = "diy-case-v1"
DIY_MODEL_PART_KEYS = (
    "case",
    "motherboard",
    "cpu",
    "gpu",
    "ram",
    "ssd",
    "cooler",
    "psu",
)

_ALIASES = {
    "mobo": "motherboard",
    "mainboard": "motherboard",
    "memory": "ram",
    "storage": "ssd",
    "nvme": "ssd",
    "heatsink": "cooler",
    "aio": "cooler",
    "power": "psu",
    "chassis": "case",
}
_GLB_HEADER = struct.Struct("<4sII")
_GLB_CHUNK_HEADER = struct.Struct("<II")
_JSON_CHUNK_TYPE = 0x4E4F534A


class InvalidGlb(ValueError):
    """Raised when an uploaded file is not a structurally valid GLB 2.0 file."""


@dataclass(frozen=True)
class GlbContractReport:
    contract: str
    node_names: tuple[str, ...]
    found: tuple[str, ...]
    missing: tuple[str, ...]
    empty: tuple[str, ...]

    @property
    def valid(self) -> bool:
        return not self.missing and not self.empty

    def to_dict(self) -> dict[str, Any]:
        return {**asdict(self), "valid": self.valid}


def normalize_diy_part_key(name: str) -> Optional[str]:
    normalized = re.sub(r"^diy[-_]", "", str(name or "").strip().lower())
    for token in filter(None, re.split(r"[^a-z0-9]+", normalized)):
        candidate = _ALIASES.get(token, token)
        if candidate in DIY_MODEL_PART_KEYS:
            return candidate
    return None


def inspect_glb(data: bytes, contract: str = DIY_CASE_CONTRACT) -> GlbContractReport:
    """Parse the JSON chunk and report the named DIY nodes present in a GLB."""
    if len(data) < _GLB_HEADER.size:
        raise InvalidGlb("GLB 文件头不完整")

    magic, version, declared_length = _GLB_HEADER.unpack_from(data)
    if magic != b"glTF" or version != 2:
        raise InvalidGlb("仅支持 GLB 2.0")
    if declared_length != len(data):
        raise InvalidGlb("GLB 文件长度与文件头不一致")

    offset = _GLB_HEADER.size
    document = None
    while offset < len(data):
        if offset + _GLB_CHUNK_HEADER.size > len(data):
            raise InvalidGlb("GLB Chunk 头不完整")
        chunk_length, chunk_type = _GLB_CHUNK_HEADER.unpack_from(data, offset)
        offset += _GLB_CHUNK_HEADER.size
        chunk_end = offset + chunk_length
        if chunk_end > len(data):
            raise InvalidGlb("GLB Chunk 超出文件边界")
        if chunk_type == _JSON_CHUNK_TYPE and document is None:
            try:
                payload = data[offset:chunk_end].decode("utf-8").rstrip(" \t\r\n\x00")
                document = json.loads(payload)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise InvalidGlb("GLB JSON Chunk 无法解析") from exc
        offset = chunk_end

    if offset != len(data) or not isinstance(document, dict):
        raise InvalidGlb("GLB 缺少有效 JSON Chunk")

    nodes = document.get("nodes", [])
    if not isinstance(nodes, list):
        raise InvalidGlb("GLB nodes 字段格式错误")
    node_names = tuple(
        node.get("name", "").strip()
        for node in nodes
        if isinstance(node, dict) and isinstance(node.get("name"), str) and node.get("name", "").strip()
    )
    indices_by_part = {key: [] for key in DIY_MODEL_PART_KEYS}
    for index, node in enumerate(nodes):
        if not isinstance(node, dict):
            continue
        part_key = normalize_diy_part_key(node.get("name", ""))
        if part_key:
            indices_by_part[part_key].append(index)

    found = tuple(key for key in DIY_MODEL_PART_KEYS if indices_by_part[key])
    missing = tuple(key for key in DIY_MODEL_PART_KEYS if not indices_by_part[key])
    empty = tuple(
        key
        for key in found
        if not any(_node_has_mesh(nodes, index) for index in indices_by_part[key])
    )
    return GlbContractReport(
        contract=contract,
        node_names=node_names,
        found=found,
        missing=missing,
        empty=empty,
    )


def _node_has_mesh(nodes: list, index: int, visited: Optional[set] = None) -> bool:
    if index < 0 or index >= len(nodes):
        return False
    visited = visited or set()
    if index in visited:
        return False
    visited.add(index)

    node = nodes[index]
    if not isinstance(node, dict):
        return False
    if isinstance(node.get("mesh"), int):
        return True
    children = node.get("children", [])
    if not isinstance(children, list):
        return False
    return any(
        isinstance(child, int) and _node_has_mesh(nodes, child, visited)
        for child in children
    )
