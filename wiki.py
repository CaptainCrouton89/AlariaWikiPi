import difflib
import logging
import os
import re
import time
import uuid
from random import randint
from threading import Thread

import autoLinker
import knowledge_graph
import pypandoc
from config import WikmdConfig
from flask import Flask, redirect, render_template, request, send_from_directory, url_for
from git_manager import WikiRepoManager
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

SYSTEM_SETTINGS = {
    "darktheme": False,
    "listsortMTime": False,
}

cfg = WikmdConfig()
UPLOAD_FOLDER = f"{cfg.wiki_directory}/{cfg.images_route}"

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# console logger
app.logger.setLevel(logging.INFO)

# file logger
logger = logging.getLogger('werkzeug')
logger.setLevel(logging.ERROR)

wrm = WikiRepoManager(flask_app=app)


def save(page_name):
    """
    Function that saves a *.md page.
    :param page_name: name of the page
    """
    content = request.form['CT']
    app.logger.info(f"Saving >>> '{page_name}' ...")

    try:
        filename = os.path.join(cfg.wiki_directory, page_name + '.md')
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(filename, 'w') as f:
            f.write(content)
        autoLinker.auto_link(filename)
        # autoLinker.total_auto_link(filename)
    except Exception as e:
        app.logger.error(f"Error while saving '{page_name}' >>> {str(e)}")


def search():
    """
    Function that searches for a term and shows the results.
    """
    search_term = request.form['ss']
    escaped_search_term = re.escape(search_term)
    found = []
    tag = re.match(r"^tag:", search_term)
    tag_text = search_term.lower().replace(" ", "").replace("tag:", "")

    app.logger.info(f"Searching >>> '{search_term}' ...")

    for root, subfolder, files in os.walk(cfg.wiki_directory):
        for item in files:
            path = os.path.join(root, item)
            if os.path.join(cfg.wiki_directory, '.git') in str(path):
                # We don't want to search there
                app.logger.debug(f"Skipping {path} is git file")
                continue
            if os.path.join(cfg.wiki_directory, cfg.images_route) in str(path):
                # Nothing interesting there too
                continue
            with open(root + '/' + item, encoding="utf8", errors='ignore') as f:
                fin = f.read()  
                fin_tags = fin.partition('\n')[0].lower().replace("tags: ", "").replace(",", "")
                try:
                    if tag and re.search(tag_text, fin_tags, re.IGNORECASE):
                        found.append(get_info_from_item(item, root))
                        app.logger.info(f"Found '{search_term}' in '{item}'")
                    elif (re.search(escaped_search_term, root + '/' + item, re.IGNORECASE) or
                            re.search(escaped_search_term, fin, re.IGNORECASE) is not None):
                        found.append(get_info_from_item(item, root))
                        app.logger.info(f"Found '{search_term}' in '{item}'")
                except Exception as e:
                    app.logger.error(f"Error while searching >>> {str(e)}")

    found = sorted(found, key=lambda x: difflib.SequenceMatcher(None, x["doc"], search_term).ratio(), reverse=True)
    return render_template('search.html', zoekterm=found, system=SYSTEM_SETTINGS)

def get_info_from_item(item, root):
    # Stripping 'wiki/' part of path before serving as a search result
    folder = root[len(cfg.wiki_directory + "/"):]
    if folder == "":
        url = os.path.splitext(
            root[len(cfg.wiki_directory + "/"):] + "/" + item)[0]
    else:
        url = "/" + \
            os.path.splitext(
                root[len(cfg.wiki_directory + "/"):] + "/" + item)[0]

    info = {'doc': item,
            'url': url,
            'folder': folder,
            'folder_url': root[len(cfg.wiki_directory + "/"):]}
    return info
    

def fetch_page_name() -> str:
    page_name = request.form['PN']
    if page_name[-4:] == "{id}":
        page_name = f"{page_name[:-4]}{uuid.uuid4().hex}"
    return page_name


@app.route('/list/', methods=['GET'])
def list_full_wiki():
    return list_wiki("")


@app.route('/list/<path:folderpath>/', methods=['GET'])
def list_wiki(folderpath):
    folder_list = []
    app.logger.info("Showing >>> 'all files'")
    for root, subfolder, files in os.walk(os.path.join(cfg.wiki_directory, folderpath)):
        if root[-1] == '/':
            root = root[:-1]
        for item in files:
            path = os.path.join(root, item)
            mtime = os.path.getmtime(os.path.join(root, item))
            if os.path.join(cfg.wiki_directory, '.git') in str(path):
                # We don't want to search there
                app.logger.debug(f"skipping {path}: is git file")
                continue
            if os.path.join(cfg.wiki_directory, cfg.images_route) in str(path):
                # Nothing interesting there too
                continue

            folder = root[len(cfg.wiki_directory + "/"):]
            if folder == "":
                if item == cfg.homepage:
                    continue
                url = os.path.splitext(
                    root[len(cfg.wiki_directory + "/"):] + "/" + item)[0]
            else:
                url = "/" + \
                    os.path.splitext(
                        root[len(cfg.wiki_directory + "/"):] + "/" + item)[0]

            info = {'doc': item,
                    'url': url,
                    'folder': folder,
                    'folder_url': folder,
                    'mtime': mtime,
                    }
            folder_list.append(info)

    if SYSTEM_SETTINGS['listsortMTime']:
        folder_list.sort(key=lambda x: x["mtime"], reverse=True)
    else:
        folder_list.sort(key=lambda x: (str(x["url"]).casefold()))

    return render_template('list_files.html', list=folder_list, folder=folderpath, system=SYSTEM_SETTINGS)


