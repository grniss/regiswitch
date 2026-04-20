from regiswitch.utils.errors import (
    EXIT_INPUT_ERROR,
    EXIT_OK,
    EXIT_RUNTIME_ERROR,
    FileAlreadyRegisteredError,
    FileNotRegisteredError,
    NoActiveProfileError,
    ProfileAlreadyExistsError,
    ProfileNotFoundError,
    RegiswitchError,
)


def test_exit_code_constants():
    assert EXIT_OK == 0
    assert EXIT_INPUT_ERROR == 1
    assert EXIT_RUNTIME_ERROR == 2


def test_regiswitch_error_default_exit_code():
    err = RegiswitchError("oops")
    assert err.exit_code == EXIT_RUNTIME_ERROR
    assert str(err) == "oops"


def test_regiswitch_error_custom_exit_code():
    err = RegiswitchError("bad input", EXIT_INPUT_ERROR)
    assert err.exit_code == EXIT_INPUT_ERROR


def test_profile_not_found_exit_code():
    err = ProfileNotFoundError("dev")
    assert err.exit_code == EXIT_INPUT_ERROR
    assert "dev" in str(err)


def test_profile_already_exists_exit_code():
    err = ProfileAlreadyExistsError("dev")
    assert err.exit_code == EXIT_INPUT_ERROR
    assert "dev" in str(err)


def test_file_not_registered_exit_code():
    err = FileNotRegisteredError("/etc/hosts")
    assert err.exit_code == EXIT_INPUT_ERROR
    assert "/etc/hosts" in str(err)


def test_file_already_registered_exit_code():
    err = FileAlreadyRegisteredError("/etc/hosts")
    assert err.exit_code == EXIT_INPUT_ERROR
    assert "/etc/hosts" in str(err)


def test_no_active_profile_exit_code():
    err = NoActiveProfileError()
    assert err.exit_code == EXIT_INPUT_ERROR
