import shutil
import json
import os


_ROOT = os.path.abspath(os.path.dirname(__file__))

def generate_app(name: str, pathname: str):
    # Determine app name and directory
    app_name = name or "my-app"
    
    # construct templates path
    template_directory = os.path.join(_ROOT, 'templates/python')

    try:
        # Copy tree from src = template_directory to dest = chosen
        dest_directory = shutil.copytree(template_directory, pathname)

        # Write the app.json file into the directory
        generate_app_json(pathname)
    except Exception as e:
        print(e)
        raise
        

    print("Application successfully initialized!")
    print("You can start interacting with Meroxa in your app located at {}"
          .format(dest_directory))


def generate_app_json(app_name: str):

    app_json = dict(name=app_name, language="python")

    try:
        with open(app_name + '/app.json', 'w', encoding='utf-8') as fp:
            json.dump(app_json, fp, ensure_ascii=False, indent=4)
    except Exception as e:
        print(e)
