"""Instructions:
1. Install all required packages by running:
pip install -e .[dev]
2. Install winrar as followed:
https://visatch.medium.com/python-rarfile-package-error-rarfile-rarcannotexec-cannot-find-working-tool-window-only-630ff25f4ef8
3. Move all-grades zip under hw1 folder
4. Run the script as an administrator (permissions required)
"""

import glob
import os
import re
import shutil
import stat
from zipfile import ZipFile

import pandas as pd
from rarfile import RarFile

# Define paths
root_folder = ".\\src\\hw1"
temp_folder = ".\\temp"
output_file = "grades.csv"

jupyter_libs = [
    "notebook",
    "jupyterlab",
    "ipykernel",
    "nbconvert",
    "nbformat",
    "jupyter-client",
    "jupyter-console",
    "ipywidgets",
    "qtconsole",
]
jupyter_vsc_extention_identifier = "ms-toolsai.jupyter"


def extractCompresedFile(file_indicator, zip_folder_path, extract_folder_path) -> None:
    student_folder_path_zip = glob.glob(f"{zip_folder_path}/*.zip")
    student_folder_path_rar = glob.glob(f"{zip_folder_path}/*.rar")

    if student_folder_path_zip:
        with ZipFile(student_folder_path_zip[0], "r") as zip_ref:
            zip_ref.extractall(extract_folder_path)
            return
    if student_folder_path_rar:
        with RarFile(student_folder_path_rar[0], "r") as zip_ref:
            zip_ref.extractall(extract_folder_path)
            return
    print(f"no zip file found for {file_indicator}")


def handle_readonly(func, path, exc_info):
    """Handle permission errors by making the file writable and retrying."""
    if not os.access(path, os.W_OK):  # Check if the path is writable
        os.chmod(path, stat.S_IWRITE)  # Change to writable
        func(path)  # Retry the function (e.g., os.remove or os.rmdir)
    else:
        raise  # Reraise the exception if it's not a permission issue


def delete_folder_if_needed(path) -> None:
    if os.path.exists(path):
        shutil.rmtree(path, onerror=handle_readonly)


def delete_file_if_needed(path) -> None:
    if os.path.exists(path):
        os.remove(path)


def save_dic_to_csv_file(dic, csv_path):
    # Convert the dictionary to a DataFrame
    df = pd.DataFrame.from_dict(dic, orient="index")
    df.to_csv(csv_path, encoding="utf-8-sig")


def init_student_entry(grades, student_name):
    student = grades[student_name] = {}
    student["grade"] = 0
    student["jupyter_notebook_dependency_added"] = False
    student["jupyter_notebook_vsc_extention_added"] = False


def calculate_grades() -> list:
    delete_file_if_needed(os.path.join(root_folder, output_file))
    delete_folder_if_needed(os.path.join(root_folder, temp_folder))
    grades = {}
    all_students_zip_file = glob.glob(f"{root_folder}/*.zip")[0]
    # zip of all students homeworks
    with ZipFile(all_students_zip_file, "r") as z:
        temp_folder_path = os.path.join(root_folder, temp_folder)
        z.extractall(path=temp_folder_path)
        # Root file of a student hw
        for student_folder in os.listdir(os.path.join(root_folder, temp_folder)):
            # initiate student grade
            student_name = re.split("_", student_folder)[0]
            init_student_entry(grades, student_name)
            student = grades[student_name]
            # extracting files under student folder
            student_folder_path = os.path.join(temp_folder_path, student_folder)
            extract_student_path = os.path.join(student_folder_path, "extract")
            extractCompresedFile(student_name, student_folder_path, extract_student_path)

            # searching for toml file and checking if it contains jupyter dependency
            toml_file = glob.glob("**/*.toml", root_dir=extract_student_path, recursive=True)
            if toml_file:
                with open(os.path.join(extract_student_path, toml_file[0])) as project_config:
                    if (any(jup_lib in project_config.read()) for jup_lib in jupyter_libs):
                        student["jupyter_notebook_dependency_added"] = True
                        student["grade"] += 80

            # searching for code-workspace file and checking if it contains recommandation for jupyter extention
            code_workspace_file = glob.glob("**/*.code-workspace", root_dir=extract_student_path, recursive=True)
            if code_workspace_file:
                with open(os.path.join(extract_student_path, code_workspace_file[0])) as vsc_config:
                    if jupyter_vsc_extention_identifier in vsc_config.read():
                        student["jupyter_notebook_vsc_extention_added"] = True
                        student["grade"] += 20
    return grades


if __name__ == "__main__":
    save_dic_to_csv_file(calculate_grades(), os.path.join(root_folder, output_file))
