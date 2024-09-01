import asyncio
import json
import os

from telebot import asyncio_filters, types
from telebot.async_telebot import AsyncTeleBot
from telebot.asyncio_handler_backends import State, StatesGroup
from telebot.asyncio_storage import StateMemoryStorage

DATA_PATH = "/data"

HELP_ENG = {
    "lists": "Display the curret set of lists.",
    "addList ListName": "Create a new empty list.",
    "delList ListName": "Remove an existing list.",
    "advanced": "Display advanced commands.",
}

HELP_SPA = {
    "lists": "Mostrar el conjunto de listas actual.",
    "addList NombreLista": "Crear una nueva lista vacía.",
    "delList ListName": "Eliminar una lista existente.",
    "advanced": "Mostrar comandos avanzados.",
}

ADVANCED_ENG = {
    "show ListName": "Display the tasks of a single list.",
    "add ListName,TaskName": "Add a task to the list.",
    "addAll ListName": "Add multiple tasks (one per line).",
    "del ListName,TaskNumber": "Remove a task from a list.",
    "delAll ListName,3,1,4": "Remove multiple tasks from a list.",
    "done ListName,TaskNumber": "Mark a task as done.",
    "empty ListName": "Remove all the tasks in a given list.",
    "news": "Displays the bot's most recent news.",
    "github": "Displays a link to the bot's source code.",
}

ADVANCED_SPA = {
    "show ListName": "Mostrar las tareas de una única lista.",
    "add NombreLista,NombreTarea": "Añadir una tarea a la lista.",
    "addAll NombreLista": "Añadir multiples tareas (cada una en una línea).",
    "del NombreLista,NumeroTarea": "Eliminar una tarea de una lista.",
    "delAll NombreLista,3,1,4": "Eliminar multiples tareas de una lista.",
    "done NombreLista,NumeroTarea": "Marcar una tarea como hecha.",
    "empty NombreLista": "Eliminar todas las tareas de una lista.",
    "news": "Muestra las últimas novedades del bot",
    "github": "Muestra un link al código fuente del bot.",
}

NEWS = [
    "2022/09/10 Autoborrado de mensajes (al fin!)",
    "2020/08/07 Solución de pequeños bugs.",
    "2020/08/06 A partir de hoy el bot estará disponible 24/7 (en principio).",
    "2020/07/12 Nuevos botones para añadir, eliminar y marcar tareas como hechas.",
    "2020/07/10 Añadidos los comandos /empty y /delAll.",
    "2020/06/23 Mayor tolerancia a errores de sintaxis en los comandos.",
    "2020/06/23 Añadida una lista de novedades.",
    "2020/06/23 Resistencia a errores: A partir de ahora el bot se reinicia en caso de error, evitando así que deje de funcionar.",
    "2020/06/?? Añadido el comando /addAll, que permite añadir múltiples tareas a una lista, con un único comando.",
    "2020/06/?? A partir de ahora se toleran errores comunes en la sintaxis de los comandos.",
    "2020/06/18 Bot creado!",
]


class TasksListsBot(AsyncTeleBot):

    async def send_message(self, *args, delete_timeout: float = None, **kwargs):
        msg = await super().send_message(*args, **kwargs)
        cid = msg.chat.id
        mid = msg.id

        if delete_timeout is not None:
            await asyncio.sleep(delete_timeout)
            try:
                asyncio.create_task(self.delete_message(cid, mid))
            except:
                return

    def send_async_message(self, *args, **kwargs):
        asyncio.create_task(bot.send_message(*args, **kwargs))


class UserStates(StatesGroup):
    select_list = State()
    add_all_tasks = State()
    done_all_tasks_numbers = State()
    del_all_tasks_numbers = State()


token = os.getenv("BOT_TOKEN")
if token is None:
    print("Error: No token provided.")
    exit(1)

bot = TasksListsBot(token, state_storage=StateMemoryStorage())
bot.add_custom_filter(asyncio_filters.StateFilter(bot))


# Helper functions

def to_sentence(s):
    """Transfrom string into a correctly formatted sentence."""

    return str(s).strip().capitalize()


def command_regex(command):
    """Provide command regex."""

    return f"^/{command}( |$|@)(?i)"


def get_lists(cid):
    """Return the lists dictionary of the specified chat."""

    dic = None
    try:
        with open(DATA_PATH + f"lists_{cid}.json", "r") as f:
            dic = json.loads(f.read())
    except:
        dic = {}
    return dic


