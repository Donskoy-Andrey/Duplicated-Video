from .router import router
from fastapi.responses import ORJSONResponse


@router.get('/readiness')
def readiness():
    # TODO надо сделать в бд select 1
    return ORJSONResponse({'status': 'ok'})
