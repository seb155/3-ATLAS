"""
Temporary auth module for Phase 1.
Provides mock authentication until proper auth is implemented.
"""



from fastapi import Header


class MockUser:
    """Mock user for Phase 1 development."""

    def __init__(self, user_id: str = "dev-user"):
        self.id = user_id
        self.username = "Developer"
        self.email = "dev@axoiq.com"


async def get_current_user(authorization: str | None = Header(None)) -> MockUser:
    """
    Mock authentication function for Phase 1.
    Returns a mock user without requiring actual authentication.

    TODO: Implement proper JWT authentication in Phase 2.
    """
    return MockUser()