def write_lists(cid, dic):
    """Write lists dictionary to file."""

    with open(DATA_PATH + f"lists_{cid}.json", "w") as f:
        f.write(json.dumps(dic))


async def show_lists(cid, list_name):
    """Display requested list to in certain chat."""

    dic = get_lists(cid)

    if list_name in dic.keys():
        ls = dic[list_name]
        res = list_name + ":"
        for i in range(len(ls)):
            task = ls[i]
            res += f"\n {i}. {task}"
        if len(ls) == 0:
            res += "\n(Esta lista está vacía)"

        keyboard = types.InlineKeyboardMarkup()
        keyboard.add(
            types.InlineKeyboardButton(
                "➕", callback_data=f"addall#{list_name}"
            ),
            types.InlineKeyboardButton(
                "✅", callback_data=f"doneall#{list_name}"
            ),
            types.InlineKeyboardButton(
                "🗑️", callback_data=f"delall#{list_name}"
            ))
        bot.send_async_message(
            cid,
            res,
            reply_markup=keyboard,
            delete_timeout=300
        )

    elif list_name == "":
        bot.send_async_message(
            cid,
            "Debe indicar una lista.",
            delete_timeout=10
        )

    else:
        bot.send_async_message(
            cid,
            f"La lista {list_name} no existe.",
            delete_timeout=10
        )


async def delete_task(cid, list_name, task_number):
    """Remove task from list."""

    dic = get_lists(cid)

    num = None
    try:
        num = int(task_number)
    except:
        bot.send_async_message(
            cid,
            "No ha indicado un número de tarea válido.",
            delete_timeout=10
        )
        return

    if list_name in dic.keys():
        ls = dic[list_name]
        try:
            task_name = ls.pop(num)
            write_lists(cid, dic)
            bot.send_async_message(
                cid,
                f"La tarea \"{task_name}\" ha sido eliminada.",
                delete_timeout=10
            )
        except:
            bot.send_async_message(
                cid,
                f"Índice fuera de rango: {num}.",
                delete_timeout=10
            )
    else:
        bot.send_async_message(
            cid,
            f"La lista {list_name} no existe.",
            delete_timeout=10
        )


async def done_task(cid, list_name, task_number):
    """Set a task as done."""

    dic = get_lists(cid)

    if list_name in dic.keys():
        try:
            task_number = int(task_number)
            try:
                ls = dic[list_name]
                task_name = ls.pop(task_number)
                if "Hechas" in dic.keys():
                    dic["Hechas"].append(task_name)
                else:
                    dic["Hechas"] = [task_name]
                write_lists(cid, dic)
                bot.send_async_message(
                    cid,
                    f"Tarea \"{task_name}\" marcada como hecha.",
                    delete_timeout=10
                )
            except IndexError:
                bot.send_async_message(
                    cid,
                    "Índice fuera de rango.",
                    delete_timeout=10
                )
            except Exception as e:
                bot.send_async_message(cid, "ERROR", delete_timeout=10)
                print(e)
        except:
            bot.send_async_message(
                cid,
                "Debe indicar el índice en la lista de la tarea hecha.",
                delete_timeout=10
            )
    else:
        await bot.send_message(
            cid,
            f"La lista {list_name} no existe.",
            delete_timeout=10
        )


async def add_all(cid, list_name, tasks):
    """Add one or more tasks to a list."""

    dic = get_lists(cid)
    if list_name in dic.keys():
        ls = dic[list_name]
        c = 0
        for task_name in tasks:
            task_name = to_sentence(task_name)
            if len(task_name) >= 3:
                ls.append(task_name)
                c += 1
        write_lists(cid, dic)
        bot.send_async_message(
            cid,
            f"Se han añadido {c} tareas a la lista \"{list_name}\".",
            delete_timeout=10
        )
    else:
        bot.send_async_message(
            cid,
            f"La lista {list_name} no existe.",
            delete_timeout=10
        )


async def del_all(cid, list_name, indices):
    """Remove one or more tasks from a list."""

    indices = sorted([int(i.strip()) for i in indices], reverse=True)
    for i in indices:
        await delete_task(cid, list_name, i)


async def done_all(cid, list_name, indices):
    """Set one or more tasks as done."""

    indices = sorted([int(i.strip()) for i in indices], reverse=True)
    for i in indices:
        await done_task(cid, list_name, i)


# Command handlers

