import urllib
import urllib2
import os

from paver.easy import options, task

options(
    virtualenv=dict(
        script_name="bootstrap.py",
        paver_command_line="init",
        ))

def cmd(c, silent=False):
    if not silent:
        print c
    os.system(c)


APP_ENGINE_VERSION = '1.6.3'

@task
def getappengine():
    """Download Google App Engine"""
    zip_path = "google_appengine_"+APP_ENGINE_VERSION+".zip"
    if os.path.exists(zip_path):
        cmd("rm "+zip_path)
    if os.path.isdir("google_appengine"):
        cmd("rm -rf google_appengine")
    urllib.urlretrieve(
        "http://googleappengine.googlecode.com/files/google_appengine_"+APP_ENGINE_VERSION+".zip",
        zip_path)
    cmd("unzip -uq "+zip_path)
    cmd("rm "+zip_path)

@task
def init():
    """Initialize everything so you can start working"""
    getappengine()

@task
def run():
    """Run the google app engine development server against gvr-online"""
    datastore = os.path.abspath(os.path.join(os.path.dirname(__file__), "data.datastore"))
    cmd("python google_appengine/dev_appserver.py --enable_sendmail "
        "--address=0.0.0.0 --datastore_path=%s app" % datastore)

@task
def deploy():
    """Deploy to google app engine."""
    cmd("python google_appengine/appcfg.py update app")
