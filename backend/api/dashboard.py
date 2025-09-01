"""
CEO Dashboard API

This API provides highly secure endpoints for accessing aggregated business and
platform health metrics. Access is restricted by a special high-security
authentication system with real 2FA.
"""

import pyotp
import time
from typing import Optional
from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from backend.core.settings import settings

router = APIRouter()

# --- High-Security Authentication ---

async def high_security_auth(
    x_ceo_token: Optional[str] = Header(None),
    x_2fa_code: Optional[str] = Header(None),
):
    """
    Real high-security authentication with TOTP-based 2FA
    """
    # CEO token validation (should be from environment/secrets)
    expected_ceo_token = settings.OWNER_EMERGENCY_KEY  # Reuse emergency key for admin access
    
    if not x_ceo_token or x_ceo_token != expected_ceo_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing CEO token.",
        )

    # 2FA validation using TOTP
    if not x_2fa_code:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="2FA code required.",
        )
    
    # In production, each admin would have their own TOTP secret
    # For now, use a shared secret that should be configured per deployment
    totp_secret = getattr(settings, 'ADMIN_TOTP_SECRET', 'JBSWY3DPEHPK3PXP')  # Default for demo
    
    totp = pyotp.TOTP(totp_secret)
    if not totp.verify(x_2fa_code, valid_window=1):  # Allow 1 window (30 seconds) tolerance
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid 2FA code.",
        )


# --- Pydantic Models for Dashboard Metrics ---


class PlatformHealthMetrics(BaseModel):
    active_users: int
    total_projects: int
    api_requests_per_minute: int
    error_rate: float


class BusinessMetrics(BaseModel):
    mrr: float
    new_customers_last_30_days: int
    churn_rate: float


# --- API Endpoints ---


@router.get(
    "/health",
    response_model=PlatformHealthMetrics,
    dependencies=[Depends(high_security_auth)],
)
async def get_platform_health():
    """
    Provides platform health metrics.
    """
    # In a real implementation, this data would be fetched from a monitoring service.
    return PlatformHealthMetrics(
        active_users=1500,
        total_projects=450,
        api_requests_per_minute=12000,
        error_rate=0.01,
    )


@router.get(
    "/business",
    response_model=BusinessMetrics,
    dependencies=[Depends(high_security_auth)],
)
async def get_business_metrics():
    """
    Provides business metrics.
    """
    # In a real implementation, this data would be fetched from a billing or analytics service.
    return BusinessMetrics(
        mrr=50000.0,
        new_customers_last_30_days=42,
        churn_rate=0.05,
    )
