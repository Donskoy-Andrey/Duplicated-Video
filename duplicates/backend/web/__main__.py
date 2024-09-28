if __name__ == '__main__':
    import uvicorn

    from web.config.settings import settings

    uvicorn.run(
        'web.app:create_app',
        host=settings.BIND_IP,
        port=settings.BIND_PORT,
        reload=True,
    )
