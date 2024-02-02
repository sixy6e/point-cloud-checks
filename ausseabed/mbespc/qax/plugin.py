from datetime import datetime
import logging
import traceback
from typing import Callable, Any
from pathlib import Path
import rasterio
from shapely import geometry
import geopandas
import geojson

from hyo2.qax.lib.plugin import QaxCheckToolPlugin, QaxCheckReference, \
    QaxFileType
from ausseabed.qajson.model import QajsonRoot, QajsonDataLevel, QajsonCheck, \
    QajsonFile, QajsonInputs, QajsonExecution, QajsonOutputs

from ausseabed.mbespc.lib.density_check import AlgorithmIndependentDensityCheck

LOG = logging.getLogger(__name__)


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

        if point_file is None:
            msg = "Missing input point data"
            LOG.info(msg)
            execution_details.status = "aborted"
            execution_details.error = msg

        if grid_file is None:
            msg = "Missing input depth data"
            LOG.info(msg)
            execution_details.status = "aborted"
            execution_details.error = msg

        if execution_details.status == "aborted":
            msg = "Aborting Algorithm Independent Density Check"
            LOG.info(msg)
            return

        if self.spatial_outputs_export:
            outdir = Path(self.spatial_outputs_export_location)
        else:
            outdir = None

        density_check = AlgorithmIndependentDensityCheck(
            grid_file=grid_file,
            point_cloud_file=point_file,
            minimum_count=min_soundings,
            minimum_count_percentage=min_soundings_percentage,
            outdir=outdir,
        )

        try:
            # now run the check
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

        # pass_percentage = (density_check.total_nodes - density_check.failed_nodes) / density_check.total_nodes

        messages: list[str] = []
        messages.append(
                f'{density_check.percentage_passed:.1f}% of nodes were found to have a '
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
            'total_soundings': density_check.total_nodes,
            'check_passed': density_check.passed,
            'percentage_over_threshold': density_check.percentage_passed,
            'under_threshold_soundings': density_check.percentage_failed,
            'failed_nodes': density_check.failed_nodes,
        }

        LOG.info(density_check.total_nodes)
        LOG.info(density_check.passed)
        LOG.info(density_check.percentage_passed)
        LOG.info(density_check.percentage_failed)
        LOG.info(density_check.failed_nodes)

        if self.spatial_outputs_qajson:
            # the qax viewer isn't designed to be an all bells viewing solution
            # nor replace tools like QGIS, TuiView ...
            # the vector geoms need to be simplified, and all geoms transformed
            # to epsg:4326
            # other plugins use a buffer of 5 pixel widths and then simplify

            with rasterio.open(grid_file) as ds:
                # bounds derived from input raster
                gdf_box = geopandas.GeoDataFrame(
                    {"geometry": [geometry.box(*ds.bounds)]},
                    crs=ds.crs,
                ).to_crs(epsg=4326)

                # buffering; assuming square-ish pixels ...
                distance = 5*ds.res[0]  # used for buffering and simplifying
                buffered = density_check.gdf.buffer(distance)

                # false means use the "Douglas-Peucker algorithm"
                simplified_geom = buffered.simplify(
                    distance, preserve_topology=False
                )
                warped_geom = simplified_geom.to_crs(epsg=4326)

                # qax map viewer requires MultiPolygon geoms
                mp_box_geoms = geometry.MultiPolygon(gdf_box.geometry.values)
                mp_pix_geoms = geometry.MultiPolygon(
                    warped_geom.geometry.values,
                )
                # mp_box = geopandas.GeoDataFrame(
                #     {"geometry": [mp_box_geoms]},
                #     crs=gdf_box.crs,
                # )
                # mp_gdf = geopandas.GeoDataFrame(
                #     {"geometry": [mp_pix_geoms]},
                #     crs=warped_geom.crs,
                # )

                # data['map'] = geojson.loads(mp_gdf.to_json())
                # data['extents'] = geojson.loads(mp_box.to_json())
                data['map'] = geojson.dumps(mp_pix_geoms)
                data['extents'] = geojson.dumps(mp_box_geoms)

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
