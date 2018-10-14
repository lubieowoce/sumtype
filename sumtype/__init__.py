# Main user-facing api
from .sumtype import sumtype
__all__ = ['sumtype']

# Expose the actual functions `sumtype` calls
from .sumtype_slots import sumtype         as make_sumtype
from .sumtype_slots import untyped_sumtype as make_untyped_sumtype

# Expose submodules
# from . import sumtype	 		  as sumtype
from . import future
from . import sumtype_meta 		  as meta
from . import sumtype_slots       as slots
from . import experimental

