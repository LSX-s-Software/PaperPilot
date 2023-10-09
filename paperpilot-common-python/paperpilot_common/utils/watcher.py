from pathlib import Path

import watchfiles
from django.conf import settings
from django.utils import autoreload


class WatchfilesReloader(autoreload.BaseReloader):
    def tick(self):
        watcher = watchfiles.watch(*settings.WATCHFILES, debug=False)
        for file_changes in watcher:
            for _change, path in file_changes:
                self.notify_file_changed(Path(path))
            yield


def replaced_get_reloader() -> autoreload.BaseReloader:
    return WatchfilesReloader()


autoreload.get_reloader = replaced_get_reloader
