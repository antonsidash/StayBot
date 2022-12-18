import json
from requests import get
from aiogram import Bot, Dispatcher, executor, types
import requests as req
import sqlite3
from mcrcon import MCRcon
import datetime

RCON = MCRcon("", "", )

API_TOKEN = ''

bot = Bot(token = API_TOKEN)
dp = Dispatcher(bot)

db_connect = sqlite3.connect(r'C:\Users\Anton\Downloads\Django\StayBot\StayConsole.db')
db_cursor = db_connect.cursor()


def InsertLog(user_id, log):
    db_cursor.execute("SELECT NICKNAME FROM USERS WHERE ID = {0}".format(int(user_id)))
    userName = db_cursor.fetchone()
    userName = str(str(userName)[2:len(str(userName)) - 3])
    print(userName)
    if (userName == None):
        print("[Logs]: Имя пользователя с ID {0} не найдено!".format(user_id))
        return

    db_insert = """INSERT INTO LOGS
                (Time, UserID, UserName, Log)
                VALUES 
                ('{0}', {1}, '{2}', '{3}');""".format(str(datetime.datetime.now()), user_id, userName, log)
    db_cursor.execute(db_insert)
    db_connect.commit()


def  isAdmin(user_id):
    db_cursor.execute("SELECT ID FROM USERS")
    all_users = db_cursor.fetchall()
    all_users = list(all_users)
    for i in range(len(all_users)):
        all_users[i] = int(str(all_users[i])[1:len(str(i)) - 3])
    if (all_users.__contains__(user_id)):
        return True
    else:
        return False

def getUserAccessLvl(user_id):
    db_cursor.execute("SELECT AccessLvl FROM USERS WHERE ID = '{0}'".format(user_id))
    userAccessLvl = db_cursor.fetchone()
    return int(str(userAccessLvl)[1:len(str(userAccessLvl)) - 2])

def getCommandAccessLvl(command):
    db_cursor.execute("SELECT AccessLvl FROM COMMANDS WHERE Command = '{0}'".format(command))
    commandAccessLvl = db_cursor.fetchone()
    print(str(commandAccessLvl)[1:len(str(commandAccessLvl)) - 2])
    return int(str(commandAccessLvl)[1:len(str(commandAccessLvl)) - 2])

@dp.message_handler(commands=['start'])

async def send_welcome(message: types.Message):
    db_cursor.execute("SELECT ID FROM USERS")
    all_users = db_cursor.fetchall()
    all_users = list(all_users)
    for i in range(len(all_users)):
        all_users[i] = int(str(all_users[i])[1:len(str(i)) - 3])
    print(all_users)
    if (all_users.__contains__(message.from_user.id)):
        await message.answer("Здравствуйте, {0}! \nЧто вы хотите сделать?".format(message.from_user.username))
    else:
        await message.answer("У Вас пока нет доступа! \nЧтобы его получить, сообщите администрации свой ID: {0}".format(message.from_user.id))


@dp.message_handler(commands=['help'])

async def send_welcome(message: types.Message):
    db_cursor.execute("SELECT ID FROM USERS WHERE ID = {0}".format(message.from_user.id))
    if (db_cursor.fetchone() == None):
        await message.answer("У Вас пока нет доступа! \nЧтобы его получить, сообщите администрации свой ID: {0}".format(message.from_user.id))
        return
    # Стандартные команды:
    mess = "Команды: \n"
    db_cursor.execute("SELECT * FROM COMMANDS")
    commandslist = db_cursor.fetchall()
    print(commandslist)
    for x in (commandslist):
        mess += "{0} | {1} \n".format(str(x[0]), str(x[1]))

    # Админские команды:
    db_cursor.execute("SELECT ID FROM ADMINS WHERE ID = {0}".format(message.from_user.id))
    if (db_cursor.fetchone() != None):
        mess += """\n\nАдминские команды: \n
/adduser <ID NICKNAME AccessLvl> \n
/deluser <ID> \n
/addcommand <Command AccessLvl> \n
/delcommand <Command> \n
/addadmin <ID NICKNAME AdminAccessLvl> \n
/deladmin <ID>"""

    await message.answer(mess)



