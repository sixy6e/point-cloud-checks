from datetime import datetime
import traceback
from typing import Callable, Any
from pathlib import Path

from hyo2.qax.lib.plugin import QaxCheckToolPlugin, QaxCheckReference, \
    QaxFileType
from ausseabed.qajson.model import QajsonRoot, QajsonDataLevel, QajsonCheck, \
    QajsonFile, QajsonInputs, QajsonExecution, QajsonOutputs

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

    def _get_param_value(self, param_name: str, check: QajsonCheck) -> Any:
        ''' Gets a parameter value from the QajsonCheck based on the parameter
        name. Will return None if the parameter is not found.
        '''
        param = next(
            (
                p
                for p in check.inputs.params
                if p.name == param_name
            ),
            None
        )
        if param is None:
            return None
        else:
            return param.value


    def _run_algorithm_indepenent_density_check(self, check: QajsonCheck):
        # get the parameter values the check needs to run
        min_soundings = int(self._get_param_value(
            'Minimum Soundings per node',
            check
        ))
        min_soundings_percentage = float(self._get_param_value(
            'Minimum Soundings per node percentage',
            check
        ))

        # get the input files the check needs to run. In this case we get
        # the first point cloud and first grid file and assume those are the
        # ones that will be tested
        point_file = None
        grid_file = None
        for f in check.inputs.files:
            if point_file is None and f.file_type == 'Point Cloud':
                point_file = Path(f.path)
            if grid_file is None and f.file_type == 'Survey DTMs':
                grid_file = Path(f.path)

        output_details = QajsonOutputs()
        check.outputs = output_details

        start_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
        execution_details = QajsonExecution(
            start=start_time,
            end=None,
            status='running',
            error=None
        )
        check.outputs.execution = execution_details

        try:
            # now run the check
            density_check = AlgorithmIndependentDensityCheck(
                grid_file=grid_file,
                point_cloud_file=point_file,
                minimum_count=min_soundings,
                minimum_count_percentage=min_soundings_percentage
            )
            density_check.run()

            execution_details.status = 'completed'
        except Exception as ex:
            execution_details.status = 'failed'
            execution_details.error = traceback.format_exc()
        finally:
            execution_details.end = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")

        if execution_details.status == 'failed':
            # no need to populate results as there are none
            return

        # now add the result data to the qajson output details so that it's
        # captured and presented to the user
        if density_check.passed:
            output_details.check_state = 'pass'
        else:
            output_details.check_state = 'fail'

        pass_percentage = (density_check.total_nodes - density_check.failed_nodes) / density_check.total_nodes * 100.0

        messages: list[str] = []
        messages.append(
                f'{pass_percentage:.1f}% of nodes were found to have a '
                f'sounding count above {min_soundings}. This is required to'
                f' be {min_soundings_percentage}% of all nodes'
            )

        output_details.messages = messages

        # use the data dict to stash some misc information generated by the check
        data = {}
        # need to convert the density values from ints to strings to support
        # json serialisation
        str_key_counts = [(str(d),c) for d,c in density_check.histogram]
        data['chart'] = {
            'type': 'histogram',
            'data': str_key_counts
        }

        data['summary'] = {
            'total_soundings': int(density_check.total_nodes),
            'percentage_over_threshold': int(density_check.passed),
            'under_threshold_soundings': int(density_check.failed_nodes)
        }
        output_details.data = data

    def run(
        self,
        qajson: QajsonRoot,
        progress_callback: Callable = None,
        qajson_update_callback: Callable = None,
        is_stopped: Callable = None
    ) -> None:
        ''' Run all checks implemented by this plugin
        '''
        # get all survey product checks, the check references we create in
        # _build_check_references all specify "survey_products" so we'll only
        # find the input details for this plugin here
        sp_qajson_checks = qajson.qa.survey_products.checks

        for qajson_check in sp_qajson_checks:
            # loop through all the checks, this will include checks implemented in
            # other plugins (we need to skip these)
            if qajson_check.info.id == AlgorithmIndependentDensityCheck.id:
                # then run the density check
                self._run_algorithm_indepenent_density_check(qajson_check)
            # other checks would be added here

        if qajson_update_callback is not None:
            qajson_update_callback()
