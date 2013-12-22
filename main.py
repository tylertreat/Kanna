"""Initialize Flask app."""

import furious_router
furious_router.setup_lib_path()

from kanna import create_app


app = create_app()

