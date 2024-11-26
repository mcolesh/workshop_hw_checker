"""Instructions:
1. Install all required packages by running:
pip install -e .[dev]
2. Install winrar as followed:
https://visatch.medium.com/python-rarfile-package-error-rarfile-rarcannotexec-cannot-find-working-tool-window-only-630ff25f4ef8
3. Move all-grades zip under hw1 folder
"""

import glob
import os
import re
from zipfile import ZipFile

from rarfile import RarFile

# Define paths
parent_folder = ".\\src\\hw1"
output_folder = os.path.join(parent_folder, "\\grades")
temp_folder = ".\\temp"
# Ensure output folder exists
os.makedirs(output_folder, exist_ok=True)

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


def extractCompresedFile(student_name, student_folder_path, extract_path) -> None:
    student_folder_path_zip = glob.glob(f"{student_folder_path}/*.zip")
    student_folder_path_rar = glob.glob(f"{student_folder_path}/*.rar")

    if student_folder_path_zip:
        with ZipFile(student_folder_path_zip[0], "r") as zip_ref:
            zip_ref.extractall(extract_path)
            return
    if student_folder_path_rar:
        with RarFile(student_folder_path_rar[0], "r") as zip_ref:
            zip_ref.extractall(extract_path)
            return
    print(f"no zip file found under {student_name}")


def delete_temp_folder() -> None:
    os.remove(os.path.join(parent_folder, temp_folder))


def calculate_grades(grades) -> list:
    delete_temp_folder()
    grades = {}
    all_students_zip_file = glob.glob(f"{parent_folder}/*.zip")[0]
    # zip of all students homeworks
    with ZipFile(all_students_zip_file, "r") as z:
        temp_folder_path = os.path.join(parent_folder, temp_folder)
        z.extractall(path=temp_folder_path)
        # Root file of a student hw
        for student_folder in os.listdir(os.path.join(parent_folder, temp_folder)):
            # initiate student grade
            student_name = re.split("_", student_folder)[0]
            grades[student_name] = {"grade": 0}
            student_grade = grades[student_name]
            # extracting files under student folder
            student_folder_path = os.path.join(temp_folder_path, student_folder)
            extract_student_path = os.path.join(student_folder_path, "extract")
            extractCompresedFile(student_name, student_folder_path, extract_student_path)
            # searching for toml file and checking if it contains jupyter dependency
            toml_file = glob.glob("**/*.toml", root_dir=extract_student_path, recursive=True)
            if toml_file:
                with open(os.path.join(extract_student_path, toml_file[0])) as project_config:
                    if (any(jup_lib in project_config.read()) for jup_lib in jupyter_libs):
                        student_grade["jupyter_notebook_dependency_exists"] = True
                        student_grade["grade"] += 80
            # searching for code-workspace file and checking if it contains recommandation for jupyter extention
            code_workspace_file = glob.glob("**/*.code-workspace", root_dir=extract_student_path, recursive=True)
            if code_workspace_file:
                with open(os.path.join(extract_student_path, code_workspace_file[0])) as vsc_config:
                    if jupyter_vsc_extention_identifier in vsc_config.read():
                        student_grade["jupyter_notebook_vsc_extention_exists"] = True
                        student_grade["grade"] += 20
            """
                        for root, dirs, files in os.walk(extract_student_path):
                if file.endswith("toml"):
                    toml_file = open(os.path.join(extract_student_path, file))
                    if (any(jup_lib in toml_file.read()) for jup_lib in jupyter_libs):
                        student_grade["jupyter_notebook_dependency_exists"] = True
                if file.endswith("code-workspace"):
                    student_grade["grade"] += 50
                    code_workspace_file = open(os.path.join(extract_student_path, file))
                    if jupyter_vsc_extention_identifier in code_workspace_file:
                        student_grade["jupyter_notebook_vsc_extention_exists"] = True
                        student_grade["grade"] += 50
            """
    return grades


print(calculate_grades(grades))
