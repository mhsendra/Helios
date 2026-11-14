import glob
import os
import shutil

from pythonforandroid.logger import info
from pythonforandroid.recipe import PyProjectRecipe
from pythonforandroid.util import BuildInterruptingException


class ReportLabRecipe(PyProjectRecipe):
    version = "5.1.0"

    # No se descarga ni compila código fuente.
    url = None

    # ReportLab necesita Pillow en tiempo de ejecución.
    depends = ["Pillow"]

    call_hostpython_via_targetpython = False

    def should_build(self, arch):
        # No aceptar versiones antiguas ya instaladas.
        return True

    def clean_stale_venv_metadata(self):
        """
        Elimina metadatos antiguos de ReportLab del entorno
        virtual temporal utilizado por python-for-android.
        """

        venv_lib = os.path.join(
            self.ctx.build_dir,
            "venv",
            "lib"
        )

        site_packages_dirs = glob.glob(
            os.path.join(
                venv_lib,
                "python*",
                "site-packages"
            )
        )

        for site_packages in site_packages_dirs:
            pattern = os.path.join(
                site_packages,
                "reportlab-*.dist-info"
            )

            for metadata_dir in glob.glob(pattern):
                if os.path.basename(metadata_dir) == (
                    "reportlab-5.1.0.dist-info"
                ):
                    continue

                info(
                    "ReportLab: eliminando metadatos obsoletos "
                    "del entorno virtual: {}".format(metadata_dir)
                )

                if os.path.isdir(metadata_dir):
                    shutil.rmtree(metadata_dir)
                elif os.path.exists(metadata_dir):
                    os.remove(metadata_dir)

    def build_arch(self, arch):
        info("ReportLab: buscando rueda binaria compatible 5.1.0")

        if not self.check_prebuilt(arch):
            raise BuildInterruptingException(
                "ReportLab 5.1.0: no se ha encontrado una rueda "
                "compatible con Python y Android."
            )

        info("ReportLab: rueda compatible encontrada")

        if not self.install_prebuilt_wheel(arch):
            raise BuildInterruptingException(
                "ReportLab 5.1.0: ha fallado la instalación de la rueda."
            )

        destination = self.ctx.get_python_install_dir(arch.arch)

        package_dir = os.path.join(destination, "reportlab")
        metadata_dir = os.path.join(
            destination,
            "reportlab-5.1.0.dist-info"
        )
        metadata_file = os.path.join(metadata_dir, "METADATA")

        if not os.path.isdir(package_dir):
            raise BuildInterruptingException(
                "ReportLab 5.1.0: no existe el directorio del paquete."
            )

        if not os.path.isfile(metadata_file):
            raise BuildInterruptingException(
                "ReportLab 5.1.0: no se han encontrado sus metadatos."
            )

        with open(metadata_file, "r", encoding="utf-8") as file:
            metadata = file.read()

        if "Version: 5.1.0" not in metadata:
            raise BuildInterruptingException(
                "ReportLab: la versión instalada no coincide con 5.1.0."
            )

        # Limpiar metadatos antiguos del destino Android.
        pattern = os.path.join(destination, "reportlab-*.dist-info")

        for old_metadata in glob.glob(pattern):
            if os.path.abspath(old_metadata) == os.path.abspath(
                metadata_dir
            ):
                continue

            info(
                "ReportLab: eliminando metadatos antiguos: {}".format(
                    os.path.basename(old_metadata)
                )
            )

            if os.path.isdir(old_metadata):
                shutil.rmtree(old_metadata)
            elif os.path.exists(old_metadata):
                os.remove(old_metadata)

        # Limpiar también el entorno virtual temporal.
        # Evita que pip freeze genere restricciones con rutas
        # directas a versiones antiguas de ReportLab.
        self.clean_stale_venv_metadata()

        info("ReportLab 5.1.0 instalado y verificado correctamente.")


recipe = ReportLabRecipe()
