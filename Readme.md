Site that displays status history of FFXIV worlds.

### Docker deployment

#### Before deployment

- create `fws_site/settings/prod_secrets.py` file and define add your own secret key there with
`SECRET_KEY = '<your-secret-key>'`. You can use `django.core.management.utils.get_random_secret_key()`.
- Your website hostname needs to go in `ALLOWED_HOSTS` list in the appropriate settings file under
`fws_site/settings/` (e.g. `prod.py`) and in the `server_name` directive in `deployment/fws_nginx.conf`. Ideally it should be the only
thing in those lists.

#### Production

1. Install `docker`, `python`, `pip`, and `pipenv` if you haven't already. This varies by distribution and preference.

2. Install dependencies from Pipfile. Alternatively only install django, since it's the only one currently required.
    ```shell
    # Install all dependencies
    pipenv install

    # Only install django
    pipenv install django
    ```

3. Prepare project by running `init.sh` script. This will create required directories and files for deployment.
    ```shell
    ./init.sh
    ```
    * Only docker is required beyond this step, everything else installed in steps 1 and 2 can be safely removed.

4. Initialize database by running:
    ```shell
    docker compose --file docker-compose-prod-manage.yml run manage migrate
    docker compose --file docker-compose-prod-manage.yml run manage loaddata --app ffxivws --format json worlds.fixture.json
    ```

5. Start the web server:
    ```shell
    docker compose --file docker-compose-prod.yml up --remove-orphans
    ```
    * you may append `-d` option at the end of that command to run it in detached mode