@bot.message_handler(regexp=command_regex("start"))
async def command_start(message):
    """start command: Send welcome message."""

    user = message.from_user
    cid = message.chat.id

    full_name = (" " + user.full_name) if user.full_name else ""
    ans = (
        f"Hola{full_name}. Encantado de conocerle!\n"
        "Escriba /help para acceder a la lista de comandos básicos."
    )
    bot.send_async_message(cid, ans)


@bot.message_handler(regexp=command_regex("help"))
async def command_help(message):
    """help command: Display basic commands."""

    cid = message.chat.id

    help = "Estos son los comandos básicos:"
    for c in HELP_SPA:
        help += f"\n*/{c}*: {HELP_SPA[c]}"

    bot.send_async_message(
        cid,
        help,
        parse_mode="Markdown",
        delete_timeout=300
    )


@bot.message_handler(regexp=command_regex("advanced"))
async def command_advanced(message):
    """advanced command: Display advanced commands."""

    cid = message.chat.id

    help = "Estos son los comandos avanzados:"
    for c in ADVANCED_SPA:
        help += f"\n*/{c}*: {ADVANCED_SPA[c]}"

    bot.send_async_message(
        cid,
        help,
        parse_mode="Markdown",
        delete_timeout=300
    )


@bot.message_handler(regexp=command_regex("new(s)?"))
async def command_news(message):
    """news command: Display the most recent development news of the bot."""

    cid = message.chat.id

    text = "*Estas son las últimas novedades:*"
    for new in NEWS:
        text += "\n - " + new

    bot.send_async_message(
        cid,
        text,
        parse_mode="Markdown",
        delete_timeout=300)


@bot.message_handler(regexp=command_regex("list(s)?"))
async def command_lists(message):
    """
    lists command: Display the lists available in this chat and the number of
    elements in each of them.
    """

    cid = message.chat.id
    uid = message.from_user.id
    dic = get_lists(cid)

    markup = types.ReplyKeyboardMarkup(one_time_keyboard=True, selective=True)
    if len(dic) == 0:
        bot.send_async_message(
            cid, "Aún no se ha creado ninguna lista.",
            delete_timeout=10
        )
    else:
        c = 0
        fila = ["", "", ""]
        for l in dic.keys():
            fila[c] = f"{l} #{len(dic[l])}"

            if c == 2:
                c = 0
                markup.row(fila[0], fila[1], fila[2])
            else:
                c += 1
        if c == 1:
            markup.row(fila[0])
        elif c == 2:
            markup.row(fila[0], fila[1])

        await bot.set_state(uid, UserStates.select_list, cid)
        await bot.reply_to(
            message,
            "Elija una lista",
            reply_markup=markup,
            delete_timeout=20
        )


@bot.message_handler(regexp=command_regex("addList"))
async def command_add_list(message):
    """addList command: Create a new list with the specified name."""

    cid = message.chat.id
    list_name = to_sentence(message.text[9:])

    if len(list_name) < 3:
        bot.send_async_message(
            cid,
            "El nombre de la lista debe tener al menos 3 caracteres.",
            delete_timeout=10
        )
        return

    dic = get_lists(cid)

    if list_name in dic:
        bot.send_async_message(
            cid,
            f"Ya existe una lista llamada \"{list_name}\".",
            delete_timeout=10
        )
        return

    dic[list_name] = []
    write_lists(cid, dic)

    bot.send_async_message(
        cid,
        f"Se ha creado la lista \"{list_name}\"."
    )


@bot.message_handler(regexp=command_regex("add"))
async def command_add(message):
    """add command: Add a single task to a list."""

    cid = message.chat.id

    partes = message.text.split(",")
    if len(partes) < 2:
        bot.send_async_message(
            cid,
            "Debe indicar el nombre de la lista y el de la tarea "
            "separados por una coma. Ejemplo: /add Lista1, Tarea1",
            delete_timeout=10
        )
    else:
        list_name = to_sentence(partes[0][5:])
        task_name = to_sentence(partes[1])
        dic = get_lists(cid)

        if len(task_name) < 3:
            bot.send_async_message(
                cid,
                "El nombre de la tarea debe tener al menos 3 caracteres.",
                delete_timeout=10
            )
        elif not list_name in dic.keys():
            bot.send_async_message(
                cid,
                f"La lista {list_name} no existe.",
                delete_timeout=10
            )
        else:
            ls = dic[list_name]
            ls.append(task_name)
            write_lists(cid, dic)
            bot.send_async_message(
                cid,
                f"Se ha añadido \"{task_name}\" a la lista \"{list_name}\".",
                delete_timeout=10
            )


