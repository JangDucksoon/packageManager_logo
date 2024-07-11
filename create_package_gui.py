import os
import sys
import tkinter as tk
import subprocess
import configparser
import create_java as cj
from tkinter import filedialog, simpledialog, messagebox
from PIL import Image, ImageTk

config = None

config_dir = 'C:\\Temp'
os.makedirs(config_dir, exist_ok=True)
config_file = os.path.join(config_dir, 'JavaPackageCreator_config_logo.ini')


def load_config():
    global config
    config = configparser.ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file)
        if 'PATHS' not in config or 'git_repo_path' not in config['PATHS']:
            config['PATHS'] = {'git_repo_path': ''}
            save_config(config)
    else:
        config['PATHS'] = {'git_repo_path': ''}
        with open(config_file, 'w') as configfile:
            config.write(config_file)
    return config


def save_config(config):
    with open(config_file, 'w') as configfile:
        config.write(configfile)


# Git 저장소 경로 선택 함수
def select_git_repo_path():
    git_repo_path = filedialog.askdirectory(title='Select the Git repository path')
    if git_repo_path:
        config['PATHS']['git_repo_path'] = git_repo_path
        save_config(config)
        update_git_repo_path_label()
    return git_repo_path


def images_path(relative_path):
    try:
        base_path = os.path.join(sys._MEIPASS, 'images')
    except AttributeError:
        base_path = os.path.abspath("./images")

    return os.path.join(base_path, relative_path)


def create_package(base_path, new_package_name, clazz_name):
    base_path = os.path.abspath(base_path)
    package_path = os.path.join(base_path, new_package_name.replace('.', os.sep))
    web_package_path = os.path.join(package_path, 'web')
    service_package_path = os.path.join(package_path, 'service')
    serviceImpl_package_path = os.path.join(service_package_path, 'impl')
    git_repo_path = config['PATHS'].get('git_repo_path', '')

    try:
        os.makedirs(web_package_path, exist_ok=True)
        os.makedirs(service_package_path, exist_ok=True)
        os.makedirs(serviceImpl_package_path, exist_ok=True)

        if clazz_name:
            cj.create_controller_java(web_package_path, clazz_name)
            cj.create_service_java(service_package_path, clazz_name)
            cj.create_serviceImpl_java(serviceImpl_package_path, clazz_name)

            if git_repo_path:
                try:
                    subprocess.run(['git', 'add', os.path.join(web_package_path, '*')], cwd=git_repo_path, shell=True,
                                   check=True)
                    subprocess.run(['git', 'add', os.path.join(service_package_path, '*')], cwd=git_repo_path,
                                   shell=True, check=True)
                except subprocess.CalledProcessError as e:
                    messagebox.showerror('git fail', 'Failed to add the file to the Git repository.')

        messagebox.showinfo('success', 'packages are made')
    except Exception as e:
        print(e)
        messagebox.showerror('error', 'can not make packages')


def select_base_path():
    base_path = filedialog.askdirectory(title='select the root package')
    if base_path:
        package_name = simpledialog.askstring('package name', 'write the package\'s name : \t\t\t')
        if package_name:
            clazz_name = simpledialog.askstring('class word',
                                                'The name of the class must follow PascalCase rules : \t\t\t')
            create_package(base_path, package_name, clazz_name)


def update_git_repo_path_label():
    git_repo_path = config['PATHS'].get('git_repo_path', '')

    if not git_repo_path:
        git_repo_path = "Not selected"

    git_repo_path_label.config(text=f'Git Repository: {git_repo_path}')


def change_git_repo_path():
    git_repo_path = select_git_repo_path()
    if git_repo_path:
        git_repo_path_label.config(text=f"Git Repository: {git_repo_path}")


def resize_image(event):
    new_width = event.width
    new_height = event.height
    image = background_image.resize((new_width, new_height), Image.LANCZOS)
    background_photo = ImageTk.PhotoImage(image)
    frame.create_image(0, 0, image=background_photo, anchor='nw')
    frame.image = background_photo  # Keep a reference to prevent garbage collection


root = tk.Tk()
root.title("package creator")
root.geometry("500x450")
root.iconbitmap(images_path('rm_ico.ico'))

background_image = Image.open(images_path('rm_logo.png'))

frame = tk.Canvas(root, width=500, height=450)
frame.grid(row=1, column=0, sticky="nsew")
frame.bind("<Configure>", lambda event, canvas=frame: resize_image(event))

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(0, weight=1)

top_frame = tk.Frame(root)
top_frame.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
top_frame.grid_columnconfigure(0, weight=1)
top_frame.grid_columnconfigure(1, weight=0)
top_frame.grid_columnconfigure(2, weight=1)

git_repo_path_label = tk.Label(top_frame, text="Git Repository: Not selected")
git_repo_path_label.grid(row=0, column=1, sticky="e")

change_git_repo_button = tk.Button(top_frame, text="...", command=change_git_repo_path)
change_git_repo_button.grid(row=0, column=2, padx=5, sticky="w")

select_button = tk.Button(root, text="select package and create", command=select_base_path)
select_button.grid(row=2, column=0, pady=20)

load_config()
update_git_repo_path_label()

root.mainloop()
