from app.api.admin import _has_valid_signature


def test_glb_signature_requires_version_two():
    valid = b"glTF" + (2).to_bytes(4, "little") + (12).to_bytes(4, "little")
    invalid = b"glTF" + (1).to_bytes(4, "little") + (12).to_bytes(4, "little")
    assert _has_valid_signature(valid, ".glb") is True
    assert _has_valid_signature(invalid, ".glb") is False


def test_image_signatures_do_not_trust_extensions_only():
    assert _has_valid_signature(b"\x89PNG\r\n\x1a\ncontent", ".png") is True
    assert _has_valid_signature(b"not really a png", ".png") is False