@bot.message_handler(regexp=command_regex("addAll"))
async def command_add_all(message):
    """addAll command: Add multiple tasks to the specified list."""

    cid = message.chat.id

    partes = message.text.split("\n")
    if len(partes) < 2:
        bot.send_async_message(
            cid,
            "Debe indicar el nombre de la lista y escribir una línea"
            "por cada nueva tarea separados por una coma. Ejemplo:\n"
            "```\n"
            "/addAll Lista1\n"
            "Tarea1\n"
            "Tarea2\n"
            "```",
            parse_mode="markdown",
            delete_timeout=10
        )
    else:
        list_name = to_sentence(partes[0][8:])
        tasks = partes[1:]
        asyncio.create_task(add_all(cid, list_name, tasks))


@bot.message_handler(regexp=command_regex("show"))
async def command_show(message):
    """show command: Display all the tasks in the specified list."""

    cid = message.chat.id

    list_name = to_sentence(message.text[6:])
    asyncio.create_task(show_lists(cid, list_name))


@bot.message_handler(regexp=command_regex("delList"))
async def command_del_list(message):
    """delList command: Remove a list and all of its tasks."""

    cid = message.chat.id
    dic = get_lists(cid)

    list_name = to_sentence(message.text[9:])
    if list_name in dic.keys():
        dic.pop(list_name)
        write_lists(cid, dic)
        bot.send_async_message(
            cid,
            f"La lista {list_name} ha sido eliminada.",
            delete_timeout=10
        )
    elif list_name == "":
        bot.send_async_message(
            cid,
            "Debe indicar la lista que eliminar.",
            delete_timeout=10
        )
    else:
        bot.send_async_message(
            cid,
            f"La lista {list_name} no existe.",
            delete_timeout=10
        )


@bot.message_handler(regexp=command_regex("del"))
async def command_del(message):
    """del command: Remove a single task Elimina una única tarea de la lista especificada."""

    cid = message.chat.id
    dic = get_lists(cid)

    partes = message.text.split(",")
    if len(partes) < 2:
        bot.send_async_message(
            cid,
            "Debe indicar el nombre de la lista y el número de la tarea "
            "separados por una coma. Ejemplo: /del Lista1, 0",
            delete_timeout=10
        )
    else:
        list_name = to_sentence(partes[0][5:])
        asyncio.create_task(delete_task(cid, list_name, partes[1]))


@bot.message_handler(regexp=command_regex("delAll"))
async def command_del_all(message):
    """dellAll command: Remove a single task from the specified list."""

    cid = message.chat.id

    partes = message.text.split(",")
    if len(partes) < 2:
        bot.send_async_message(
            cid,
            "Debe indicar el nombre de la lista y el número de la tarea "
            "separados por una coma. Ejemplo: /del Lista1, 0",
            delete_timeout=10
        )
    else:
        list_name = to_sentence(partes[0][7:])
        del_all(cid, list_name, partes[1:])


@bot.message_handler(regexp=command_regex("(empty|clear)"))
async def command_empty(message):
    """empty command: Clear all the tasks from the specified list."""

    cid = message.chat.id
    dic = get_lists(cid)

    list_name = to_sentence(message.text[6:])
    if list_name in dic.keys():
        size = len(dic[list_name])
        dic[list_name] = []
        write_lists(cid, dic)
        bot.send_async_message(
            cid,
            f"Se han eliminado {size} tareas de la lista \"{list_name}\".",
            delete_timeout=10
        )
    elif list_name == "":
        bot.send_async_message(
            cid,
            "Debe indicar la lista que vaciar.",
            delete_timeout=10
        )
    else:
        bot.send_async_message(
            cid,
            f"La lista {list_name} no existe.",
            delete_timeout=10
        )


@bot.message_handler(regexp=command_regex("done"))
async def command_done(message):
    """done command: Set a single task as done."""

    cid = message.chat.id

    partes = message.text.split(",")
    if len(partes) < 2:
        bot.send_async_message(
            cid,
            "Debe indicar el nombre de la lista y el número de la tarea "
            "separados por una coma. Ejemplo: /done Lista1, 0",
            delete_timeout=10
        )
    else:
        list_name = to_sentence(partes[0][6:])
        task_number = None
        try:
            task_number = int(partes[1])
        except:
            bot.send_async_message(
                cid,
                "No ha indicado un número de tarea válido.",
                delete_timeout=10
            )
            return
        done_task(cid, list_name, task_number)


