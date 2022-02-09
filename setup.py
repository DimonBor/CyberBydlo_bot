import json

# Operations with users

def loadUsers():

    try:
        with open('users', 'r') as users:
            usersList = json.load(users)
    except FileNotFoundError:
        with open('users', 'w') as users:
            json.dump([], users)
        with open('users', 'r') as users:
            usersList = json.load(users)

    return usersList


def addUser(userID, groupName):

    usersList = loadUsers()
    
    for user in usersList:
        if user[0] == userID: return "ERROR"

    user = [userID, groupName]
    usersList.append(user)

    with open('users', 'w') as users:
        json.dump(usersList, users)

    return "OK"


def deleteUser(userID):

    usersList = loadUsers()

    for user in usersList:
        if user[0] == userID:
            usersList.remove(user)
            with open('users', 'w') as users:
                json.dump(usersList, users)
            return "OK"

    return "ERROR"


def setGroup(userID, groupName):

    usersList = loadUsers()

    for user in usersList:
        if int(user[0]) == userID:
            usersList[usersList.index(user)][1] = groupName
            with open('users', 'w') as users:
                json.dump(usersList, users)
            return "OK"

    return "ERROR"


# URLs for buttons


def loadURLs():

    try:
        with open('urls', 'r') as urls:
            urlsList = json.load(urls)
    except FileNotFoundError:
        with open('urls', 'w') as urls:
            json.dump({}, urls)
        with open('urls', 'r') as urls:
            urlsList = json.load(urls)

    return urlsList


def addUrl(groupCode, subjectName, action, urlToAppend):

    urlsList = loadURLs()

    try: urlsList[groupCode]
    except: urlsList[groupCode] = {}

    try: urlsList[groupCode][subjectName]
    except: urlsList[groupCode][subjectName] = {}

    urlsList[groupCode][subjectName][action] = urlToAppend

    with open('urls', 'w') as urls:
        json.dump(urlsList, urls)

    return "OK"

def deleteURL(groupCode, subjectName, action):

    urlsList = loadURLs()

    try:
        urlsList[groupCode][subjectName][action] = ""
    except: return "ERROR: NOT FOUND!"

    with open('urls', 'w') as urls:
        json.dump(urlsList, urls)

    return "OK"
