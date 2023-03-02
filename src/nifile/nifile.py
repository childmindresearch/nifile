import dataclasses
import json
import pathlib as pl
import re
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Iterable

try:
    import numpy as np
    import nibabel as nib
except:
    print(f'Warning: nibabel is not installed. Not all functions are available.')


RX_SURFACE_MESH_FREESURFER = (r'\.pial$', r'\.white$', r'\.inflated$', r'\.smoothwm$', r'\.sphere$')
RX_SURFACE_MAP_FREESURFER = (r'\.sulc$', r'\.volume$', r'\.thickness$')

RX_SURFACE_MESH_GIFTI = (r'\.surf.gii$', r'\.coord.gii$')
RX_SURFACE_MAP_GIFTI = (r'\.shape.gii$', r'\.func.gii$', r'\.label.gii$')

# RX_SURFACE_MESH_CIFTI = ()
RX_SURFACE_MAP_CIFTI = (r'\.dlabel.nii$', r'\.dtseries.nii$', r'\.dscalar.nii$')

RX_VOLUME_VOXEL_NIFTI = (r'\.nii$', r'\.nii.gz$')


def _matches_any_regex(s: str, regexes: Iterable[str]) -> Optional[re.Match[str]]:
    for rx in regexes:
        m = re.search(rx, s)
        if m:
            return m
    return None


class NiFileStandard(Enum):
    FREESURFER = 'freesurfer'
    CIFTI = 'cifti'
    GIFTI = 'gifti'
    NIFTI = 'nifti'


class NiFileModality(Enum):
    VOLUME_VOXEL = 'volume_voxel'
    SURFACE_MESH = 'surface_mesh'
    SURFACE_MAP = 'surface_map'


class NiFileObject(Enum):
    HEMI_RIGHT = 'hemi_right'
    '''Right brain hemisphere'''
    HEMI_LEFT = 'hemi_left'
    '''Left brain hemisphere'''


@dataclass
class FilenameData:
    standard: Optional[NiFileStandard]
    modality: Optional[NiFileModality]
    object: Optional[NiFileObject]
    meta: Optional[dict]


def _find_freesurfer_mod_object(filename) -> Optional[NiFileObject]:
    p = pl.Path(filename).stem

    # Explicitly mentioned (BIDS)

    if 'hemi-R' in p:
        return NiFileObject.HEMI_RIGHT
    if 'hemi-L' in p:
        return NiFileObject.HEMI_LEFT

    # Freesurfer standard

    if re.search(r'rh\.[^.]+$', p):
        return NiFileObject.HEMI_RIGHT
    if re.search(r'lh\.[^.]+$', p):
        return NiFileObject.HEMI_LEFT

    return None


def filename_data(filename) -> FilenameData:
    file = pl.Path(filename)
    file_name = file.name
    if _matches_any_regex(file_name, RX_SURFACE_MESH_FREESURFER):
        return FilenameData(
            standard=NiFileStandard.FREESURFER,
            modality=NiFileModality.SURFACE_MESH,
            object=_find_freesurfer_mod_object(filename),
            meta=None
        )
    if _matches_any_regex(file_name, RX_SURFACE_MAP_FREESURFER):
        return FilenameData(
            standard=NiFileStandard.FREESURFER,
            modality=NiFileModality.SURFACE_MAP,
            object=_find_freesurfer_mod_object(filename),
            meta=None
        )
    if _matches_any_regex(file_name, RX_SURFACE_MAP_GIFTI):
        return FilenameData(
            standard=NiFileStandard.GIFTI,
            modality=NiFileModality.SURFACE_MAP,
            object=None,
            meta=None
        )
    if _matches_any_regex(file_name, RX_SURFACE_MESH_GIFTI):
        return FilenameData(
            standard=NiFileStandard.GIFTI,
            modality=NiFileModality.SURFACE_MESH,
            object=None,
            meta=None
        )
    if _matches_any_regex(file_name, RX_SURFACE_MAP_CIFTI):
        return FilenameData(
            standard=NiFileStandard.CIFTI,
            modality=NiFileModality.SURFACE_MAP,
            object=None,
            meta=None
        )
    if _matches_any_regex(file_name, RX_VOLUME_VOXEL_NIFTI):
        return FilenameData(
            standard=NiFileStandard.NIFTI,
            modality=NiFileModality.VOLUME_VOXEL,
            object=None,
            meta=None
        )
    return FilenameData(
        standard=None,
        modality=None,
        object=None,
        meta=None
    )


def file_data(filename, filename_data: FilenameData):
    meta = {}
    if filename_data.standard == NiFileStandard.FREESURFER:
        if filename_data.modality == NiFileModality.SURFACE_MESH:
            geom_vert, geom_tri, file_meta, file_comment = nib.freesurfer.read_geometry(filename, read_metadata=True,
                                                                                        read_stamp=True)

            meta['num_vert'] = geom_vert.shape[0]
            meta['vert_dtype'] = str(geom_vert.dtype)
            meta['num_tri'] = geom_tri.shape[0]

            meta.update(file_meta)
            meta['comment'] = file_comment

        if filename_data.modality == NiFileModality.SURFACE_MAP:
            blob = nib.freesurfer.read_morph_data(filename).shape
            print(blob)

    filename_data.meta = meta
    return filename_data


class EnumAndDataclassEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        if dataclasses.is_dataclass(obj):
            return dataclasses.asdict(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def probe_file(path_input: str, path_output: Optional[str], deep: bool):
    dat = filename_data(path_input)

    if deep:
        file_data(path_input, dat)

    if path_output:
        with open(path_output, 'w', encoding='utf8') as f:
            json.dump(dat, f, indent=4, cls=EnumAndDataclassEncoder)
    else:
        print(json.dumps(dat, indent=4, cls=EnumAndDataclassEncoder))
