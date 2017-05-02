#!/usr/bin/env python

"""Ninja build configurator for lua library"""

import sys
import os

sys.path.insert(0, os.path.join('build', 'ninja'))

import generator

dependlibs = ['resource', 'network', 'foundation']
extralibs = []
extravariables = {'support_lua' : True}

generator = generator.Generator(project = 'lua', dependlibs = dependlibs, variables = [('bundleidentifier', 'com.rampantpixels.lua.$(binname)')])
target = generator.target
writer = generator.writer
toolchain = generator.toolchain

if target.is_windows():
  extralibs += ['ws2_32', 'iphlpapi']

lua_lib = generator.lib(module = 'lua', sources = [
  'bind.c', 'compile.c', 'event.c', 'foundation.c', 'import.c', 'lua.c', 'module.c', 'network.c',
  'read.c', 'resource.c', 'symbol.c', 'version.c'])

if not target.is_ios() and not target.is_android():
  configs = [config for config in toolchain.configs if config not in ['profile', 'deploy']]
  if not configs == []:
    generator.bin('lua', ['main.c'], 'lua', basepath = 'tools', implicit_deps = [lua_lib], libs = ['lua', 'luajit'] + dependlibs + extralibs, configs = configs, variables = extravariables)
    generator.bin('luadump', ['main.c'], 'luadump', basepath = 'tools', implicit_deps = [lua_lib], libs = ['lua', 'luajit'] + dependlibs + extralibs, configs = configs, variables = extravariables)
    generator.bin('luaimport', ['main.c'], 'luaimport', basepath = 'tools', implicit_deps = [lua_lib], libs = ['lua', 'luajit'] + dependlibs + extralibs, configs = configs, variables = extravariables)
    generator.bin('luacompile', ['main.c'], 'luacompile', basepath = 'tools', implicit_deps = [lua_lib], libs = ['lua', 'luajit'] + dependlibs + extralibs, configs = configs, variables = extravariables)
    generator.bin('', ['luacompile/main.c'], 'luacompile32', basepath = 'tools', implicit_deps = [lua_lib], libs = ['lua', 'luajit32'] + dependlibs + extralibs, configs = configs, variables = extravariables)

includepaths = generator.test_includepaths()

test_cases = [
  'bind', 'foundation'
]
if target.is_ios() or target.is_android():
  #Build one fat binary with all test cases
  test_resources = []
  test_extrasources = []
  test_cases += ['all']
  if target.is_ios():
    test_resources = [os.path.join('all', 'ios', item) for item in ['test-all.plist', 'Images.xcassets', 'test-all.xib']]
  elif target.is_android():
    test_resources = [os.path.join('all', 'android', item) for item in [
      'AndroidManifest.xml', os.path.join('layout', 'main.xml'), os.path.join('values', 'strings.xml'),
      os.path.join('drawable-ldpi', 'icon.png'), os.path.join('drawable-mdpi', 'icon.png'), os.path.join('drawable-hdpi', 'icon.png'),
      os.path.join('drawable-xhdpi', 'icon.png'), os.path.join('drawable-xxhdpi', 'icon.png'), os.path.join('drawable-xxxhdpi', 'icon.png')
    ]]
    test_extrasources = [os.path.join('all', 'android', 'java', 'com', 'rampantpixels', 'foundation', 'test', item) for item in [
      'TestActivity.java'
    ]]
  if target.is_pnacl():
    generator.bin(module = '', sources = [os.path.join(module, 'main.c') for module in test_cases] + test_extrasources, binname = 'test-all', basepath = 'test', implicit_deps = [lua_lib], libs = ['test', 'lua', 'luajit'] + dependlibs + extralibs, resources = test_resources, includepaths = includepaths)
  else:
    generator.app(module = '', sources = [os.path.join(module, 'main.c') for module in test_cases] + test_extrasources, binname = 'test-all', basepath = 'test', implicit_deps = [lua_lib], libs = ['test', 'lua', 'luajit'] + dependlibs + extralibs, resources = test_resources, includepaths = includepaths, variables = extravariables)
else:
  #Build one binary per test case
  generator.bin(module = 'all', sources = ['main.c'], binname = 'test-all', basepath = 'test', implicit_deps = [lua_lib], libs = ['lua'] + dependlibs + extralibs, includepaths = includepaths)
  for test in test_cases:
    generator.bin(module = test, sources = ['main.c'], binname = 'test-' + test, basepath = 'test', implicit_deps = [lua_lib], libs = ['test', 'lua', 'luajit'] + dependlibs + extralibs, includepaths = includepaths, variables = extravariables)