@app.route('/<path:file_page>', methods=['POST', 'GET'])
def file_page(file_page):
    if request.method == 'POST':
        return search()
    else:
        html = ""
        mod = ""
        folder = ""

        if "favicon" not in file_page:  # if the GET request is not for the favicon
            try:
                md_file_path = os.path.join(cfg.wiki_directory, file_page + ".md")
                # latex = pypandoc.convert_file("wiki/" + file_page + ".md", "tex", format="md")
                # html = pypandoc.convert_text(latex,"html5",format='tex', extra_args=["--mathjax"])

                app.logger.info(f"Converting to HTML with pandoc >>> '{md_file_path}' ...")
                html = pypandoc.convert_file(md_file_path, "html5",
                                             format='md', extra_args=["--wrap=preserve"])

                mod = "Last modified: %s" % time.ctime(os.path.getmtime(md_file_path))
                folder = file_page.split("/")
                file_page = folder[-1:][0]
                folder = folder[:-1]
                folder = "/".join(folder)
                app.logger.info(f"Showing HTML page >>> '{file_page}'")
            except Exception as a:
                app.logger.info(a)

        return render_template('content.html', title=file_page, folder=folder, info=html, modif=mod,
                               system=SYSTEM_SETTINGS)


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        return search()
    else:
        html = ""
        app.logger.info("Showing HTML page >>> 'homepage'")
        try:
            app.logger.info("Converting to HTML with pandoc >>> 'homepage' ...")
            html = pypandoc.convert_file(
                os.path.join(cfg.wiki_directory, cfg.homepage), "html5", format='md', extra_args=["--mathjax"],
                filters=['pandoc-xnos'])

        except Exception as e:
            app.logger.error(f"Conversion to HTML failed >>> {str(e)}")

        return render_template('index.html', homepage=html, system=SYSTEM_SETTINGS)


@app.route('/' + cfg.images_route, methods=['POST', 'DELETE'])
def upload_file():
    app.logger.info(f"Uploading new image ...")
    # Upload image when POST
    if request.method == "POST":
        file_names = []
        for key in request.files:
            file = request.files[key]
            filename = secure_filename(file.filename)
            # bug found by cat-0
            while filename in os.listdir(os.path.join(cfg.wiki_directory, cfg.images_route)):
                app.logger.info(
                    "There is a duplicate, solving this by extending the filename...")
                filename, file_extension = os.path.splitext(filename)
                filename = filename + str(randint(1, 9999999)) + file_extension

            file_names.append(filename)
            try:
                app.logger.info(f"Saving image >>> '{filename}' ...")
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            except Exception as e:
                app.logger.error(f"Error while saving image >>> {str(e)}")
        return filename

    # DELETE when DELETE
    if request.method == "DELETE":
        # request data is in format "b'nameoffile.png" decode by utf-8
        filename = request.data.decode("utf-8")
        try:
            app.logger.info(f"Removing >>> '{str(filename)}' ...")
            os.remove((os.path.join(app.config['UPLOAD_FOLDER'], filename)))
        except Exception as e:
            app.logger.error(f"Could not remove {str(filename)}")
        return 'OK'

# Translate id to page path


@app.route('/nav/<path:id>/', methods=['GET'])
def nav_id_to_page(id):
    for i in links:
        if i["id"] == int(id):
            return redirect("/"+i["path"])
    return redirect("/")


@app.route('/' + cfg.images_route + '/<path:filename>')
def display_image(filename):
    # print('display_image filename: ' + filename)
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=False)


@app.route('/toggle-darktheme/', methods=['GET'])
def toggle_darktheme():
    SYSTEM_SETTINGS['darktheme'] = not SYSTEM_SETTINGS['darktheme']
    return redirect(request.referrer)  # redirect to the same page URL

@app.route('/toggle-sorting/', methods=['GET'])
def toggle_sort():
    SYSTEM_SETTINGS['listsortMTime'] = not SYSTEM_SETTINGS['listsortMTime']
    return redirect("/list")


def run_wiki():
    """
    Function that runs the wiki as a Flask app.
    """
    if int(cfg.wikmd_logging) == 1:
        logging.basicConfig(filename=cfg.wikmd_logging_file, level=logging.INFO)
    
    app.run(host=cfg.wikmd_host, port=cfg.wikmd_port, debug=True, use_reloader=False)


if __name__ == '__main__':
    run_wiki()
