### To start project at first time:
1. Remove die "venv".
2. Open terminal/cmd.
3. Choose dir with project.
4. Enter the command "python -m venv env".
5. Enter the command "env/scripts/activate".
    NOTICE: If it doesn't work. You need: 
                5.1. Open PowerShell (in Windows 10).
                5.2. Enter the command "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser".
                5.3. Try again to enter the command "venv/scripts/activate" to the terminal.
6. Enter the command "pip install -r requirements.txt".

# Commands
## To start app:
1. Enter to the terminal to activate venv: env/scripts/activate 
2. Enter to the terminal to start flask server: python app.py

### create new venv
python -m venv <name>

#### freeze libs to requirements.txt
pip freeze > requirements.txt

### install libs from requirements.txt
pip install -r requirements.txt

## Used commands
1. python -m pip install --upgrade pip wheel setuptools virtualenv
2. python -m pip install flask
3. python -m pip install pandas
4. python -m pip install xlrd
5. python -m pip install xlsxwriter
6. python -m pip install openpyxl
7. python -m pip install sklearn
8. python -m pip install python-magic
9. python -m pip install python-magic-bin
10. python -m pip install
