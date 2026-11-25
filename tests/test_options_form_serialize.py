"""The options forms must load in the frontend (issue 27).

The flow tests call the flow directly, which never turns the form schema into
the field list the frontend gets. Home Assistant does that only in its HTTP
view, and a validator it can't describe (a plain function) makes the request
fail with "unable to serialize schema". So these go through the HTTP API.
"""

from __future__ import annotations

import pytest
from homeassistant.core import HomeAssistant
from homeassistant.setup import async_setup_component
from pytest_homeassistant_custom_component.common import MockConfigEntry


@pytest.mark.parametrize("step_id", ["globalopts", "calibration1_global"])
async def test_options_form_loads_over_http(
    hass: HomeAssistant, hass_client, setup_bermuda_entry: MockConfigEntry, step_id: str
):
    assert await async_setup_component(hass, "config", {})
    client = await hass_client()

    resp = await client.post(
        "/api/config/config_entries/options/flow",
        json={"handler": setup_bermuda_entry.entry_id},
    )
    assert resp.status == 200
    flow_id = (await resp.json())["flow_id"]

    resp = await client.post(
        f"/api/config/config_entries/options/flow/{flow_id}",
        json={"next_step_id": step_id},
    )
    assert resp.status == 200, await resp.text()
    data = await resp.json()
    assert data["type"] == "form"
    assert data["step_id"] == step_id
    names = {field["name"] for field in data["data_schema"]}
    assert {"attenuation", "ref_power"} <= names
