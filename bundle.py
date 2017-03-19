import sys
import os
import logging

import disunity
import pynity

log = logging.getLogger()

class BundleApp(disunity.RecursiveFileApp):

    def __init__(self):
        super().__init__()

        self.cmd = None

    def parse_args(self, argv):
        if not argv:
            return False

        self.cmd = argv.pop(0).lower()
        if self.cmd not in ("x", "l"):
            return False

        return len(argv) > 0

    def usage(self):
        print("Usage: %s <command> [file...]" % os.path.basename(self.path))

    def process(self, path):
        print(path)

        path_out, _ = os.path.splitext(path)
        if path_out == path:
            path_out += "_"

        with pynity.ArchiveFile.open(path) as archive:
            if self.cmd == "l":
                # list files
                print("% 12s  %s" % ("Size", "Name"))
                print("%s  %s" % ("-" * 12, "-" * 48))
                for entry in archive.entries:
                    print("% 12d  %s" % (entry.size, entry.path))
            elif self.cmd == "x":
                # extract files
                for entry in archive.entries:
                    print(entry.path)

                    # append output path
                    entry_path = os.path.join(path_out, entry.path)

                    # block path traversal attempts
                    entry_path = os.path.abspath(entry_path)
                    common_prefix = os.path.commonprefix([entry_path, path_out])

                    if common_prefix != path_out:
                        log.warning("Blocked path traversal attempt: '%s'" % entry.path)
                        continue

                    # create directories
                    os.makedirs(os.path.dirname(entry_path), exist_ok=True)

                    entry.extract(entry_path)
            else:
                # validation went wrong
                assert False

if __name__ == "__main__":
    sys.exit(BundleApp().main(sys.argv))