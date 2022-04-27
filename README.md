# Ansible Collection - nvidia.dpu_ops

The following is a collection of roles that can be used to administer NVIDIA DPU cards. 
It contains the following functions:

* `bf_bmc` - Run arbitrary ipmitool commands on the BMC of a DPU
* `bf2_boot` - Modify the boot order of a DPU
* `bf2_mode` - Modify the security and ownership modes of a DPU
* `force_reboot_armos` - Force reboot the DPU over rshim
* `install_doca` - Install DOCA utilities
* `load_bfb` - Load BFB and bf.cfg over rshim
* `manage_bf_bmc_fw` - Upgrade the firmware of the BMC of the DPU
* `manage_bf2_fw` - Upgrade the firmware of the DPU
* `manage_bf2_nic_speed` - Change settings on the nic speed for a DPU
* `manage_rshim_owner` - Change rshim ownership between a DPU and its host
* `prepare_cuda_repo` - Prepare local repository of CUDA installer
* `install_cuda` - Install CUDA on x86 or DPU
* `dpu_nvconfig` - Set nvconfig parameters of DPU
