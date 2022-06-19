from flask import Flask, render_template
from flask import request


from Routes.index import index1
from Routes.soiscatel import soiscatel
from Routes.hr import hr
from Routes.vacancy_apply import vacancy_apply
from Routes.vacancy import vacancy
from Routes.evalcandidates import eval


app = Flask(__name__)


# папка для сохранения загруженных файлов
UPLOAD_FOLDER = './uploads'
# расширения файлов, которые разрешено загружать
ALLOWED_EXTENSIONS = {'pdf','docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

app.config['SECRET_KEY'] = ''

app.register_blueprint(index1)
app.register_blueprint(soiscatel)
app.register_blueprint(hr)
app.register_blueprint(vacancy_apply)
app.register_blueprint(vacancy)
app.register_blueprint(eval)



if __name__ == "__main__":
    app.run()