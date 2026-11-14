from multiprocessing import cpu_count
from os.path import join

import sh

from pythonforandroid.logger import shprint
from pythonforandroid.recipe import Recipe
from pythonforandroid.util import current_directory


class HarfbuzzRecipe(Recipe):
    """
    HarfBuzz 2.6.4 con adaptación localizada para Clang del NDK moderno.

    Se mantiene el ciclo original de compilación con FreeType de p4a.
    """

    version = "2.6.4"
    url = (
        "http://www.freedesktop.org/software/harfbuzz/release/"
        "harfbuzz-{version}.tar.xz"
    )

    opt_depends = ["freetype"]

    patches = ["relax-cast-function-type.patch", "remove-unused-supp-size.patch"]

    built_libraries = {
        "libharfbuzz.so": "src/.libs",
    }

    def get_recipe_env(self, arch=None):
        env = super().get_recipe_env(arch)

        if "freetype" in self.ctx.recipe_build_order:
            freetype = self.get_recipe("freetype", self.ctx)
            freetype_install = join(
                freetype.get_build_dir(arch.arch),
                "install",
            )

            env["FREETYPE_CFLAGS"] = (
                "-I{}/include/freetype2".format(freetype_install)
            )

            env["FREETYPE_LIBS"] = " ".join([
                "-L{}/lib".format(freetype_install),
                "-lfreetype",
            ])

        return env

    def build_arch(self, arch):
        env = self.get_recipe_env(arch)

        with current_directory(self.get_build_dir(arch.arch)):
            configure = sh.Command("./configure")

            shprint(
                configure,
                "--host={}".format(arch.command_prefix),
                "--prefix={}".format(self.get_build_dir(arch.arch)),
                "--with-freetype={}".format(
                    "yes"
                    if "freetype" in self.ctx.recipe_build_order
                    else "no"
                ),
                "--with-icu=no",
                "--with-cairo=no",
                "--with-fontconfig=no",
                "--with-glib=no",
                _env=env,
            )

            shprint(
                sh.make,
                "-j",
                str(cpu_count()),
                _env=env,
            )

        if "freetype" in self.ctx.recipe_build_order:
            freetype = self.get_recipe("freetype", self.ctx)
            freetype.build_arch(arch, with_harfbuzz=True)
            freetype.install_libraries(arch)


recipe = HarfbuzzRecipe()
