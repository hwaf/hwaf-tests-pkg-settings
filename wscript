# -*- python -*-

import waflib.Logs as msg

PACKAGE = {
    'name': 'pkg-settings',
    'author': 'mana collaboration',
}

def pkg_deps(ctx):
    return

def options(ctx):
    ctx.load("hwaf-base")
    ctx.load("find_python")
    ctx.load("find_root")
    return

def configure(ctx):
    ctx.load("hwaf-base")
    ctx.load("find_python")
    ctx.load("find_root")
    ctx.find_python()
    ctx.find_root()

    # register this module for export
    ctx.hwaf_export_module("wscript")

    # declare a runtime env. var.
    ctx.env.JOBOPTPATH = []
    ctx.hwaf_declare_runtime_env("JOBOPTPATH")
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
@feature('hwaf_runtime_tsk', '*')
@before_method('process_rule')
def insert_project_level_pythonpath(self):
    '''
    insert_project_level_pythonpath adds ${INSTALL_AREA}/python into the
    ${PYTHONPATH} environment variable.
    '''
    _get = getattr(self, 'hwaf_get_install_path', None)
    if not _get: _get = getattr(self.bld, 'hwaf_get_install_path')
    pydir = _get('${INSTALL_AREA}/python')
    #msg.info("inserting [%s]..." % pydir)
    self.env.prepend_value('PYTHONPATH', pydir)
    #msg.info("==> %s" % self.env.PYTHONPATH)
    return

@feature('hwaf_runtime_tsk', '*')
@before_method('process_rule')
def insert_project_level_joboptpath(self):
    '''
    insert_project_level_pythonpath adds ${INSTALL_AREA}/share into the
    ${JOBOPTPATH} environment variable.
    '''
    _get = getattr(self, 'hwaf_get_install_path', None)
    if not _get: _get = getattr(self.bld, 'hwaf_get_install_path')
    pydir = _get('${INSTALL_AREA}/share')
    self.env.prepend_value('JOBOPTPATH', pydir)
    return

### -----------------------------------------------------------------------------
def install_headers(self, incdir=None, relative_trick=True, cwd=None):
    
    # extract package name
    PACKAGE_NAME = self._get_pkg_name()
    inc_node = None
    if not incdir:
        inc_node = self.path.find_dir(PACKAGE_NAME)
        if not inc_node:
            return
    else:
        if isinstance(incdir, str):
            inc_node = self.path.find_dir(incdir)
        else:
            inc_node = incdir
            pass
        pass
    
    if isinstance(cwd, str):
        cwd = self.path.find_dir(cwd)
        
    if not inc_node:
        self.fatal('no such directory [%s] (pkg=%s)' % (incdir, PACKAGE_NAME))
        pass
    
    includes = inc_node.ant_glob('**/*', dir=False)
    self.install_files(
        '${INSTALL_AREA}/include', includes, 
        relative_trick=relative_trick,
        cwd=cwd,
        postpone=False,
        )

    incpath = waflib.Utils.subst_vars('${INSTALL_AREA}/include',self.env)
    #msg.info("--> [%s] %s" %(PACKAGE_NAME,incpath))
    self.env.append_unique('INCLUDES_%s' % PACKAGE_NAME,
                           [incpath,inc_node.parent.abspath()])
    #inc_node.parent.abspath())
    return
    
### ---------------------------------------------------------------------------
def build_app(self, name, source, **kw):
    kw = dict(kw)

    # FIXME: hack !!! cppunit doesn't propagate correctly...
    do_test = kw.get('do_test', False)
    if do_test:
        return

    kw['features'] = waflib.Utils.to_list(
        kw.get('features', '')) + [
        'cxx', 'cxxprogram', 'symlink_tsk',
        ]
    
    kw['use'] = waflib.Utils.to_list(kw.get('use', []))

    pkg_node = self.path.get_src()
    src_node = self.path.find_dir('src')

    srcs = self._cmt_get_srcs_lst(source)
    linkflags = waflib.Utils.to_list(kw.get('linkflags', []))
    linkflags = self.env.SHLINKFLAGS + linkflags
    kw['linkflags'] = linkflags

    defines = waflib.Utils.to_list(kw.get('defines', []))
    kw['defines'] = defines + self._get_pkg_version_defines()
    
    includes = waflib.Utils.to_list(kw.get('includes', []))
    includes.insert(0, self.path.abspath())
    #includes.insert(1, self.path.abspath()+'/'+PACKAGE_NAME)
    kw['includes'] = includes + [src_node]

    kw['target'] = kw.get('target', name+".exe")
    
    # extract package name
    PACKAGE_NAME = self._get_pkg_name()

    exe = self(
        name=name,
        source=srcs,
        install_path='${INSTALL_AREA}/bin',
        libpath = self.env.LD_LIBRARY_PATH + [self.path.get_bld().abspath()],
        #libpath = self.env.LD_LIBRARY_PATH,
        **kw)
        
    return exe

