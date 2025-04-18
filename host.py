from engine import VoxelEngine
import socket

class Host:
    def __init__(self):
        self.app = VoxelEngine()
    
    def run(self):
        self.app.run()

if __name__ == "__main__":
    app = Host()
    app.run()