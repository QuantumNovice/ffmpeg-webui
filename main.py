import os
from flask import *
from werkzeug.utils import secure_filename
from threading import Thread
import yaml


#######################################################

with open('config.yaml') as file:
    config = yaml.load(file, Loader=yaml.SafeLoader)

print(config)
#######################################################

SECRET_KEY = os.urandom(24)
UPLOAD_FOLDER = "uploads"

IMG_EXT = ['png', 'jpg', 'jpeg', 'gif', 'webp']
ALLOWED_EXTENSIONS = ['mp4', 'mkv', 'avi', '3gp']+ IMG_EXT
ALLOWED_EXTENSIONS = set(ALLOWED_EXTENSIONS)
ROOT_URL = config['app_root']

app = Flask(__name__, template_folder='src')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

FFMPEG_PROCESSED_FLAG = False



def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def optimize_file(filename):
    def optimize(filename):
        global FFMPEG_PROCESSED_FLAG
        os.system(f"ffmpeg -y -i {filename} {filename}")
        FFMPEG_PROCESSED_FLAG = True
    print(filename)
    Thread(target=optimize, args=(filename,)).start()


@app.route(ROOT_URL, methods=['GET', 'POST'])
def index_handler():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        _file = request.files['file']

        # if user does not select file, browser also
        # submit an empty part without filename
        if _file.filename == '':
            flash('No selected file')
            return redirect(request.url)


        if _file and allowed_file(_file.filename):
            filename = secure_filename(_file.filename)
            extension = filename.split('.')[-1]
            is_img = False
            if extension in IMG_EXT:
                is_img = True
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            _file.save(file_path)

            FFMPEG_PROCESSED_FLAG = False
            os.system(f"ffmpeg -y -i {file_path} {file_path}")
            #optimize_file(file_path)
            img_url = url_for('uploaded_file',
                                    filename=filename)
            print(filename)
            return render_template("image.html", img_url=img_url, conversion_status=FFMPEG_PROCESSED_FLAG, is_img=is_img)

    return render_template("index.html")

@app.route(ROOT_URL+'/uploads/<filename>')
def uploaded_file(filename):

    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)


if __name__=='__main__':
    
    app.run(host=config['ip'], port=config['port'], debug=config['debug'])

