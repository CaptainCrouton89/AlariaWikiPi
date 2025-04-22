import json
import logging
import os
import re
import uuid
from typing import Any, Dict, List, Optional

from agents.tool import function_tool
from config import WikmdConfig
from flask import url_for
from openai import OpenAI

# Initialize config for wiki directory
cfg = WikmdConfig()
logger = logging.getLogger(__name__)

def search_notes(query: str) -> List[Dict[str, Any]]:
    """
    Search for notes in the wiki that match the query
    
    Args:
        query: The search query string
        
    Returns:
        A list of dictionaries containing information about matching notes
    """
    logger.info(f"Agent searching for: {query}")
    
    escaped_search_term = re.escape(query)
    found = []
    tag = re.match(r"^tag:", query)
    tag_text = query.lower().replace(" ", "").replace("tag:", "")

    for root, subfolder, files in os.walk(cfg.wiki_directory):
        for item in files:
            path = os.path.join(root, item)
            if os.path.join(cfg.wiki_directory, '.git') in str(path):
                # We don't want to search there
                continue
            if os.path.join(cfg.wiki_directory, cfg.images_route) in str(path):
                # Nothing interesting there too
                continue
                
            try:
                with open(root + '/' + item, encoding="utf8", errors='ignore') as f:
                    fin = f.read()  
                    fin_tags = fin.partition('\n')[0].lower().replace("tags: ", "").replace(",", "")
                    
                    if tag and re.search(tag_text, fin_tags, re.IGNORECASE):
                        found.append(get_info_from_item(item, root))
                    elif (re.search(escaped_search_term, root + '/' + item, re.IGNORECASE) or
                            re.search(escaped_search_term, fin, re.IGNORECASE) is not None):
                        found.append(get_info_from_item(item, root))
            except Exception as e:
                logger.error(f"Error while searching >>> {str(e)}")

    return found

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

def create_note(title: str, content: str) -> Dict[str, Any]:
    """
    Create a new note in the wiki with a title and markdown content
    
    Args:
        title: The title of the note (will be used as filename)
        content: The markdown content of the note
        
    Returns:
        A dictionary with information about the created note
    """
    logger.info(f"Agent creating note: {title}")
    
    # Clean the title to make a valid filename
    page_name = title.strip().replace(' ', '_')
    if page_name[-4:] == "{id}":
        page_name = f"{page_name[:-4]}{uuid.uuid4().hex}"
    
    try:
        filename = os.path.join(cfg.wiki_directory, page_name + '.md')
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
            
        with open(filename, 'w') as f:
            f.write(content)
            
        url = f"/{page_name}"
        return {
            "success": True,
            "title": title,
            "url": url,
            "message": f"Successfully created note '{title}'"
        }
    except Exception as e:
        logger.error(f"Error while creating note >>> {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create note '{title}'"
        }

# Define the OpenAI Agent tools
@function_tool
def search_notes(query: str) -> List[Dict[str, Any]]:
    """
    Search for notes in the wiki that match the query
    
    Args:
        query: The search query string
        
    Returns:
        A list of dictionaries containing information about matching notes
    """
    logger.info(f"Agent searching for: {query}")
    
    escaped_search_term = re.escape(query)
    found = []
    tag = re.match(r"^tag:", query)
    tag_text = query.lower().replace(" ", "").replace("tag:", "")

    for root, subfolder, files in os.walk(cfg.wiki_directory):
        for item in files:
            path = os.path.join(root, item)
            if os.path.join(cfg.wiki_directory, '.git') in str(path):
                # We don't want to search there
                continue
            if os.path.join(cfg.wiki_directory, cfg.images_route) in str(path):
                # Nothing interesting there too
                continue
                
            try:
                with open(root + '/' + item, encoding="utf8", errors='ignore') as f:
                    fin = f.read()  
                    fin_tags = fin.partition('\n')[0].lower().replace("tags: ", "").replace(",", "")
                    
                    if tag and re.search(tag_text, fin_tags, re.IGNORECASE):
                        found.append(get_info_from_item(item, root))
                    elif (re.search(escaped_search_term, root + '/' + item, re.IGNORECASE) or
                            re.search(escaped_search_term, fin, re.IGNORECASE) is not None):
                        found.append(get_info_from_item(item, root))
            except Exception as e:
                logger.error(f"Error while searching >>> {str(e)}")

    return found

@function_tool
def create_note(title: str, content: str) -> Dict[str, Any]:
    """
    Create a new note in the wiki with a title and markdown content
    
    Args:
        title: The title of the note (will be used as filename)
        content: The markdown content of the note
        
    Returns:
        A dictionary with information about the created note
    """
    logger.info(f"Agent creating note: {title}")
    
    # Clean the title to make a valid filename
    page_name = title.strip().replace(' ', '_')
    if page_name[-4:] == "{id}":
        page_name = f"{page_name[:-4]}{uuid.uuid4().hex}"
    
    try:
        filename = os.path.join(cfg.wiki_directory, page_name + '.md')
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
            
        with open(filename, 'w') as f:
            f.write(content)
            
        url = f"/{page_name}"
        return {
            "success": True,
            "title": title,
            "url": url,
            "message": f"Successfully created note '{title}'"
        }
    except Exception as e:
        logger.error(f"Error while creating note >>> {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to create note '{title}'"
        } 