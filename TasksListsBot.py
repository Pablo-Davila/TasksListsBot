
import asyncio
import json
from sys import argv, platform

from telebot import asyncio_filters, types
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.asyncio_storage import StateMemoryStorage


class UserStates(StatesGroup):
    select_list = State()
    addAll_tasks = State()
    doneAll_tasks_numbers = State()
    delAll_tasks_numbers = State()


bot = AsyncTeleBot(argv[1], state_storage=StateMemoryStorage())
bot.send_async_message = lambda *x, **y: (
    asyncio.create_task(bot.send_message(*x, **y))
)
bot.add_custom_filter(asyncio_filters.StateFilter(bot))

# Determine data path and adapt it to the host OS
path_data = argv[2] if len(argv) > 2 else "data/"
if not path_data.endswith('/'):
    path_data += '/'

if platform == "win32":
    path_data = path_data.replace("/", "\\")

help_eng = {
    'lists': "Display the curret set of lists.",
    'addList ListName': "Create a new empty list.",
    'delList ListName': "Remove an existing list.",
    'advanced': "Display advanced commands."
}

help_spa = {
    'lists': "Mostrar el conjunto de listas actual.",
    'addList NombreLista': "Crear una nueva lista vacía.",
    'delList ListName': "Eliminar una lista existente.",
    'advanced': "Mostrar comandos avanzados."
}

advanced_eng = {
    'show ListName': "Display the tasks of a single list.",
    'add ListName,TaskName': "Add a task to the list.",
    'addAll ListName': "Add multiple tasks (one per line).",
    'del ListName,TaskNumber': "Remove a task from a list.",
    'delAll ListName,3,1,4': "Remove multiple tasks from a list.",
    'done ListName,TaskNumber': "Mark a task as done.",
    'empty ListName': "Remove all the tasks in a given list.",
    'news': "Displays the bot's most recent news",
    'github': "Displays a link to the bot's source code"
}

advanced_spa = {
    'show ListName': "Mostrar las tareas de una única lista.",
    'add NombreLista,NombreTarea': "Añadir una tarea a la lista.",
    'addAll NombreLista': "Añadir multiples tareas (cada una en una línea).",
    'del NombreLista,NumeroTarea': "Eliminar una tarea de una lista.",
    'delAll NombreLista,3,1,4': "Eliminar multiples tareas de una lista.",
    'done NombreLista,NumeroTarea': "Marcar una tarea como hecha.",
    'empty NombreLista': "Eliminar todas las tareas de una lista.",
    'news': "Muestra las últimas novedades del bot",
    'github': "Muestra un link al código fuente del bot."
}

news = [
    "2020/08/07 Solución de pequeños bugs.",
    "2020/08/06 A partir de hoy el bot estará disponible 24/7 (en principio).",
    "2020/07/12 Nuevos botones para añadir, eliminar y marcar tareas como hechas.",
    "2020/07/10 Añadidos los comandos /empty y /delAll.",
    "2020/06/23 Mayor tolerancia a errores de sintaxis en los comandos.",
    "2020/06/23 Añadida una lista de novedades.",
    "2020/06/23 Resistencia a errores: A partir de ahora el bot se reinicia en caso de error, evitando así que deje de funcionar.",
    "Añadido el comando /addAll, que permite añadir múltiples tareas a una lista, con un único comando.",
    "A partir de ahora se toleran errores comunes en las máyúsculas y minúsculas de los comandos.",
    "2020/06/18: Bot creado!",
]


# Helper functions

def toSentence(s):
    '''Transfrom string into a correctly formatted sentence.'''

    return str(s).strip().capitalize()


def commandRegex(command):
    '''Provide command regex.'''

    return f"^/{command}( |$|@)(?i)"


def getLists(cid):
    '''Returns the lists dictionary of the specified chat.'''

    dic = None
    try:
        with open(path_data + f"lists_{cid}.json", "r") as f:
            dic = json.loads(f.read())
    except:
        dic = {}
    return dic


