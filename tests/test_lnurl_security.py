import json
from datetime import datetime, timedelta
from ipaddress import ip_address
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from lnbits.core.services import lnurl as core_lnurl
from lnbits.settings import settings
from starlette.exceptions import HTTPException

from .. import views_api as views


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
def game_route(monkeypatch):
    payment = SimpleNamespace(payment_hash="payment-hash", bolt11="invoice")
    create = AsyncMock(return_value=payment)
    monkeypatch.setattr(views, "create_invoice", create)
    monkeypatch.setattr(settings, "lnbits_callback_url_rules", [])
    monkeypatch.setattr(settings, "lnbits_lnurl_allow_private_ips", False)
    monkeypatch.setattr(
        views,
        "get_game",
        AsyncMock(
            return_value=SimpleNamespace(
                completed=False,
                closing_date=datetime.now() + timedelta(hours=2),
                buy_in_max=100,
                odds=10,
                wallet="wallet",
                name="game",
            )
        ),
    )
    data = SimpleNamespace(
        game_id="game", ln_address="alice@pay.example", buy_in=21, block_number=5
    )
    route = views.api_create_player
    return route, data, create


@pytest.mark.anyio
async def test_private_lnurl_rejected_before_invoice(game_route, monkeypatch):
    route, data, create = game_route
    assert views.lnurl_handle is core_lnurl.handle
    monkeypatch.setattr(
        core_lnurl,
        "_resolve_lnurl_host",
        AsyncMock(return_value=[ip_address("127.0.0.1")]),
    )
    send = AsyncMock()
    monkeypatch.setattr(core_lnurl, "_send_lnurl_request", send)
    with pytest.raises(HTTPException) as exc:
        await route(data)
    assert exc.value.status_code == 400
    create.assert_not_awaited()
    send.assert_not_awaited()


@pytest.mark.anyio
async def test_public_lnurl_preserves_invoice_amount_wallet_and_metadata(
    game_route, monkeypatch
):
    route, data, create = game_route
    monkeypatch.setattr(
        core_lnurl,
        "_resolve_lnurl_host",
        AsyncMock(return_value=[ip_address("93.184.216.34")]),
    )
    response = {
        "tag": "payRequest",
        "callback": "https://pay.example/callback",
        "minSendable": 1000,
        "maxSendable": 100000000,
        "metadata": '[["text/plain","Test payment"]]',
    }
    monkeypatch.setattr(
        core_lnurl,
        "_send_lnurl_request",
        AsyncMock(return_value=(200, {}, json.dumps(response).encode())),
    )
    result = await route(data)
    assert result == {"payment_hash": "payment-hash", "payment_request": "invoice"}
    args = create.await_args.kwargs
    assert args["wallet_id"] == "wallet"
    assert args["amount"] == 21
    assert args["extra"] == {
        "tag": "numberlottery",
        "ln_address": data.ln_address,
        "game_id": "game",
        "block_number": 5,
    }
