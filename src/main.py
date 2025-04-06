from viewer_with_button import Open3DViewer
from data_manager import DataManager


def main():
    data_manager = DataManager()

    viewer = Open3DViewer(data_manager)
    viewer.run()


if __name__ == "__main__":
    main()