def writeLists(cid, dic):
    '''Write lists dictionary to file.'''

    with open(path_data + f"lists_{cid}.json", "w") as f:
        f.write(json.dumps(dic))


async def showList(cid, listName):
    '''Display requested list to in certain chat.'''

    dic = getLists(cid)

    if(listName in dic.keys()):
        ls = dic[listName]
        res = listName + ":"
        for i in range(len(ls)):
            task = ls[i]
            res += f"\n {i}. {task}"
        if(len(ls) == 0):
            res += "\n(Esta lista está vacía)"

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                "➕", callback_data=f"addall#{listName}"
            ),
            types.InlineKeyboardButton(
                "✅", callback_data=f"doneall#{listName}"
            ),
            types.InlineKeyboardButton(
                "🗑️", callback_data=f"delall#{listName}"
            ))
        bot.send_async_message(cid, res, reply_markup=keyboard)

    elif listName == "":
        bot.send_async_message(cid, "Debe indicar una lista.")

    else:
        bot.send_async_message(
            cid,
            f"La lista {listName} no existe."
        )


async def deleteTask(cid, listName, taskNumber):
    '''Remove task from list.'''

    dic = getLists(cid)

    num = None
    try:
        num = int(taskNumber)
    except:
        bot.send_async_message(
            cid,
            "No ha indicado un número de tarea válido."
        )
        return

    if listName in dic.keys():
        ls = dic[listName]
        try:
            taskName = ls.pop(num)
            writeLists(cid, dic)
            bot.send_async_message(
                cid,
                f"La tarea \"{taskName}\" ha sido eliminada."
            )
        except:
            bot.send_async_message(
                cid,
                f"Índice fuera de rango: {num}."
            )
    else:
        bot.send_async_message(
            cid,
            f"La lista {listName} no existe."
        )


async def doneTask(cid, listName, taskNumber):
    '''Set a task as done.'''

    dic = getLists(cid)

    if listName in dic.keys():
        try:
            taskNumber = int(taskNumber)
            try:
                ls = dic[listName]
                taskName = ls.pop(taskNumber)
                if "Hechas" in dic.keys():
                    dic["Hechas"].append(taskName)
                else:
                    dic["Hechas"] = [taskName]
                writeLists(cid, dic)
                bot.send_async_message(
                    cid,
                    f"Tarea \"{taskName}\" marcada como hecha."
                )
            except IndexError:
                bot.send_async_message(
                    cid,
                    "Índice fuera de rango."
                )
            except Exception as e:
                bot.send_async_message(cid, "ERROR")
                print(e)
        except:
            bot.send_async_message(
                cid,
                "Debe indicar el índice en la lista de la tarea hecha."
            )
    else:
        await bot.send_message(cid, f"La lista {listName} no existe.")


async def addAll(cid, listName, tasks):
    '''Add one or more tasks to a list.'''

    dic = getLists(cid)
    if listName in dic.keys():
        ls = dic[listName]
        c = 0
        for taskName in tasks:
            taskName = toSentence(taskName)
            if(len(taskName) >= 3):
                ls.append(taskName)
                c += 1
        writeLists(cid, dic)
        bot.send_async_message(
            cid,
            f"Se han añadido {c} tareas a la lista \"{listName}\"."
        )
    else:
        bot.send_async_message(
            cid,
            f"La lista {listName} no existe."
        )


async def delAll(cid, listName, indices):
    '''Remove one or more tasks from a list.'''

    indices = sorted([int(i.strip()) for i in indices], reverse=True)
    for i in indices:
        await deleteTask(cid, listName, i)


async def doneAll(cid, listName, indices):
    '''Set one or more tasks as done.'''

    indices = sorted([int(i.strip()) for i in indices], reverse=True)
    for i in indices:
        await doneTask(cid, listName, i)


# Command handlers

@bot.message_handler(regexp=commandRegex("start"))
async def command_start(message):
    '''start command: Send welcome message.'''

    user = message.from_user
    cid = message.chat.id

    ans = f"Hola{' ' + user.first_name if user.first_name else ''}{' ' + user.last_name if user.last_name else ''}. " \
        "Encantado de conocerle!\nEscriba /help para acceder a la lista de comandos básicos."

    bot.send_async_message(cid, ans)


