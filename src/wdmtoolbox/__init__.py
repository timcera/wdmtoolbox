"""Package __init__.py."""

import os

if os.name == "nt":
    import sysconfig

    os.add_dll_directory(sysconfig.get_paths()["purelib"])

__all__ = [
    "cleancopywdm",
    "copydsn",
    "copydsnlabel",
    "createnewdsn",
    "createnewwdm",
    "csvtowdm",
    "deletedsn",
    "describedsn",
    "extract",
    "hydhrseqtowdm",
    "listdsns",
    "renumberdsn",
    "setattrib",
    "stdtowdm",
    "wdmtoswmm5rdii",
]
from .wdmtoolbox import (
    cleancopywdm,
    copydsn,
    copydsnlabel,
    createnewdsn,
    createnewwdm,
    csvtowdm,
    deletedsn,
    describedsn,
    extract,
    hydhrseqtowdm,
    listdsns,
    renumberdsn,
    setattrib,
    stdtowdm,
    wdmtoswmm5rdii,
)
