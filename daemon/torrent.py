#encoding: utf-8
#解析种子文件的基本函数(torrent.py)
from time import time

def torrentinfo(torrentcontent):
    metadata = torrentcontent["info"]
    info = {
        "name": getname(metadata),
        "length": calclength(metadata),
        "timestamp": getcreatedate(torrentcontent),
        "files": extrafiles(metadata)
    }
    return info

def calclength(metadata):
    length = 0
    try:
        length = metadata["length"]
    except KeyError:
        try:
            for file in metadata["files"]:
                length += file["length"]
        except KeyError:
            pass
    return length

def extrafiles(metadata):
    files = []
    try:
        for file in metadata["files"]:
            path = file["path"]
            if len(path) > 1:
                main = path[0]
                for f in path[1:]:
                    files.append("%s/%s" % (main, f))
            else:
                files.append( path[0] )
        if files:
            return '\r\n'.join(files)
        else:
            return getname(metadata)
    except KeyError:
        return getname(metadata)

def getname(metadata):
    try:
        name = metadata["name"]
        if name.strip() == "": raise KeyError
    except KeyError:
        name = getmaxfile(metadata)

    return name

def getmaxfile(metadata):
    try:
        maxfile = metadata["files"][0]
        for file in metadata["files"]:
            if file["length"] > maxfile["length"]:
                maxfile = file
        name = maxfile["path"][0]
        return name
    except KeyError:
        return ""

def getcreatedate(torrentcontent):
    try:
        timestamp = torrentcontent["creation date"]
    except KeyError:
        timestamp = int( time() )
    return timestamp