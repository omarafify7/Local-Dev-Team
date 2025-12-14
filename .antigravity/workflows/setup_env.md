## Build Local Team

Standard procedure for initializing a deep learning environment on NVIDIA RTX 5070 Ti (Blackwell) hardware. mandates Python 3.11+ and PyTorch 2.9.1+ with CUDA 12.8 to prevent kernel errors.

# Workflow: RTX 5070 Ti Environment Setup

**Trigger:**
This workflow applies when the user requests assistance setting up a Python environment, installing PyTorch, or configuring drivers for the NVIDIA GeForce RTX 50-series (specifically 5070 Ti) or the Blackwell architecture.

**Context:**
The RTX 5070 Ti utilizes the Blackwell architecture (Compute Capability `sm_120`). Standard PyTorch builds (CUDA 11.8/12.1) are incompatible and will result in "no kernel image" errors. The agent must enforce the use of **CUDA 12.8** or newer.

**Execution Steps:**

1.  **Environment Initialization:**
    Instruct the user to create a pristine Miniconda environment to prevent system conflicts. Python 3.11 is the preferred version for compatibility.
    * Command: `conda create --name name_that_is_relavent_to_the_workspace python=3.11 -y`
    * Command: `conda activate torch_5070`

2.  **PyTorch Installation (Critical Step):**
    Do NOT use the standard `pip install torch`. The agent must provide the specific command pointing to the CUDA 12.8 wheel index.
    * Command: `pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu128`

3.  **Validation:**
    Provide a python one-liner to verify that the GPU is detected and the CUDA capability matches the Blackwell architecture (Major version 12).
    * Command: `python -c "import torch; print(f'CUDA: {torch.cuda.is_available()} | Device: {torch.cuda.get_device_name(0)} | Cap: {torch.cuda.get_device_capability(0)}'"`

Expected Output:
'CUDA Available: True
Device Name: NVIDIA GeForce RTX 5070 Ti
CUDA Capability: (12, 0) (or similar, denoting the Blackwell architecture)'

**Error Handling:**
* If the user reports `AssertionError: Torch not compiled with CUDA enabled`, instruct them to check that they did not accidentally use the default `pip` repository.
* If the user reports driver issues, verify they are on NVIDIA Driver version **570.xx** or higher.