from flask import Flask,render_template, request, redirect, url_for
from PIL import Image
import hashlib
from datetime import datetime
import logging
import traceback

app = Flask(__name__)

canvas_file = 'static/img/canvas.png'
canvas_file_date = 'static/img/canvas_{date}.png'
user_log_filename = 'logs/users.log'
user_action_log_filename = 'logs/users_action.log'
visitor_log_filename = 'logs/visitors.log'

logging.basicConfig(filename='logs/debug.log', level=logging.DEBUG)


@app.route("/<location>.html")
def google_auth(location):
    return render_template(f"{location}.html")

@app.route("/", methods=['POST','GET'])
def index():
    log_visitor(request.headers['X-Forwarded-For'].split(',')[0])
    x = 0
    y = 0
    color = '#000000'
    img = ''
    if request.method == "POST":
        if check_user(request.headers['X-Forwarded-For'].split(',')[0]):
            try:
                logging.debug(f'RF:{request.form}')
                if 'x' in request.form:
                    print("FORM")
                    x = int(request.form['x'])
                    y = int(request.form['y'])
                    color = tuple(int(request.form['color'][1:][i:i+2], 16) for i in (0, 2, 4))    
                    hex_color = request.form['color'][1:]  
                    imagefile = request.files.get('img', '')
                    if imagefile:
                        filename = request.files['img'].filename
                        if addImage(x,y,imagefile,filename,request.headers['X-Forwarded-For'].split(',')[0]) == 'ERROR':
                            return "Failed to add to canvas. :("
                        log_user_action(request.headers['X-Forwarded-For'].split(',')[0], f'({x}, {y})', f'image: {filename}')
                    else:
                        if addPixel(x,y,color,request.headers['X-Forwarded-For'].split(',')[0]) == 'ERROR':
                            return "Failed to add to canvas. :("
                        log_user_action(request.headers['X-Forwarded-For'].split(',')[0], f'({x}, {y})', f'color: {color}')
                log_user(request.headers['X-Forwarded-For'].split(',')[0])
            except Exception as e:
                print(e)
                logging.error(f'post home:(e)')
                return "Failed to add to canvas. :("
            return "Success!"
        else:
            return "Failed to add to canvas because your time is not up! :("
    return render_template('index.html', x=x, y=y, color=color, visitors=countVisitors(), hash=getImageHash())

@app.route("/imghash")
def getImageUpdate():
    return f'{getImageHash()}|{countVisitors()}'

def getImageHash():
    try:
        with open(canvas_file, "r", errors='ignore') as f:
            return hashlib.sha256(f.read().encode()).hexdigest()
    except Exception as e:
        logging.error(f'getImageHash:{e}:{traceback.print_exc()}')
        return 'none'

def check_user(user:str):
    try:
        user_in_log = [_ for _ in open(user_log_filename, 'r').read().split('\n') if user in _]
        if user_in_log:
            now = datetime.now()
            if user_in_log[0].split('|')[1] != f'{now.hour}:{now.minute}':
                user_log = open(user_log_filename, 'r').read().replace(user_in_log[0]+'\n','')
                new_user_log = open(user_log_filename, 'w')
                new_user_log.write(user_log)
                new_user_log.close()
                return True
            return False
        return True
    except Exception as e:
        logging.error(f'CheckUser:{user}:{e}:{traceback.print_exc()}')

def log_user(user:str):
    try:
        user_log = open(user_log_filename, 'a')
        now = datetime.now()
        user_log.write(f'{user}|{now.hour}:{now.minute}\n')    
        user_log.close()
    except Exception as e:
        logging.error(f'LogUser:{user}:{e}:{traceback.print_exc()}')

def log_user_action(user:str, location:str, action:str):
    try:
        user_log = open(user_action_log_filename, 'a')
        now = datetime.now()
        user_log.write(f'{user}|{now}:{location} {action}\n')    
        user_log.close()
    except Exception as e:
        logging.error(f'LogUserAction:{user}:{e}:{traceback.print_exc()}')

def log_visitor(user:str):
    try:
        if user in open(visitor_log_filename, 'r').read():
            return
        visitor_log = open(visitor_log_filename, 'a')
        visitor_log.write(f'{user}\n')    
        visitor_log.close()
    except Exception as e:
        logging.error(f'LogVisitor:{user}:{e}:{traceback.print_exc()}')
        

def countVisitors():
    return len(open(visitor_log_filename, 'r').read().strip().split('\n'))

def addImage(x:int,y:int,image,filename:str,user:str):
    try:
        print(canvas_file)
        canvas = Image.open(canvas_file).convert("RGBA")
        now = datetime.now()
        canvas.save(canvas_file_date.format(date=str(now).replace(' ','_')))
        user_image = Image.open(image).convert("RGBA")
        user_image.thumbnail((100,100))
        canvas.paste(user_image,(x,y),user_image)
        canvas.save(canvas_file, format="png")
    except Exception as e:
        logging.error(f'ADDIMAGE:{user}:{filename}:{e}:{traceback.print_exc()}')
        return "ERROR"
    return "SUCCESS"

def addPixel(x:int,y:int,color:str,user:str):
    try:
        canvas = Image.open(canvas_file)
        now = datetime.now()
        canvas.save(canvas_file_date.format(date=str(now).replace(' ','_')))
        pixel_map = canvas.load()
        if canvas.size[0] < x:
            x = 0
        if canvas.size[1] < y:
            y = 0
        pixel_map[int(x),int(y)] = color
        canvas.save(canvas_file)
    except Exception as e:
        logging.error(f'ADDPIXEL:{user}:{e}:{traceback.print_exc()}')
        return "ERROR"
    return "SUCCESS"