### ---------------------------------------------------------------------------
def build_linklib(self, name, source, **kw):

    #msg.info('=========== %s ============' % name)
    # extract package name
    PACKAGE_NAME = self._get_pkg_name()

    kw = dict(kw)
    linkflags = kw.get('linkflags', [])
    linkflags = self.env.SHLINKFLAGS + linkflags
    kw['linkflags'] = linkflags
    
    src_node = self.path.find_dir('src')

    srcs = self._cmt_get_srcs_lst(source)
    includes = waflib.Utils.to_list(kw.get('includes', []))
    includes.insert(0, self.path.abspath())
    #includes.insert(1, self.path.abspath()+'/'+PACKAGE_NAME)
    kw['includes'] = includes + [src_node]

    export_incs = None
    kw['export_includes'] = waflib.Utils.to_list(
        kw.get('export_includes', [])
        )[:]
    if not kw['export_includes']:
        inc_node = self.path.find_dir(PACKAGE_NAME)
        if inc_node:
            export_incs = '.'
            kw['export_includes'].append(export_incs)
        inc_node = self.path.find_dir('inc/%s' % PACKAGE_NAME)
        if inc_node:
            export_incs = 'inc'
            kw['export_includes'].append(export_incs)
            #self.fatal('%s: export_includes - inc' % name)
        else:
            #self.fatal('%s: could not find [inc/%s] !!' % (name,PACKAGE_NAME))
            pass
    else:
        export_incs = kw['export_includes']
        #msg.info('%s: exports: %r' % (name, kw['export_includes']))
        pass

    kw['includes'].extend(kw['export_includes'])
    
    kw['use'] = waflib.Utils.to_list(kw.get('use', [])) + ['dl']
    kw['target'] = kw.get('target', name)
    
    defines = kw.get('defines', [])
    _defines = []
    for d in self.env.CPPFLAGS:
        if d.startswith('-D'):
            _defines.append(d[len('-D'):])
        else:
            _defines.append(d)
    defines = _defines + defines
    kw['defines'] = defines + self._get_pkg_version_defines()

    kw['features'] = waflib.Utils.to_list(kw.get('features', [])) + [
        'cxx', 'cxxshlib', 'symlink_tsk',
        ]
    #msg.info ("==> build_linklib(%s, '%s', %r)..." % (name, source, kw))
    o = self(
        name            = name,
        source          = srcs,
        install_path    = '${INSTALL_AREA}/lib',
        #export_includes = ['.', './'+PACKAGE_NAME],
        #export_includes = export_,
        libpath = self.env.LD_LIBRARY_PATH + [self.path.get_bld().abspath()],
        #libpath         = self.env.LD_LIBRARY_PATH,
        **kw
        )
    # for use-exports
    # FIXME: also propagate uses ?
    self.env['LIB_%s' % name] = [name]
    self.env.append_unique('LIBPATH_%s'%name, self.path.get_bld().abspath())
    #msg.info('--> libpath[%s]: %s' % (name, self.env['LIBPATH_%s'%name]))
    #msg.info('--> incpath[%s]: %s' % (name, export_incs))

    if export_incs:
        export_incs = waflib.Utils.to_list(export_incs)[0]
        if export_incs == '.':
            self.install_headers()
        elif export_incs == 'inc':
            incdir = self.path.find_dir('inc')
            hdrdir = 'inc/%s' % PACKAGE_NAME
            self.install_headers(hdrdir, cwd=incdir)
        else:
            pass

    #o.post()
    return o

### ---------------------------------------------------------------------------
import waflib.Build
waflib.Build.BuildContext.build_app = build_app
waflib.Build.BuildContext.build_linklib = build_linklib
waflib.Build.BuildContext.install_headers = install_headers
### ---------------------------------------------------------------------------
