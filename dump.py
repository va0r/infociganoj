if __name__ == '__main__':

    from config.settings import INSTALLED_APPS
    import os

    installed_apps = INSTALLED_APPS[10:]

    for _ in installed_apps:

        json_file_name = f'{_}_data.json'
        print(f'{json_file_name = }')
        app_name = f'{_}'
        print(f'{app_name = }')

        try:
            os.system(f'python3 manage.py dumpdata {app_name} > {json_file_name}')
            print(f'{_.upper()} dumped')
        except OSError:
            f'{OSError = }'