@bot.message_handler(regexp=commandRegex("help"))
async def command_help(message):
    '''help command: Display basic commands.'''

    cid = message.chat.id

    help = "Estos son los comandos básicos:"
    for c in help_spa:
        help += f"\n*/{c}*: {help_spa[c]}"

    bot.send_async_message(cid, help, parse_mode='Markdown')


@bot.message_handler(regexp=commandRegex("advanced"))
async def command_advanced(message):
    '''advanced command: Display advanced commands.'''

    cid = message.chat.id

    help = "Estos son los comandos avanzados:"
    for c in advanced_spa:
        help += f"\n*/{c}*: {advanced_spa[c]}"

    bot.send_async_message(cid, help, parse_mode='Markdown')


@bot.message_handler(regexp=commandRegex("new(s)?"))
async def command_news(message):
    '''news command: Display the most recent development news of the bot.'''

    cid = message.chat.id

    text = "*Estas son las últimas novedades:*"
    for new in news:
        text += "\n - " + new

    bot.send_async_message(cid, text, parse_mode='Markdown')


@bot.message_handler(regexp=commandRegex("list(s)?"))
async def command_lists(message):
    '''
    lists command: Display the lists available in this chat and the number of
    elements in each of them.
    '''

    cid = message.chat.id
    uid = message.from_user.id
    dic = getLists(cid)

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True)
    if(dic == {}):
        bot.send_async_message(
            cid, "Aún no se ha creado ninguna lista."
        )
    else:
        c = 0
        fila = ["", "", ""]
        for l in dic.keys():
            fila[c] = f"{l} #{len(dic[l])}"

            if(c == 2):
                c = 0
                markup.row(fila[0], fila[1], fila[2])
            else:
                c += 1
        if(c == 1):
            markup.row(fila[0])
        elif(c == 2):
            markup.row(fila[0], fila[1])

        await bot.set_state(uid, UserStates.select_list, cid)
        await bot.send_message(cid, "Elija una lista", reply_markup=markup)


@bot.message_handler(regexp=commandRegex("addList"))
async def command_addList(message):
    '''addList command: Create a new list with the specified name.'''

    cid = message.chat.id
    listName = toSentence(message.text[9:])

    if(len(listName) >= 3):
        dic = getLists(cid)

        dic[listName] = []
        writeLists(cid, dic)

        bot.send_async_message(
            cid,
            f"Se ha creado la lista \"{listName}\"."
        )

    else:
        bot.send_async_message(
            cid,
            "El nombre de la lista debe tener al menos 3 caracteres."
        )


@bot.message_handler(regexp=commandRegex("add"))
async def command_add(message):
    '''add command: Add a single task to a list.'''

    cid = message.chat.id

    partes = message.text.split(',')
    if(len(partes) < 2):
        bot.send_async_message(
            cid,
            "Debe indicar el nombre de la lista y el de la tarea "
            "separados por una coma. Ejemplo: /add Lista1, Tarea1"
        )
    else:
        listName = toSentence(partes[0][5:])
        taskName = toSentence(partes[1])
        dic = getLists(cid)

        if(len(taskName) < 3):
            bot.send_async_message(
                cid,
                "El nombre de la tarea debe tener al menos 3 caracteres."
            )
        elif(not listName in dic.keys()):
            bot.send_async_message(
                cid,
                f"La lista {listName} no existe."
            )
        else:
            ls = dic[listName]
            ls.append(taskName)
            writeLists(cid, dic)
            bot.send_async_message(
                cid,
                f"Se ha añadido \"{taskName}\" a la lista \"{listName}\"."
            )


