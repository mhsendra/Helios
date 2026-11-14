from os.path import join
from pythonforandroid.recipe import MesonRecipe


class PandasRecipe(MesonRecipe):
    version = 'v2.3.0'
    url = 'git+https://github.com/pandas-dev/pandas'
    depends = ['numpy', 'libbz2', 'liblzma']
    hostpython_prerequisites = ["versioneer[toml]", "Cython<4.0.0a0"]
    patches = ['fix_numpy_includes.patch']
    python_depends = ['python-dateutil', 'pytz']
    need_stl_shared = True

    def get_recipe_env(self, arch, **kwargs):
        env = super().get_recipe_env(arch, **kwargs)
        # we need the includes from our installed numpy at site packages
        # because we need some includes generated at numpy's compile time

        env['NUMPY_INCLUDES'] = join(
            self.ctx.get_python_install_dir(arch.arch), "numpy/_core/include",
        )
        env["PYTHON_INCLUDE_DIR"] = self.ctx.python_recipe.include_root(arch)

        # this flag below is to fix a runtime error:
        #   ImportError: dlopen failed: cannot locate symbol
        #   "_ZTVSt12length_error" referenced by
        #   "/data/data/org.test.matplotlib_testapp/files/app/_python_bundle
        #   /site-packages/pandas/_libs/window/aggregations.so"...
        env['LDFLAGS'] += f' -landroid  -l{self.stl_lib_name}'
        return env

    def build_arch(self, arch):
        # Constrain NumPy only inside pandas' isolated PEP 517 build.
        # Android headers remain supplied by the NumPy Android recipe.
        build_dir = self.get_build_dir(arch.arch)
        constraints_file = build_dir + "/p4a-build-constraints.txt"

        with open(constraints_file, "w") as file:
            file.write("numpy==2.3.5\n")

        original_extra_build_args = self.extra_build_args
        self.extra_build_args = list(original_extra_build_args)
        self.extra_build_args.extend([
            "--dependency-constraints-txt",
            constraints_file,
        ])

        try:
            super().build_arch(arch)
        finally:
            self.extra_build_args = original_extra_build_args

        self.restore_hostpython_prerequisites(["cython"])


recipe = PandasRecipe()
