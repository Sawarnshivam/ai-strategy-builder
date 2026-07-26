"""Signup, login, and current-user endpoints."""

from fastapi import APIRouter, Depends, status

from app.api.deps import get_auth_service, get_current_user
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    SignupRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/signup",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new account",
)
def signup(
    body: SignupRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Create an account and return an access token."""
    _, token = service.signup(body)
    return TokenResponse(access_token=token)


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Log in and receive a token",
)
def login(
    body: LoginRequest,
    service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """Authenticate and return an access token."""
    return TokenResponse(access_token=service.login(body))


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get the current user",
)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    """Return the authenticated user's profile."""
    return UserResponse.model_validate(current_user)