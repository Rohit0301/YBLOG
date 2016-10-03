# -*- coding: utf-8 -*-
"""
Created on Mon Jun 20 22:17:37 2016

@author: Administrator
"""

import os
COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from app import create_app, db
from app.models import Follower, Comment, Post, Message, Administrator
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate, MigrateCommand

app = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(app)
migrate = Migrate(app, db)

#帮shell自动载入应用的上下文
def make_shell_context():
    return dict(app=app, db=db, Follower=Follower, Comment=Comment, Post=Post, 
                Message=Message, Admin=Administrator)
manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def add_post():
    Post.add_post()


@manager.command
def update_post():
    Post.update_post()


@manager.command
def test(coverage=False):
    """Run the unit tests."""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        COV.html_report(directory=covdir)
        print('HTML version: file://%s/index.html' % covdir)
        COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    """Run deployment tasks."""
    from flask.ext.migrate import upgrade
    # migrate database to latest revision
    upgrade()
    
    #add blogs
    Post.add_post()
    
    #add admin
    if not Administrator.query.all():
        pwd = os.environ.get['ADMIN_PWD'] or '1111'
        admin = Administrator(pwd)
        db.session.add(admin)
        db.session.commit()


if __name__ == '__main__':
    manager.run()
