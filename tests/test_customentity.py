#!/usr/bin/env python3

import pytest

from ngsildclient.api.custom_client import CustomClient

token = "eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0eXBlIjoiYWRtaW5TeXN0ZW0iLCJ1c2VySWQiOiJhZG1pbiIsIm5pY2tuYW1lIjoiYWRtaW4iLCJlbWFpbCI6ImFkbWluQHRlc3QuY29tIiwicm9sZSI6IlN5c3RlbV9BZG1pbiIsImlhdCI6MTcxOTg5NDI2MCwiZXhwIjoxNzE5ODk3ODYwLCJhdWQiOiI0RTdRWFVmY1Q4YU9OTkN3Ynp2diIsImlzcyI6InVybjpkYXRhaHViOmNpdHlodWI6c2VjdXJpdHkifQ.O_5k-GSUANgM1MIOQoMfh48DbSdbsCQC8SoA-wft6mHGiYQuTetmWt4ZwL3Cn4ygnvn_dDVTn4YenHmA9fKUjW5FATNQE7tFn-JVX55kbZOtXS-OqVtuszQYbQ7pdK7y1yjGf-GV5GpDJPuL4TobJ1C41lW_pbek2L6cdboBTxlEWIr12rkQLvVbHTBLDZYcocl3AGRZcGfmtNEtxSlURly1mhozNwkUB-PqeLMywS0qPT17La-H050Vf9n9xrMmURLquJRjRbsGZ5Bl4SE7pSGxtGuIqVnRyraZ9ZjiZ-rFOzEjDtcOooeoTbEmH9zY1kf6ax0ni8YRR1eLhgn3iw"

@pytest.mark.parametrize("hostname, port, token, entityId, expected", [
    ("172.31.13.226", 8085, token, "urn:datahub:KwaterSensor:ecobot00006", 200),
])

def test_custom_getEntity(hostname, port, token, entityId, expected):
    # Create a CustomClient instance
    client = CustomClient(hostname = hostname, port=port, token=token)

    # Entity query using the overridden get method
    response = client.get(entityId)
    # response = client.get("urn:datahub:KwaterSensor:ecobot00006")

    print(response.json)

    assert response.status_code == expected