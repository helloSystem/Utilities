import os
import psutil


def get_application_name(p):
    try:
        environ = p.environ()
    except psutil.AccessDenied:
        environ = None
    if environ and "LAUNCHED_BUNDLE" in environ:
        return os.path.basename(environ["LAUNCHED_BUNDLE"]).rsplit(".", 1)[0]
    else:
        return p.name()
