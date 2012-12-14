# -*- python -*-

import waflib.Logs as msg

def pkg_deps(ctx):
    return

def options(ctx):
    ctx.load("hep-waftools-base")
    ctx.load("find_python")
    ctx.load("find_root")
    return

def configure(ctx):
    ctx.load("hep-waftools-base")
    ctx.load("find_python")
    ctx.load("find_root")
    ctx.find_python()
    ctx.find_root()

    # register this module for export
    ctx.hwaf_export_module("wscript")
    return

def build(ctx):
    msg.info("ROOT-home: %s" % ctx.env.ROOT_HOME)
    return

def install(ctx):
    return



### define a few dummy tasks --------------------------------------------------
from waflib import TaskGen
TaskGen.declare_chain(
    name='task-a',
    rule='/bin/cp ${SRC} ${TGT}',
    ext_in='.in',
    ext_out='.a',
    )
TaskGen.declare_chain(
    name='task-b',
    rule='/bin/cp ${SRC} ${TGT}',
    ext_in='.a',
    ext_out='.b',
    )
TaskGen.declare_chain(
    name='task-c',
    rule='/bin/cp ${SRC} ${TGT}',
    ext_in='.b',
    ext_out='.cxx',
    reentrant = False,
    )

### ---------------------------------------------------------------------------
import waflib.Utils
from waflib.TaskGen import feature, before_method, after_method
@feature('hepwaf_runtime_tsk', '*')
@before_method('process_rule')
def insert_project_level_pythonpath(self):
    '''
    insert_project_level_pythonpath adds ${INSTALL_AREA}/python into the
    ${PYTHONPATH} environment variable.
    '''
    msg.info("^"*80)
    #pydir = waflib.Utils.subst_vars('${INSTALL_AREA}/python', self.env)
    pydir = self.hepwaf_get_install_path('${INSTALL_AREA}/python')
    msg.info("inserting [%s]..." % pydir)
    self.env.prepend_value('PYTHONPATH', pydir)
    msg.info("==> %s" % self.env.PYTHONPATH)
    return
