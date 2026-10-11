"""Regression tests for API route ordering."""

from app.main import app


def test_product_static_routes_are_registered_before_uuid_detail_route():
    paths = [route.path for route in app.router.routes]

    detail_index = paths.index("/api/products/{product_id}")
    assert paths.index("/api/products/slug/{slug}") < detail_index
    assert paths.index("/api/products/featured/list") < detail_index
    assert paths.index("/api/products/hot/list") < detail_index
    assert paths.index("/api/products/commerce-settings") < detail_index


def test_mock_payment_route_is_sandbox_only():
    paths = [route.path for route in app.router.routes]

    assert "/api/payment/sandbox/mock-pay/{order_id}" in paths
    assert "/api/payment/mock-pay/{order_id}" not in paths


def test_admin_asset_upload_route_is_registered():
    route = next(route for route in app.router.routes if route.path == "/api/admin/assets")
    assert "POST" in route.methods


def test_admin_asset_library_routes_are_registered():
    methods_by_path = {}
    for route in app.router.routes:
        methods = getattr(route, "methods", None)
        if methods:
            methods_by_path.setdefault(route.path, set()).update(methods)

    assert {"GET", "POST"} <= methods_by_path["/api/admin/assets"]
    assert "DELETE" in methods_by_path["/api/admin/assets/{asset_path:path}"]


def test_order_create_route_keeps_its_public_path_and_response_contract():
    route = next(route for route in app.router.routes if route.path == "/api/orders" and "POST" in route.methods)

    assert route.status_code == 201
    assert route.response_model.__name__ == "OrderResponse"
