"""Pydantic schema for the simple lease extraction example."""

from datetime import date

from pydantic import BaseModel, Field


class SimpleLeaseDetails(BaseModel):
    """Simple schema for lease details extraction."""

    landlord: str | None = Field(None, description="Name of the landlord")
    tenant: str | None = Field(None, description="Name of the tenant")
    landlord_address: str | None = Field(None, description="Address of the landlord")
    tenant_address: str | None = Field(
        None,
        description="Address of the tenant. If not provided, use the property address.",
    )
    property_address: str | None = Field(
        None, description="Address of the leased property"
    )
    property_postcode: str | None = Field(
        None, description="Postcode of the leased property"
    )
    lease_start_date: date | None = Field(
        None, description="Start date of the lease, in ISO format (YYYY-MM-DD)"
    )
    lease_end_date: date | None = Field(
        None, description="End date of the lease, in ISO format (YYYY-MM-DD)"
    )
    rent_amount: int | None = Field(None, description="Amount of rent")
    rent_period: str | None = Field(
        None, description="Period of the rent (e.g., per annum)"
    )
    deposit_amount: int | None = Field(None, description="Amount of deposit")
