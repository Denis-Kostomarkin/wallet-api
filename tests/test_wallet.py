import asyncio
from decimal import Decimal
from uuid import uuid4

import pytest


class TestWalletAPI:
    @pytest.mark.asyncio
    async def test_get_wallet_not_found(self, client):
        response = await client.get(f"/api/v1/wallets/{uuid4()}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Wallet not found"

    @pytest.mark.asyncio
    async def test_deposit_new_wallet(self, client):
        wallet_id = uuid4()
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "DEPOSIT", "amount": "1000.00"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(wallet_id)
        assert Decimal(data["balance"]) == Decimal("1000.00")

    @pytest.mark.asyncio
    async def test_deposit_existing_wallet(self, client):
        wallet_id = uuid4()
        await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "DEPOSIT", "amount": "1000.00"}
        )
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "DEPOSIT", "amount": "500.50"}
        )
        assert response.status_code == 200
        assert Decimal(response.json()["balance"]) == Decimal("1500.50")

    @pytest.mark.asyncio
    async def test_withdraw_success(self, client):
        wallet_id = uuid4()
        await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "DEPOSIT", "amount": "1000.00"}
        )
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "WITHDRAW", "amount": "300.00"}
        )
        assert response.status_code == 200
        assert Decimal(response.json()["balance"]) == Decimal("700.00")

    @pytest.mark.asyncio
    async def test_withdraw_insufficient_funds(self, client):
        wallet_id = uuid4()
        await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "DEPOSIT", "amount": "100.00"}
        )
        response = await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "WITHDRAW", "amount": "200.00"}
        )
        assert response.status_code == 400
        assert "Insufficient funds" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_withdraw_wallet_not_found(self, client):
        response = await client.post(
            f"/api/v1/wallets/{uuid4()}/operation",
            json={"operation_type": "WITHDRAW", "amount": "100.00"}
        )
        assert response.status_code == 400
        assert "Wallet not found" in response.json()["detail"]

    @pytest.mark.asyncio
    async def test_invalid_operation_type(self, client):
        response = await client.post(
            f"/api/v1/wallets/{uuid4()}/operation",
            json={"operation_type": "INVALID", "amount": "100.00"}
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_negative_amount(self, client):
        response = await client.post(
            f"/api/v1/wallets/{uuid4()}/operation",
            json={"operation_type": "DEPOSIT", "amount": "-100.00"}
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_concurrent_deposits(self, client):
        wallet_id = uuid4()
        await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "DEPOSIT", "amount": "1000.00"}
        )

        async def deposit():
            return await client.post(
                f"/api/v1/wallets/{wallet_id}/operation",
                json={"operation_type": "DEPOSIT", "amount": "100.00"}
            )

        tasks = [deposit() for _ in range(10)]
        responses = await asyncio.gather(*tasks)

        for r in responses:
            assert r.status_code == 200

        final = await client.get(f"/api/v1/wallets/{wallet_id}")
        assert Decimal(final.json()["balance"]) == Decimal("2000.00")

    @pytest.mark.asyncio
    async def test_concurrent_withdrawals(self, client):
        wallet_id = uuid4()
        await client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "DEPOSIT", "amount": "1000.00"}
        )

        async def withdraw():
            return await client.post(
                f"/api/v1/wallets/{wallet_id}/operation",
                json={"operation_type": "WITHDRAW", "amount": "100.00"}
            )

        tasks = [withdraw() for _ in range(10)]
        responses = await asyncio.gather(*tasks)

        success_count = sum(1 for r in responses if r.status_code == 200)
        fail_count = sum(1 for r in responses if r.status_code == 400)

        assert success_count + fail_count == 10
        assert success_count <= 10

        final = await client.get(f"/api/v1/wallets/{wallet_id}")
        final_balance = Decimal(final.json()["balance"])
        assert final_balance == Decimal("1000.00") - Decimal(str(success_count * 100))
