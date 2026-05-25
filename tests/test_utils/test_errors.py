import pytest

from regiswitch.utils.errors import (
    RegiswitchError,
    NotInitializedError,
    ProfileNotFoundError,
    ProfileAlreadyExistsError,
    FileNotRegisteredError,
    FileAlreadyRegisteredError,
    NoActiveProfileError,
)


def test_all_errors_are_subclass_of_regiswitch_error():
    for cls in (
        NotInitializedError,
        ProfileNotFoundError,
        ProfileAlreadyExistsError,
        FileNotRegisteredError,
        FileAlreadyRegisteredError,
        NoActiveProfileError,
    ):
        assert issubclass(cls, RegiswitchError)


def test_error_message():
    exc = RegiswitchError("something went wrong")
    assert str(exc) == "something went wrong"


def test_not_initialized_error_raised():
    with pytest.raises(NotInitializedError):
        raise NotInitializedError("not init")


def test_profile_not_found_raised():
    with pytest.raises(ProfileNotFoundError):
        raise ProfileNotFoundError("missing")
