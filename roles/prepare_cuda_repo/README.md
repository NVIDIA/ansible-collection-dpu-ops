# Prepare CUDA local repository

The `prepare_cuda_repo` role is used to download CUDA "DEB local" installer,
unpack it on the "control plane" host line Foreman and set up corresponding data.

This roles is used in conjunction with `install_cuda` role

## Parameters

* `cuda_release` -- release of CUDA like `11.5.1`, `11.6.2`
* `cuda_arch` -- CPU architecture to install. Allowed values are:
  * `amd64`
  * `arm64`

