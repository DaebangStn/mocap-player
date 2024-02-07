import pytest

from ctrl.player import Player, Status


@pytest.fixture
def player():
    bvh_path = "C:/Users/geon/PycharmProjects/mocap-player/res/a_001_1_1.bvh"
    return Player(bvh_path)


class TestPlayer:
    def test_init(self, player):
        assert player is not None

    def test_button_callback(self, player):
        player.status = Status.Unloaded

        player._start_player(None)
        assert player.status == Status.Unloaded

        player._stop_player(None)
        assert player.status == Status.Unloaded

        player._load_and_configure_model(None)
        assert player.status == Status.Stopped
