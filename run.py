import uvicorn

if __name__ == "__main__":
    uvicorn.run('app:main_app', host='127.0.0.1', port=8500, reload=True)
    # uvicorn.run('app:main_app', host='0.0.0.0',port=8500, reload=False)