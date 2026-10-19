import argparse

from webcamfx.app import App

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="Effetti webcam attivati dai gesti")
    ap.add_argument("--camera", type=int, default=0, help="indice webcam (NON quello di OBS Virtual Camera)")
    App(ap.parse_args().camera).run()
