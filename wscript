# -*- python -*-

import waflib.Logs as msg

def pkg_deps(ctx):
    return

def options(ctx):
    ctx.load("hep-waftools-base")
    ctx.load("find_root")
    return

def configure(ctx):
    ctx.load("hep-waftools-base")
    ctx.load("find_root")
    ctx.find_root()
    return

def build(ctx):
    msg.info("ROOT-home: %s" % ctx.env.ROOT_HOME)
    return

def install(ctx):
    return
