from pythonforandroid.recipe import MesonRecipe


class ContourpyRecipe(MesonRecipe):
    version = "1.3.3"
    url = "https://github.com/contourpy/contourpy/archive/refs/tags/v{version}.tar.gz"

    depends = ["numpy"]

    pybind_version = "2.13.4"

    hostpython_prerequisites = [
        "meson-python>=0.13.1,<0.17.0",
        "pybind11>=2.13.2,!=2.13.3",
    ]


recipe = ContourpyRecipe()