@dp.message_handler(commands=['addcommand'])

async def send_info(message):
    db_cursor.execute("SELECT Command FROM COMMANDS")
    commandslist = db_cursor.fetchall()
    if (len(message.text.split(" ")) != 3):
        await message.answer("Неверное количество аргументов!")
        return
    for i in range(len(commandslist)):
        commandslist[i] = str(str(commandslist[i])[2:len(str(commandslist[i])) - 3])

    if (commandslist.__contains__(message.text.split(" ")[1])):
        await message.reply("Такая команда уже существует!")
        return
    
    try:
        AccessLvl = int(message.text.split(" ")[2])
    except:
        await message.answer("Формат аргументов некорректен!")
        return
    
    db_insert = """INSERT INTO COMMANDS
                (Command, AccessLvl)
                VALUES 
                ('{0}', {1});""".format(message.text.split(" ")[1], AccessLvl)
    db_cursor.execute(db_insert)
    db_connect.commit()

    await message.reply("Команда {0} с уровнем доступа {1} была успешно добавлена в Бота!".format(message.text.split(" ")[1], AccessLvl))
    InsertLog(message.from_user.id, "Команда {0} с уровнем доступа {1} была успешно добавлена в Бота!".format(message.text.split(" ")[1], AccessLvl))

@dp.message_handler(commands=['delcommand'])

async def send_info(message):
    db_cursor.execute("SELECT Command FROM COMMANDS")
    commandslist = db_cursor.fetchall()
    if (len(message.text.split(" ")) != 2):
        await message.answer("Неверное количество аргументов!")
        return

    for i in range(len(commandslist)):
        commandslist[i] = str(str(commandslist[i])[2:len(str(commandslist[i])) - 3])
        
    print(commandslist[5])
    print(message.text.split(" ")[1])

    if (not commandslist.__contains__(message.text.split(" ")[1])):
        await message.reply("Такой команды не существует!")
        return
    
    db_delete = """DELETE FROM COMMANDS WHERE Command = '{0}'""".format(message.text.split(" ")[1])
    db_cursor.execute(db_delete)
    db_connect.commit()

    await message.reply("Команда {0} была успешно удалена!".format(message.text.split(" ")[1]))
    InsertLog(message.from_user.id, "Команда {0} была успешно удалена!".format(message.text.split(" ")[1]))

        
@dp.message_handler(commands=['adduser'])

async def send_info(message):
    print(message.text)
    db_cursor.execute("SELECT ID FROM ADMINS")
    adminslist = db_cursor.fetchall()
    adminslist = list(adminslist)
    for i in range(len(adminslist)):
        adminslist[i] = int(str(adminslist[i])[1:len(str(i)) - 3])
    if (not adminslist.__contains__(message.from_user.id)):
        await message.answer("У Вас не хватает прав для выполнения этой команды!")
        return
    
    if (len(message.text.split(" ")) != 4):
        await message.answer("Неверное количество аргументов!")
        return

    (newUserId, nickName, AccessLvl) = message.text.split(" ")[1:]
    print(newUserId, nickName, AccessLvl)
    try:
        newUserId = int(newUserId)
        AccessLvl = int(AccessLvl)
    except:
        await message.answer("Формат аргументов некорректен!")
        return

    db_cursor.execute("SELECT ID FROM USERS WHERE ID = {0}".format(newUserId))
    findusers = db_cursor.fetchone()
    if (findusers != None):
        await message.answer("Пользователь с ID {0} уже существует!".format(newUserId))
        return

    db_cursor.execute("SELECT ID FROM WHITELIST")
    whitelisted_ids = db_cursor.fetchall()
    for i in range(len(whitelisted_ids)):
        whitelisted_ids[i] = int(str(whitelisted_ids[i])[1:len(str(i)) - 3])
    print(whitelisted_ids)
    if (whitelisted_ids.__contains__(newUserId)):
        await message.answer("Вы не можете проводить манипуляции с ID {0}!".format(newUserId))
        return
    
    db_insert = """INSERT INTO USERS
                (ID, NICKNAME, AccessLvl)
                VALUES 
                ({0}, '{1}', {2});""".format(newUserId, nickName, AccessLvl)
    db_cursor.execute(db_insert)
    db_connect.commit()
    await message.answer("Пользователь {0} (ID: {1}) успешно добавлен в систему!".format(nickName, newUserId))
    InsertLog(message.from_user.id, "Пользователь {0} (ID: {1}) успешно добавлен в систему!".format(nickName, newUserId))

