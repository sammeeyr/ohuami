import os
import glob

for app_dir in glob.glob('apps/*'):
    if os.path.isdir(app_dir):
        app_name = os.path.basename(app_dir)
        apps_py = os.path.join(app_dir, 'apps.py')
        if os.path.exists(apps_py):
            with open(apps_py, 'r', encoding='utf-8') as f:
                content = f.read()
            old_str = f"name = '{app_name}'"
            new_str = f"name = 'apps.{app_name}'"
            if old_str in content:
                content = content.replace(old_str, new_str)
                with open(apps_py, 'w', encoding='utf-8') as f:
                    f.write(content)
print("Updated all apps.py configurations successfully.")