@bot.message_handler(commands=["git", "github", "source", "src"])
async def command_github(message):
    """github command: Display a link to this bot"s code repository."""

    cid = message.chat.id

    bot.send_async_message(
        cid,
        (
            "Puedes encontrar el código fuente de este bot en "
            "[GitHub](https://github.com/Pablo-Davila/TasksListsBot)"
        ),
        parse_mode="Markdown",
    )


@bot.message_handler(regexp=command_regex("id"))
async def command_id(message):
    """id command: Display current chat's id."""

    cid = message.chat.id
    bot.send_async_message(cid, f"El id de su chat es {cid}")


@bot.callback_query_handler(func=lambda call: True)
async def handle_call(call):
    """General callback query handler."""

    cid = call.message.chat.id
    uid = call.from_user.id
    data = call.data.split("#")
    func = data[0]

    markup = types.ForceReply()

    if func == "addall":
        list_name = data[1]
        asyncio.create_task(bot.answer_callback_query(call.id, "Success"))

        await bot.set_state(uid, UserStates.add_all_tasks, cid)
        asyncio.create_task(bot.add_data(uid, cid, select_list=list_name))

        bot.send_async_message(
            cid,
            "Escriba en líneas separadas todas las tareas que desee añadir.",
            reply_markup=markup,
            delete_timeout=60
        )

    elif func == "doneall":
        list_name = data[1]
        asyncio.create_task(bot.answer_callback_query(call.id, "Success"))

        await bot.set_state(uid, UserStates.done_all_tasks_numbers, cid)
        asyncio.create_task(bot.add_data(uid, cid, select_list=list_name))

        bot.send_async_message(
            cid,
            "Escriba los números de las tareas hechas separados por espacios.",
            reply_markup=markup,
            delete_timeout=60
        )

    elif func == "delall":
        list_name = data[1]
        asyncio.create_task(bot.answer_callback_query(call.id, "Success"))

        await bot.set_state(uid, UserStates.del_all_tasks_numbers, cid)
        asyncio.create_task(bot.add_data(uid, cid, select_list=list_name))

        bot.send_async_message(
            cid,
            "Escriba los números de las tareas que borrar separados por espacios.",
            reply_markup=markup,
            delete_timeout=60
        )

    else:
        print("Unknown callback query: " + call.data)


@bot.message_handler(state="*", commands="cancel")
async def command_cancel(message):
    """Cancel state."""

    cid = message.chat.id

    await bot.send_message(cid, "Your state was cancelled.", delete_timeout=10)
    await bot.delete_state(message.from_user.id, cid)


@bot.message_handler(state=UserStates.select_list)
async def select_list(message):
    cid = message.chat.id

    list_name = message.text.split("#")[0][:-1]
    await show_lists(cid, list_name)
    await bot.delete_state(message.from_user.id, cid)


@bot.message_handler(state=UserStates.add_all_tasks)
async def add_all_state(message):
    cid = message.chat.id
    uid = message.from_user.id

    async with bot.retrieve_data(uid, cid) as user_data:
        list_name = user_data["select_list"]
    await bot.delete_state(uid, cid)

    asyncio.create_task(add_all(
        cid,
        list_name,
        message.text.split("\n")
    ))
    await bot.delete_state(uid, cid)


@bot.message_handler(state=UserStates.done_all_tasks_numbers)
async def done_all_state(message):
    cid = message.chat.id
    uid = message.from_user.id

    async with bot.retrieve_data(uid, cid) as user_data:
        list_name = user_data["select_list"]
    await bot.delete_state(uid, cid)

    asyncio.create_task(done_all(
        cid,
        list_name,
        message.text.split(" ")
    ))
    await bot.delete_state(uid, cid)


@bot.message_handler(state=UserStates.del_all_tasks_numbers)
async def del_all_state(message):
    cid = message.chat.id
    uid = message.from_user.id

    async with bot.retrieve_data(uid, cid) as user_data:
        list_name = user_data["select_list"]
    await bot.delete_state(uid, cid)

    asyncio.create_task(del_all(
        cid,
        list_name,
        message.text.split(" ")
    ))


if __name__ == "__main__":
    print("\nRunning TasksListsBot.py")
    asyncio.run(bot.polling())
