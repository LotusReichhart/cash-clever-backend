def test_user_status_enum_values():
    from src.domain.entities.user_entity import UserStatus
    assert UserStatus.ACTIVE.value == "active"
