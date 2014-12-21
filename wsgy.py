import os
from flask import Flask
from flask import render_template
from flask import  request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory
import sys
import codecs
from xml.dom.minidom import *


""" simple """

# python imports
import re
import datetime
import os
import time

from functools import wraps
from unicodedata import normalize
from os import urandom
from base64 import b32encode
# from email import utils
# web stuff and markdown imports
# import markdown
#from flask.ext.sqlalchemy import SQLAlchemy
#from sqlalchemy.orm.exc import NoResultFound
from werkzeug.security import check_password_hash
from flask import render_template, request, Flask, flash, redirect, url_for, \
    abort, jsonify, Response, make_response
from werkzeug.contrib.cache import FileSystemCache, NullCache
from werkzeug.utils import secure_filename
import json
from flask import send_from_directory


app = Flask(__name__)


UPLOAD_FOLDER = 'uploads/'
ALLOWED_EXTENSIONS = set(['txt', 'xml'])
app.config['UPLOAD_FOLDER'] = os.path.join(os.getcwd(),UPLOAD_FOLDER)
#app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

XML_PARSEADO=""


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def default():
    XML_PARSEADO=""
    respuesta= '''
    <!doctype html>
    <html>
    <title>Convertir XML i18n</title>
    <body>
    <h1>Convertir XML i18n: </h1>
    <form action="/upload" method="POST" enctype="multipart/form-data">
     <p>Idioma del fichero final: <input type="text" name="idioma" placeholder="Idioma: es|en|fr|pt-br|ro|..."/></p>
      <p>Fichero:<input type="file"  name="file"/></p>
      <p><input type=submit value="Convertir"/></p>
    </form>
    </body>
    </html>
    '''
    return renderizar_html(respuesta)



@app.route("/upload", methods=["POST"])
def upload_file():
    global XML_PARSEADO
    #print "upload_file -> method:",request.method
    if request.method == 'POST':
        idioma=request.form['idioma']
        file_upload = request.files['file']
        #print "upload_file -> file_upload.filename:",file_upload.filename,allowed_file(file_upload.filename)
        
            
        if file and allowed_file(file_upload.filename):
            filename = secure_filename(file_upload.filename)
            #print "upload_file -> secure_filename:",filename
        
            ##print "upload_file -> content:",file_upload.stream.read()
            #xml_final=parsear(file_upload.stream.read(),request.form['idioma'],filename)
            cadena=file_upload.stream.read()
            ##print "upload_file -> xml_final:",cadena
            
            XML_PARSEADO=parsear(cadena,request.form['idioma'])
            ##print "XML",xml_final
            #url = url_for('uploaded_file', filename=fichero_final)
            url=""
            respuesta= '''
              <!doctype html>
              <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
              <html>
              <title>Convertir XML i18n</title>
              <body>
              <h1>Convertir XML i18n</h1>
              <p>Cambios de idioma <b>[%s]</b> aplicados: <a href="/download/%s">%s</a></p>
              </body>
              </html>
              '''%(idioma,filename,filename)
            #print XML_PARSEADO

            return renderizar_html(respuesta)
            #return json.dumps({'status': 'ok', 'url': url, 'name': filename, 'name_orig': filename_orig,'fichero_final': fichero_final,'idioma':idioma})
        else:
          return renderizar_html("No es un tipo fichero permitido. Utilize XML o TXT")
    else:
      return renderizar_html("Error en la subida")
            

@app.route('/download/<filename>')
def download_file(filename):
  global XML_PARSEADO
  ##print "download_file",XML_PARSEADO
  
  response=make_response(XML_PARSEADO)
  response.headers.add('Last-Modified', datetime.datetime.now())
  response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0')
  response.headers.add('Pragma','no-cache')
  response.headers.add('Expires', '-1')

  #return Response(XML_PARSEADO, mimetype='text/xml')
  return response,200,{'Content-Type': 'text/xml; charset=utf-8'}

def renderizar_html(respuesta):
    response = make_response(respuesta)

    response.headers.add('Last-Modified', datetime.datetime.now())
    response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0')
    response.headers.add('Pragma','no-cache')
    response.headers.add('Expires', '-1')
    return response

def parsear(contenido, idioma):
    xmlDocument = xml.dom.minidom.parseString(contenido)
    #print "parsear",xmlDocument
    elemento=xmlDocument.getElementsByTagName("i18n")
    for n in elemento:
        n.setAttribute("languages","es|en|fr|ro|pt-br|it")
        
    elemento=xmlDocument.getElementsByTagName("definitions")
    for n in elemento:
        n.setAttribute("languages","es|en|fr|ro|pt-br|it")
    
    
    list = xmlDocument.getElementsByTagName("text")
    for node in list:
        if node.getAttribute("language")!="es":
            parent = node.parentNode
            parent.removeChild(node)
        else:
            node.setAttribute("language",idioma)

    cadena=xmlDocument.toxml("utf-8")
    return cadena

if __name__ == '__main__':
  # app.debug = True
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)