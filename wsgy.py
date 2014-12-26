# Librerias de Sistema
import os
import datetime


# Libreria para parseao de xml
from xml.dom.minidom import *

# Librerias de Flask
from flask import render_template, request, Flask, flash, redirect, url_for, \
    abort, jsonify, Response, make_response, send_from_directory
from werkzeug.utils import secure_filename
# from werkzeug.security import check_password_hash

# from werkzeug.contrib.cache import FileSystemCache, NullCache
##############################################



app = Flask(__name__)


# Vbles para el control del parseado de ficheros
ALLOWED_EXTENSIONS = set(['txt', 'xml'])
XML_PARSEADO=""

# FUNCION: allowed_file
# parametros: 
#    * filename: nombre del fichero que se ha subido por web
# retorno:
#    * True o False en funcion de si el fichero tiene una extension permitida en la lista de ALLOWED_EXTENSIONS
# Uso:
#   Verificar que la extension del fichero es correcta
def allowed_file(filename):
    global ALLOWED_EXTENSIONS
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


# ROUTE: /
#   Uso: URI para desplegar la APP 
#   Funcion asociada: default
# FUNCION: default
# parametros: 
#    * 
# retorno:
#    * Respuesta HTML en el navegador
# Uso:
#   Crear el formulario web para solicitar la transformacion del XML
@app.route('/', methods=['GET', 'POST'])
def default():
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
    return renderizar_html_no_cache(respuesta)



# ROUTE: /upload
#   Uso: URI para subir fichero y leerlo 
#   Funcion asociada: upload_file
# FUNCION: upload_file
# parametros: 
#    * 
# retorno:
#    * Respuesta HTML en el navegador
# Uso:
#   Subir el contenido del XML, leerlo e invocar a la funcion de parseado. Devuelve una salida HTML para el fichero o para el error encontrado
@app.route("/upload", methods=["POST"])
def upload_file():
    global XML_PARSEADO
    # Solo se permite el method POST para la subida
    if request.method == 'POST':
        idioma=request.form['idioma']
        file_upload = request.files['file']
            
        # Se verifica que el fichero tiene una extension permitida (XML o TXT)
        if file and allowed_file(file_upload.filename):
            filename = secure_filename(file_upload.filename)

            # Se lee el contenido del fichero con la el metodo stream.read() de Flask
            cadena=file_upload.stream.read()

            # Parseamos la cadena XML
            XML_PARSEADO=parsear(cadena,request.form['idioma'])

            # Se construye la respuesta HTML
            url=""
            respuesta= '''
              <!doctype html>
              <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
              <html>
              <title>Convertir XML i18n</title>
              <body>
              <h1>Convertir XML i18n</h1>
              <p>Cambios de idioma <b>[%s]</b> aplicados: <a href="/download/%s" target="_blank">%s</a></p>
              </body>
              </html>
              '''%(idioma,filename,filename)
            #print XML_PARSEADO

            return renderizar_html_no_cache(respuesta)
        else:
          return renderizar_html_no_cache("No es un tipo fichero permitido. Utilice XML o TXT")
    else:
      return renderizar_html_no_cache("Error en la subida")
            

# ROUTE: /download/<filename>
#   Uso: URI para descargar el XML parseado con el mismo nombre que el original
#   Funcion asociada: download_file
# FUNCION: download_file
# parametros: 
#    * filename: nombre del fichero que se quiere devolver
# retorno:
#    * Respuesta XML en el navegador
# Uso:
#   Devolver el contenido XML como "text/xml"
@app.route('/download/<filename>')
def download_file(filename):
  global XML_PARSEADO
  resp=renderizar_html_no_cache(XML_PARSEADO)
  return resp,200,{'Content-Type': 'text/xml; charset=utf-8'}

# renderizar_html_no_cache:
# parametros: 
#    * respuesta: contenido que se quiere pintar en pantalla
# retorno:
#    * Objeto response que se sirve en pantalla
# Uso:
#   Incrustar cabeceras de NO-CACHE paratoda peticion
def renderizar_html_no_cache(respuesta):
    response = make_response(respuesta)

    response.headers.add('Last-Modified', datetime.datetime.now())
    response.headers.add('Cache-Control', 'no-store, no-cache, must-revalidate, post-check=0, pre-check=0, max-age=0')
    response.headers.add('Pragma','no-cache')
    response.headers.add('Expires', '-1')
    return response


# parsear:
# parametros: 
#    * contenido: contenido del fichero subido
#    * idioma: idioma indicado en el formulario web
# retorno:
#    * String con el contenido del XML parseado
# Uso:
#   El objetivo de esta funcion es:
#     1. incluir una cabecera comun en el XML
#     2. Dado que la traduccion, sea el idioma que sea, viene en el nodo "es", lo que hara es:
#       2.1. Eliminar los nodos vacios que no sean "es"
#       2.2. Reemplazar el identificador del nodo "es" por el del idioma que han pasado en el formulario web
def parsear(contenido, idioma):
    xmlDocument = xml.dom.minidom.parseString(contenido)
    #print "parsear",xmlDocument
    elemento=xmlDocument.getElementsByTagName("i18n")
    
    # 1. Cambio de las cabeceras
    for n in elemento:
        n.setAttribute("languages","es|en|fr|ro|pt-br|it")
        
    elemento=xmlDocument.getElementsByTagName("definitions")
    for n in elemento:
        n.setAttribute("languages","es|en|fr|ro|pt-br|it")
    # End 1.
    
    list = xmlDocument.getElementsByTagName("text")
    for node in list:
        if node.getAttribute("language")!="es":
            # 2.1. Eliminacion de nodos !="es"
            parent = node.parentNode
            parent.removeChild(node)
        else:
            # 2.2. Reemplazar atributo "es" por "idioma"
            node.setAttribute("language",idioma)

    cadena=xmlDocument.toxml("utf-8")
    return cadena


# APP lanzada para cualquier ip en el puerto 5000
if __name__ == '__main__':
  # app.debug = True
  port = int(os.environ.get('PORT', 5000))
  app.run(host='0.0.0.0', port=port)