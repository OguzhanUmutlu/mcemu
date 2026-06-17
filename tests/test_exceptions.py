from mcemu.exceptions import CommandReturn


def test_command_return():
    exc = CommandReturn(42)
    assert exc.value == 42
    assert isinstance(exc, Exception)
