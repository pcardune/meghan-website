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

def download(url, filepath=None):
    if filepath is None:
        filepath = url.split('/')[-1]
    print "downloading %s to %s" % (url, filepath)
    open(filepath,'w').write(urllib2.urlopen(url).read())

def unzip(path):
    cmd("unzip -uq %s" % path)

@task
def getappengine():
    """Download Google App Engine"""
    if os.path.exists("google_appengine_1.2.7.zip"):
        cmd("rm google_appengine_1.2.7.zip")
    if os.path.isdir("google_appengine"):
        cmd("rm -rf google_appengine")
    open("google_appengine_1.2.7.zip","w").write(urllib2.urlopen("http://googleappengine.googlecode.com/files/google_appengine_1.2.7.zip").read())
    #cmd("wget http://googleappengine.googlecode.com/files/google_appengine_1.2.7.zip")
    cmd("unzip -uq google_appengine_1.2.7.zip")
    cmd("rm google_appengine_1.2.7.zip")

@task
def init():
    """Initialize everything so you can start working"""
    getappengine()

@task
def run():
    """Run the google app engine development server against gvr-online"""
    datastore = os.path.abspath(os.path.join(os.path.dirname(__file__), "data.datastore"))
    cmd("google_appengine/dev_appserver.py --enable_sendmail "
        "--address=0.0.0.0 --datastore_path=%s app" % datastore)

@task
def deploy():
    """Deploy to google app engine."""
    cmd("google_appengine/appcfg.py update app")
