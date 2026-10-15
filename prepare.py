"""Download and verify the official register-DINO checkpoint and source."""
from utils import use_local_framework


def main():
    use_local_framework()
    import runpy
    from utils import FRAMEWORK_ROOT
    runpy.run_path(str(FRAMEWORK_ROOT / "prepare_vision_hybrid.py"), run_name="__main__")


if __name__ == "__main__":
    main()
