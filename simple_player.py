from vpython import rate

from ctrl.player import Player


bvh_path = "C:/Users/geon/PycharmProjects/mocap-player/res/a_001_1_1.bvh"


def main():
    player = Player(bvh_path)
    player.mainloop()


if __name__ == "__main__":
    main()