@dp.message_handler(commands=['deluser'])

async def send_info(message):
    print(message.text)
    db_cursor.execute("SELECT ID FROM ADMINS")
    adminslist = db_cursor.fetchall()
    adminslist = list(adminslist)
    for i in range(len(adminslist)):
        adminslist[i] = int(str(adminslist[i])[1:len(str(i)) - 3])
    if (not adminslist.__contains__(message.from_user.id)):
        await message.answer("У Вас не хватает прав для выполнения этой команды!")
        return
    
    if (len(message.text.split(" ")) != 2):
        await message.answer("Неверное количество аргументов!")
        return

    delUserId = message.text.split(" ")[1]
    try:
        delUserId = int(delUserId)
    except:
        await message.answer("Вы ввели ID неверного формата!")
        return

    db_cursor.execute("SELECT ID FROM USERS WHERE ID = {0}".format(delUserId))
    findusers = db_cursor.fetchone()
    if (findusers == None):
        await message.answer("Пользователя с ID {0} не существует!".format(delUserId))
        return

    db_cursor.execute("SELECT ID FROM WHITELIST")
    whitelisted_ids = db_cursor.fetchall()
    for i in range(len(whitelisted_ids)):
        whitelisted_ids[i] = int(str(whitelisted_ids[i])[1:len(str(i)) - 3])
    print(whitelisted_ids)
    if (whitelisted_ids.__contains__(delUserId)):
        await message.answer("Вы не можете проводить манипуляции с ID {0}!".format(delUserId))
        return

    db_delete = """DELETE FROM USERS WHERE ID = {0}""".format(delUserId)
    db_cursor.execute(db_delete)
    db_connect.commit()
    await message.answer("Пользователь с ID: {0} успешно удален из системы!".format(delUserId))
    InsertLog(message.from_user.id, "Пользователь с ID: {0} успешно удален из системы!".format(delUserId))

@dp.message_handler(commands=['addadmin'])

async def send_info(message):
    print(message.text)
    db_cursor.execute("SELECT ID FROM ADMINS")
    adminslist = db_cursor.fetchall()
    adminslist = list(adminslist)
    for i in range(len(adminslist)):
        adminslist[i] = int(str(adminslist[i])[1:len(str(i)) - 3])
    if (not adminslist.__contains__(message.from_user.id)):
        await message.answer("У Вас не хватает прав для выполнения этой команды!")
        return
    
    if (len(message.text.split(" ")) != 4):
        await message.answer("Неверное количество аргументов!")
        return

    (newUserId, nickName, AccessLvl) = message.text.split(" ")[1:]
    print(newUserId, nickName, AccessLvl)
    try:
        newUserId = int(newUserId)
        AccessLvl = int(AccessLvl)
    except:
        await message.answer("Формат аргументов некорректен!")
        return

    db_cursor.execute("SELECT ID FROM ADMINS WHERE ID = {0}".format(newUserId))
    findusers = db_cursor.fetchone()
    if (findusers != None):
        await message.answer("ID {0} уже является админстратором!".format(newUserId))
        return

    db_cursor.execute("SELECT ID FROM WHITELIST")
    whitelisted_ids = db_cursor.fetchall()
    for i in range(len(whitelisted_ids)):
        whitelisted_ids[i] = int(str(whitelisted_ids[i])[1:len(str(i)) - 3])
    print(whitelisted_ids)
    if (whitelisted_ids.__contains__(newUserId)):
        await message.answer("Вы не можете проводить манипуляции с ID {0}!".format(newUserId))
        return
    
    db_insert = """INSERT INTO ADMINS
                (ID, NICKNAME, AdminAccessLvl)
                VALUES 
                ({0}, '{1}', {2});""".format(newUserId, nickName, AccessLvl)
    db_cursor.execute(db_insert)
    db_connect.commit()
    await message.answer("Пользователь {0} (ID: {1}) успешно назначен администратором!".format(nickName, newUserId))
    InsertLog(message.from_user.id, "Пользователь {0} (ID: {1}) успешно назначен администратором!".format(nickName, newUserId))

