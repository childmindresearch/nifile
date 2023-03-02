# `nifile`: Neuroimaging file identification and meta data extraction

Work in progress.

## Install

```sh
pip install git+https://github.com/nx10/nifile.git
```

## Usage

```sh
nifile anat/sub-1_ses-1_hemi-R_desc-surfaceMesh_pial.pial
```
```json
{
    "standard": "freesurfer",
    "modality": "surface_mesh",
    "object": "hemi_right",
    "meta": null
}
```

Deep scan:

```sh
nifile -d anat/sub-1_ses-1_hemi-R_desc-surfaceMesh_pial.pial
```
```json
{
    "standard": "freesurfer",
    "modality": "surface_mesh",
    "object": "hemi_right",
    "meta": {
        "num_vert": 149526,
        "vert_dtype": "float64",
        // ...
        "comment": "created by flo on Wed Dec  7 00:33:23 2022"
    }
}
```
