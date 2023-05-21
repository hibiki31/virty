from gunicorn.app.base import BaseApplication
from main import app

class Application(BaseApplication):
    def load_config(self):
        s = self.cfg.set
        s('bind', "0.0.0.0:8766")
        s('workers', 3)
        s('keepalive', 60)
        s('timeout', 600)
        s('accesslog', "-")
        s('access_log_format', '%(t)s %(h)s "%(r)s" %(s)s %(b)s %(D)s "%(a)s"')

    def load(self):
        return app

if __name__ == '__main__':
    Application().run()