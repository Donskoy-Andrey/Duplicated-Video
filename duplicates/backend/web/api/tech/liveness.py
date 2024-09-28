from .router import router
from fastapi.responses import ORJSONResponse


@router.get('/liveness')
def liveness():
    return ORJSONResponse({'status': 'ok'})
