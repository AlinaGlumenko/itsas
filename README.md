### Для запуска проекта в ПЕРВЫЙ РАЗ на своем компьютере нужно:
1. Удалить папку "venv".
2. Открыть консоль cmd.
3. Перейти в папку с проектом.
4. Ввести команду "python -m venv env" (нужно, чтобы Python 3.7.5 был установлен на компьютере).
5. После чего ввести команду "venv/scripts/activate".
    ПРИМЕЧАНИЕ: Если не работает команда и выдает ошибку. Нужно: 
                5.1. Перейти в PowerShell (через поиск в Windows 10).
                5.2. Ввести команду "Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser".
                5.3. Попробовать снова ввести команду "venv/scripts/activate" в консоль cmd.
6. Затем команду "pip install -r requirements.txt".


### В дальнейшем для запуска нужно:
1. Ввести в консоль: env/scripts/activate 
2. Ввести в консоль: python app.py


# create new venv
python -m venv <name>

# activate venv
env/scripts/activate

# start app
python main.py

# freeze libs
pip freeze > requirements.txt

# install libs
pip install -r requirements.txt

# история команд
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
