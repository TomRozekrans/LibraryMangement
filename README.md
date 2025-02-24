# LibraryManagement

This  application is a simple REST-api to manage a library of books. 



## Installation
```
poetry install
poetry run python -m uvicorn librarymanagement.main:app
```

The application will be available at http://127.0.0.1:8000


## Settings
The settings for this application can be set using environment variables or a .env file.
The following settings are available:

| Setting                | Description                                      |
|------------------------|--------------------------------------------------|
| DISABLED_GENRES_CREATE | List of genres for which books cannot be added   |
| DISABLED_GENRES_SEARCH | List of genres for which book cannot be searched |
| MASKED_GENRES          | List of genres for which the titles should be ma |

