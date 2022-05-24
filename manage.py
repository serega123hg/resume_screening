from flask import Flask, render_template
from flask import request


from Routes.index import index1
from Routes.soiscatel import soiscatel
from Routes.hr import hr
from Routes.vacancy_apply import vacancy_apply
from Routes.vacancy import vacancy


app = Flask(__name__)
app.config['DEBUG'] = True
app.config["const uri"]  = "MONGODB_URI"

# папка для сохранения загруженных файлов
UPLOAD_FOLDER = '/resumes'
# расширения файлов, которые разрешено загружать
ALLOWED_EXTENSIONS = {'pdf','docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['SECRET_KEY'] = 'fdgdfgdfggf786hfg6hfg6h7f'

app.register_blueprint(index1)
app.register_blueprint(soiscatel)
app.register_blueprint(hr)
app.register_blueprint(vacancy_apply)
app.register_blueprint(vacancy)
# app.register_blueprint(callcenter)
# app.register_blueprint(enterManager)
# app.register_blueprint(enterCall)
# app.register_blueprint(enterSup)


if __name__ == "__main__":
    app.run()

