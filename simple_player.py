from vpython import rate

from ctrl.player import Player


bvh_path = "res/walk.bvh"


def main():
    player = Player(bvh_path)
    player.mainloop()


if __name__ == "__main__":
    main()
