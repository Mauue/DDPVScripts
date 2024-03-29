from concurrent.futures import ThreadPoolExecutor
import subprocess


_dispatcher = None


def get_verifier_dispatcher():
    global _dispatcher
    if _dispatcher is None:
        _dispatcher = VerifierDispatcher()
    return _dispatcher


class VerifierDispatcher:

    def __init__(self):
        self._pool = ThreadPoolExecutor(max_workers=1)
        self._jar_path = r".\Coral-2.0.jar"

    def run(self, filepath, handle):
        self._pool.submit(self._run, filepath, handle)

    def _run(self, filepath, handle):
        process = subprocess.Popen(
            ["java", "-jar", self._jar_path, "GreenStart", "1", "--auto_parse_network", filepath],
            stdout=subprocess.PIPE, bufsize=10, universal_newlines=True
        )
        while True:
            buf = process.stdout.readline()
            if not buf :
                if process.poll() is not None:
                    break
                continue
            handle({"type": "result", "data": buf.strip()})
        handle({"type": "finish"})
