from typing import Callable

from hyo2.qax.lib.plugin import QaxCheckToolPlugin, QaxCheckReference, \
    QaxFileType
from ausseabed.qajson.model import QajsonRoot, QajsonDataLevel, QajsonCheck, \
    QajsonFile, QajsonInputs

from ausseabed.mbespc.lib.density_check import AlgorithmIndependentDensityCheck


class PointCloudChecksQaxPlugin(QaxCheckToolPlugin):

    # supported file types
    file_types = [
        QaxFileType(
            name="LAS",
            extension="las",
            group="Point Cloud"
        ),
        QaxFileType(
            name="GeoTIFF",
            extension="tif",
            group="Survey DTMs",
            icon="tif.png"
        ),
    ]

    def __init__(self):
        super(PointCloudChecksQaxPlugin, self).__init__()
        # name of the check tool
        self.name = 'Point Cloud Checks'
        self._check_references = self._build_check_references()

    def _build_check_references(self) -> list[QaxCheckReference]:
        data_level = "survey_products"
        check_refs = []

        cr = QaxCheckReference(
            id=AlgorithmIndependentDensityCheck.id,
            name=AlgorithmIndependentDensityCheck.name,
            data_level=data_level,
            description=None,
            supported_file_types=PointCloudChecksQaxPlugin.file_types,
            default_input_params=AlgorithmIndependentDensityCheck.input_params,
            version=AlgorithmIndependentDensityCheck.version,
        )
        check_refs.append(cr)
        return check_refs

    def checks(self) -> list[QaxCheckReference]:
        return self._check_references

    def run(
        self,
        qajson: QajsonRoot,
        progress_callback: Callable = None,
        qajson_update_callback: Callable = None,
        is_stopped: Callable = None
    ) -> None:
        # TODO plugin boilerplate
        pass