@bot.message_handler(regexp=commandRegex("addAll"))
async def command_addAll(message):
    '''addAll command: Add multiple tasks to the specified list.'''

    cid = message.chat.id

    partes = message.text.split('\n')
    if(len(partes) < 2):
        bot.send_async_message(
            cid,
            "Debe indicar el nombre de la lista y escribir una línea"
            "por cada nueva tarea separados por una coma. Ejemplo:\n"
            "```\n"
            "/addAll Lista1\n"
            "Tarea1\n"
            "Tarea2\n"
            "```",
            parse_mode="markdown"
        )
    else:
        listName = toSentence(partes[0][8:])
        tasks = partes[1:]
        asyncio.create_task(addAll(cid, listName, tasks))


@bot.message_handler(regexp=commandRegex("show"))
async def command_show(message):
    '''show command: Display all the tasks in the specified list.'''

    cid = message.chat.id

    listName = toSentence(message.text[6:])
    asyncio.create_task(showList(cid, listName))


@bot.message_handler(regexp=commandRegex("delList"))
async def command_delList(message):
    '''delList command: Remove a list and all of its tasks.'''

    cid = message.chat.id
    dic = getLists(cid)

    listName = toSentence(message.text[9:])
    if listName in dic.keys():
        dic.pop(listName)
        writeLists(cid, dic)
        bot.send_async_message(
            cid,
            f"La lista {listName} ha sido eliminada."
        )
    elif listName == "":
        bot.send_async_message(
            cid,
            "Debe indicar la lista que eliminar."
        )
    else:
        bot.send_async_message(
            cid,
            f"La lista {listName} no existe."
        )


@bot.message_handler(regexp=commandRegex("del"))
async def command_del(message):
    '''del command: Remove a single task Elimina una única tarea de la lista especificada.'''

    cid = message.chat.id
    dic = getLists(cid)

    partes = message.text.split(',')
    if(len(partes) < 2):
        bot.send_async_message(
            cid,
            "Debe indicar el nombre de la lista y el número de la tarea "
            "separados por una coma. Ejemplo: /del Lista1, 0"
        )
    else:
        listName = toSentence(partes[0][5:])
        asyncio.create_task(deleteTask(cid, listName, partes[1]))


@bot.message_handler(regexp=commandRegex("delAll"))
async def command_delAll(message):
    '''dellAll command: Remove a single task from the specified list.'''

    cid = message.chat.id

    partes = message.text.split(',')
    if(len(partes) < 2):
        bot.send_async_message(
            cid,
            "Debe indicar el nombre de la lista y el número de la tarea "
            "separados por una coma. Ejemplo: /del Lista1, 0"
        )
    else:
        listName = toSentence(partes[0][7:])
        delAll(cid, listName, partes[1:])


@bot.message_handler(regexp=commandRegex("(empty|clear)"))
async def command_empty(message):
    '''empty command: Clear all the tasks from the specified list.'''

    cid = message.chat.id
    dic = getLists(cid)

    listName = toSentence(message.text[6:])
    if listName in dic.keys():
        size = len(dic[listName])
        dic[listName] = []
        writeLists(cid, dic)
        bot.send_async_message(
            cid,
            f"Se han eliminado {size} tareas de la lista \"{listName}\"."
        )
    elif listName == "":
        bot.send_async_message(
            cid,
            "Debe indicar la lista que vaciar."
        )
    else:
        bot.send_async_message(
            cid,
            f"La lista {listName} no existe."
        )


@bot.message_handler(regexp=commandRegex("done"))
async def command_done(message):
    '''done command: Set a single task as done.'''

    cid = message.chat.id

    partes = message.text.split(',')
    if(len(partes) < 2):
        bot.send_async_message(
            cid,
            "Debe indicar el nombre de la lista y el número de la tarea "
            "separados por una coma. Ejemplo: /done Lista1, 0"
        )
    else:
        listName = toSentence(partes[0][6:])
        taskNumber = None
        try:
            taskNumber = int(partes[1])
        except:
            bot.send_async_message(
                cid,
                "No ha indicado un número de tarea válido."
            )
            return
        doneTask(cid, listName, taskNumber)