@dp.message_handler(commands=['deladmin'])

async def send_info(message):
    print(message.text)
    db_cursor.execute("SELECT ID FROM ADMINS")
    adminslist = db_cursor.fetchall()
    adminslist = list(adminslist)
    for i in range(len(adminslist)):
        adminslist[i] = int(str(adminslist[i])[1:len(str(i)) - 3])
    if (not adminslist.__contains__(message.from_user.id)):
        await message.answer("У Вас не хватает прав для выполнения этой команды!")
        return
    
    if (len(message.text.split(" ")) != 2):
        await message.answer("Неверное количество аргументов!")
        return

    delUserId = message.text.split(" ")[1]
    try:
        delUserId = int(delUserId)
    except:
        await message.answer("Вы ввели ID неверного формата!")
        return

    db_cursor.execute("SELECT ID FROM ADMINS WHERE ID = {0}".format(delUserId))
    findusers = db_cursor.fetchone()
    if (findusers == None):
        await message.answer("ID {0} не является администратором!".format(delUserId))
        return

    db_cursor.execute("SELECT ID FROM WHITELIST")
    whitelisted_ids = db_cursor.fetchall()
    for i in range(len(whitelisted_ids)):
        whitelisted_ids[i] = int(str(whitelisted_ids[i])[1:len(str(i)) - 3])
    print(whitelisted_ids)
    if (whitelisted_ids.__contains__(delUserId)):
        await message.answer("Вы не можете проводить манипуляции с ID {0}!".format(delUserId))
        return
    
    db_delete = """DELETE FROM ADMINS WHERE ID = {0}""".format(delUserId)
    db_cursor.execute(db_delete)
    db_connect.commit()
    await message.answer("Администратор с ID: {0} успешно разжалован!".format(delUserId))
    InsertLog(message.from_user.id, "Администратор с ID: {0} успешно разжалован!".format(delUserId))

@dp.message_handler()

async def echo(message: types.Message):
    if (not isAdmin(message.from_user.id)):
        await message.answer("У Вас пока нет доступа! \nЧтобы его получить, сообщите администрации свой ID: {0}".format(message.from_user.id))
        return

    # Вайтлист:
    db_cursor.execute("SELECT USERNAME FROM WHITELIST")
    whitelisted_users = db_cursor.fetchall()

    for i in range(len(whitelisted_users)):
        whitelisted_users[i] = str(whitelisted_users[i])[2:len(str(i)) - 4]
        print(whitelisted_users[i])
        
    message_arguments = message.text.split(" ")

    db_cursor.execute("SELECT Command FROM COMMANDS")
    listCommands = db_cursor.fetchall()
    listCommands = list(listCommands)
    for i in range(len(listCommands)):
        listCommands[i] = str(listCommands[i])[2:len(str(i)) - 4]

    if (listCommands.__contains__(str(message.text).split(" ")[0])):
        if (getCommandAccessLvl(str(message.text).split(" ")[0]) <= getUserAccessLvl(message.from_user.id)):
            for x in (message_arguments):
                if (whitelisted_users.__contains__(x)):
                    await message.answer("Вы не можете использовать в своём запросе имя {0}!".format(x))
                    return
            await message.reply("Команда успешно выполнена!")
            InsertLog(message.from_user.id, message.text)
            RCON.connect()
            RCON.command(message.text)
        else:
            await message.answer("У Вас недостаточный уровень привилегий для выполнения этой команды!")
            return
    else:
        await message.answer("Вами была введена неверная команда!")
    



if __name__ == '__main__':
    executor.start_polling(dp, skip_updates = True)