@bot.message_handler(commands=["git", "github", "source", "src"])
async def command_github(message):
    '''github command: Display a link to this bot's code repository.'''

    cid = message.chat.id

    bot.send_async_message(
        cid,
        "Puedes encontrar el código fuente de este bot en "
        "[GitHub](https://github.com/Pablo-Davila/TasksListsBot)",
        parse_mode='Markdown'
    )


@bot.message_handler(regexp=commandRegex("id"))
async def command_id(message):
    '''id command: Display current chat's id.'''

    cid = message.chat.id
    bot.send_async_message(cid, f"El id de su chat es {cid}")


@bot.callback_query_handler(func=lambda call: True)
async def handle_call(call):
    '''General callback query handler.'''

    cid = call.message.chat.id
    uid = call.from_user.id
    data = call.data.split('#')
    func = data[0]

    markup = types.ForceReply()

    if func == "addall":
        listName = data[1]
        asyncio.create_task(bot.answer_callback_query(call.id, "Success"))

        await bot.set_state(uid, UserStates.addAll_tasks, cid)
        asyncio.create_task(bot.add_data(uid, cid, select_list=listName))

        bot.send_async_message(
            cid,
            "Escriba en líneas separadas todas las tareas que desee añadir.",
            reply_markup=markup
        )

    elif func == "doneall":
        listName = data[1]
        asyncio.create_task(bot.answer_callback_query(call.id, "Success"))

        await bot.set_state(uid, UserStates.doneAll_tasks_numbers, cid)
        asyncio.create_task(bot.add_data(uid, cid, select_list=listName))

        bot.send_async_message(
            cid,
            "Escriba los números de las tareas hechas separados por espacios.",
            reply_markup=markup
        )

    elif func == "delall":
        listName = data[1]
        asyncio.create_task(bot.answer_callback_query(call.id, "Success"))

        await bot.set_state(uid, UserStates.delAll_tasks_numbers, cid)
        asyncio.create_task(bot.add_data(uid, cid, select_list=listName))

        bot.send_async_message(
            cid,
            "Escriba los números de las tareas que borrar separados por espacios.",
            reply_markup=markup
        )

    else:
        print("Unknown callback query: " + call.data)


@bot.message_handler(state="*", commands='cancel')
async def command_cancel(message):
    '''Cancel state'''

    cid = message.chat.id

    await bot.send_message(cid, "Your state was cancelled.")
    await bot.delete_state(message.from_user.id, cid)


@bot.message_handler(state=UserStates.select_list)
async def select_list(message):
    cid = message.chat.id

    listName = message.text.split('#')[0][:-1]
    await showList(cid, listName)
    await bot.delete_state(message.from_user.id, cid)


@bot.message_handler(state=UserStates.addAll_tasks)
async def addAll_state(message):
    cid = message.chat.id
    uid = message.from_user.id

    async with bot.retrieve_data(uid, cid) as user_data:
        listName = user_data['select_list']
    await bot.delete_state(uid, cid)

    asyncio.create_task(addAll(
        cid,
        listName,
        message.text.split('\n')
    ))
    await bot.delete_state(uid, cid)


@bot.message_handler(state=UserStates.doneAll_tasks_numbers)
async def doneAll_state(message):
    cid = message.chat.id
    uid = message.from_user.id

    async with bot.retrieve_data(uid, cid) as user_data:
        listName = user_data['select_list']
    await bot.delete_state(uid, cid)

    asyncio.create_task(doneAll(
        cid,
        listName,
        message.text.split(' ')
    ))
    await bot.delete_state(uid, cid)


@bot.message_handler(state=UserStates.delAll_tasks_numbers)
async def delAll_state(message):
    cid = message.chat.id
    uid = message.from_user.id

    async with bot.retrieve_data(uid, cid) as user_data:
        listName = user_data['select_list']
    await bot.delete_state(uid, cid)

    asyncio.create_task(delAll(
        cid,
        listName,
        message.text.split(' ')
    ))


if __name__ == "__main__":
    print("\nRunning TasksListsBot.py")
    asyncio.run(bot.polling())
