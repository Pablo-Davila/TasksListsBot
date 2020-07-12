import telebot
import json
import sys

from telebot import types

bot = telebot.TeleBot(sys.argv[1])

help_eng = {
	'lists': "Display the curret set of lists.",
	'addList ListName': "Create a new empty list.",
	'add ListName,TaskName': "Add a task to the list.",
	'addAll ListName': "Add multiple tasks (one per line).",
	'done ListName,TaskNumber': "Mark a task as done.",
	'advanced': "Display advanced commands."
}

help_spa = {
	'lists': "Mostrar el conjunto de listas actual.",
	'addList NombreLista': "Crear una nueva lista vacía.",
	'add NombreLista,NombreTarea': "Añadir una tarea a la lista.",
	'addAll NombreLista': "Añadir multiples tareas (cada una en una línea).",
	'done NombreLista,NumeroTarea': "Marcar una tarea como hecha.",
	'advanced': "Mostrar comandos avanzados."
}

advanced_eng = {
	'show ListName': "Display the tasks of a single list.",
	'delList ListName': "Remove an existing list.",
	'del ListName,TaskNumber': "Remove a task from a list.",
	'delAll ListName,3,1,4': "Remove multiple tasks from a list.",
	'empty ListName': "Remove all the tasks in a given list.",
	'github': "Displays a link to the bot's source code"
}

advanced_spa = {
	'show ListName': "Mostrar las tareas de una única lista.",
	'delList ListName': "Eliminar una lista existente.",
	'del NombreLista,NumeroTarea': "Eliminar una tarea de una lista.",
	'delAll NombreLista,3,1,4': "Eliminar multiples tareas de una lista.",
	'empty NombreLista': "Eliminar todas las tareas de una lista.",
	'github': "Muestra un link al código fuente del bot."
}

news = [
	"2020/07/10 Añadidos los comandos /empty y /delAll.",
	"2020/06/23 Mayor tolerancia a errores de sintaxis en los comandos.",
	"2020/06/23 Añadida una lista de novedades.",
	"2020/06/23 Resistencia a errores: A partir de ahora el bot se reinicia en caso de error, evitando así que deje de funcionar.",
	"Añadido el comando /addAll, que permite añadir múltiples tareas a una lista, con un único comando.",
	"A partir de ahora se toleran errores comunes en las máyúsculas y minúsculas de los comandos.",
	"2020/06/18: Bot creado!",
]

def toSentence(s):
	'''Transforma en una oración correctamente formateada.'''
	return str(s).strip().capitalize()

def getLists(cid):
	'''Devuelve el diccionario de listas del chat especificado.'''
	dic = None
	try:
		with open(f"data\lists_{cid}.json", "r") as f:
			dic = json.loads(f.read())
	except:
		dic = {}
	return dic
	
def menuMarkup():
	# TO-DO
	return types.ReplyKeyboardRemove(selective=False)
	
def writeLists(cid, dic):
	with open(f"data\lists_{cid}.json", "w") as f:
		f.write(json.dumps(dic))
		
def showList(cid, listName):
	dic = getLists(cid)
	
	if(listName in dic.keys()):
		ls = dic[listName]
		res = listName + ":"
		for i in range(len(ls)):
			task = ls[i]
			res += f"\n {i}. {task}"
		if(len(ls) == 0):
			res += "\n(Esta lista está vacía)"
		bot.send_message(cid, res, reply_markup=menuMarkup())
	elif listName == "":
		bot.send_message(cid, "Debe indicar una lista.")
	else:
		bot.send_message(cid, f"La lista {listName} no existe.", reply_markup=menuMarkup())
		
def deleteTask(cid, listName, taskNumber):
	dic = getLists(cid)

	num = None
	try:
		num = int(taskNumber)
	except:
		bot.send_message(cid, "No ha indicado un número de tarea válido.")
		return
		
	if listName in dic.keys():
		ls = dic[listName]
		try:
			taskName = ls.pop(num)
			writeLists(cid, dic)
			bot.send_message(cid, f"La tarea \"{taskName}\" ha sido eliminada.")
		except:
			bot.send_message(cid, f"Índice fuera de rango: {num}.")
	else:
		bot.send_message(cid, f"La lista {listName} no existe.")

@bot.message_handler(regexp="^/start(?i)")
def command_start(message):
	'''Realiza el saludo inicial.'''
	user = message.from_user
	cid = message.chat.id
	ans = f"Hola {user.first_name} {user.last_name}. Encantado de conocerle!"
	ans += "\nEscriba /help para acceder a la lista de comandos básicos."
	bot.send_message(cid, ans)

@bot.message_handler(regexp="^/help(?i)")
def command_help(message):
	'''Muestra los comandos básicos.'''
	cid = message.chat.id
	help = "Estos son los comandos básicos:"
	for c in help_spa:
		help += f"\n*/{c}*: {help_spa[c]}"
	bot.send_message(cid, help, parse_mode='Markdown')

@bot.message_handler(regexp="^/advanced(?i)")
def command_advanced(message):
	'''Muestra los comandos avanzados.'''
	cid = message.chat.id
	help = "Estos son los comandos avanzados:"
	for c in advanced_spa:
		help += f"\n*/{c}*: {advanced_spa[c]}"
	bot.send_message(cid, help, parse_mode='Markdown')

@bot.message_handler(regexp="^/new(s)?(?i)")
def command_news(message):
	'''Muestra las últimas novedades del dessarrollo del bot.'''
	cid = message.chat.id
	text = "*Estas son las últimas novedades:*"
	for new in news:
		text += "\n - " + new
	bot.send_message(cid, text, parse_mode='Markdown')

def showTEMP(message):
	showList(message.chat.id, message.text.split('#')[0][:-1])

@bot.message_handler(regexp="^/list(s)?(?i)")
def command_lists(message):
	'''Muestra las listas disponibles en este chat y el número de elementos de las mismas.'''
	cid = message.chat.id
	dic = getLists(cid)
	markup = types.ReplyKeyboardMarkup(one_time_keyboard=True,selective=True)
	if(dic == {}):
		bot.send_message(cid,"Aún no se ha creado ninguna lista.")
	else:
		c = 0
		fila = ["","",""]
		for l in dic.keys():
			fila[c] = f"{l} #{len(dic[l])}"
			
			if(c == 2):
				c = 0
				markup.row(fila[0],fila[1],fila[2])
			else:
				c += 1
		if(c == 1):
			markup.row(fila[0])
		elif(c == 2):
			markup.row(fila[0],fila[1])
		msg = bot.reply_to(message, "Elija una lista", reply_markup=markup)
		bot.register_next_step_handler(msg, showTEMP)
	
@bot.message_handler(regexp="^/addList(?i)")
def command_addList(message):
	'''Crea una lista nueva con el nombre especificado.'''
	cid = message.chat.id
	listName = toSentence(message.text[9:])
	
	if(len(listName) >= 3):
		dic = getLists(cid)

		dic[listName] = []
		writeLists(cid,dic)
		
		bot.send_message(cid, f"Se ha creado la lista \"{listName}\".")
	else:
		bot.send_message(cid, "El nombre de la lista debe tener al menos 3 caracteres.")

@bot.message_handler(regexp="^/add(?i)")
def command_add(message):
	'''Añade una única tarea a una lista dada.'''
	cid = message.chat.id
	
	partes = message.text.split(',')
	if(len(partes) < 2):
		bot.send_message(cid, "Debe indicar el nombre de la lista y el de la tarea separados por una coma. Ejemplo: /add Lista1, Tarea1")
	else:
		listName = toSentence(partes[0][5:])
		taskName = toSentence(partes[1])
		dic = getLists(cid)
		
		if(len(taskName) < 3):
			bot.send_message(cid, "El nombre de la tarea debe tener al menos 3 caracteres.")
		elif(not listName in dic.keys()):
			bot.send_message(cid, f"La lista {listName} no existe.")
		else:
			ls = dic[listName]
			ls.append(taskName)
			writeLists(cid,dic)
			bot.send_message(cid, f"Se ha añadido \"{taskName}\" a la lista \"{listName}\".")

@bot.message_handler(regexp="^/addAll(?i)")
def command_addAll(message):
	'''Añade múltiples tareas (separadas por línea) a la lista indicada.'''
	cid = message.chat.id
	
	partes = message.text.split('\n')
	if(len(partes) < 2):
		bot.send_message(cid, "Debe indicar el nombre de la lista y el de la tarea separados por una coma. Ejemplo: /add Lista1, Tarea1")
	else:
		listName = toSentence(partes[0][8:])
		tasks = partes[1:]
		dic = getLists(cid)
		if listName in dic.keys():
			ls = dic[listName]
			c = 0
			for taskName in tasks:
				taskName = toSentence(taskName)
				if(len(taskName) >= 3):
					ls.append(taskName)
					c += 1
			writeLists(cid,dic)
			bot.send_message(cid, f"Se han añadido {c} tareas a la lista \"{listName}\".")
		else:
			bot.send_message(cid, f"La lista {listName} no existe.")
		
@bot.message_handler(regexp="^/show(?i)")
def command_show(message):
	'''Muestra todas las tareas de la lista indicada.'''
	cid = message.chat.id
	
	listName = toSentence(message.text[6:])
	showList(cid, listName)

@bot.message_handler(regexp="^/dellist(?i)")
def command_delList(message):
	'''Elimina una lista y todas sus tareas asociades.'''
	cid = message.chat.id
	dic = getLists(cid)
	
	listName = toSentence(message.text[9:])
	if listName in dic.keys():
		dic.pop(listName)
		writeLists(cid, dic)
		bot.send_message(cid, f"La lista {listName} ha sido eliminada.")
	elif listName == "":
		bot.send_message(cid, "Debe indicar la lista que eliminar.")
	else:
		bot.send_message(cid, f"La lista {listName} no existe.")

@bot.message_handler(regexp="^/del(?i)")
def command_del(message):
	'''Elimina una única tarea de la lista especificada.'''
	cid = message.chat.id
	dic = getLists(cid)
	
	partes = message.text.split(',')
	if(len(partes) < 2):
		bot.send_message(cid, "Debe indicar el nombre de la lista y el número de la tarea separados por una coma. Ejemplo: /del Lista1, 0")
	else:
		listName = toSentence(partes[0][5:])
		deleteTask(cid, listName, partes[1])

@bot.message_handler(regexp="^/delAll(?i)")
def command_del(message):
	'''Elimina una única tarea de la lista especificada.'''
	cid = message.chat.id
	dic = getLists(cid)
	
	partes = message.text.split(',')
	if(len(partes) < 2):
		bot.send_message(cid, "Debe indicar el nombre de la lista y el número de la tarea separados por una coma. Ejemplo: /del Lista1, 0")
	else:
		listName = toSentence(partes[0][7:])
		indices = sorted(partes[1:], reverse=True)
		for num in indices:
			deleteTask(cid, listName, num)
	
@bot.message_handler(regexp="^/(empty|clear)(?i)")
def command_del(message):
	'''Elimina todas las tareas de la lista especificada.'''
	cid = message.chat.id
	dic = getLists(cid)
	
	listName = toSentence(message.text[6:])
	if listName in dic.keys():
		size = len(dic[listName])
		dic[listName] = []
		writeLists(cid, dic)
		bot.send_message(cid, f"Se han eliminado {size} tareas de la lista \"{listName}\".")
	elif listName == "":
		bot.send_message(cid, "Debe indicar la lista que vaciar.")
	else:
		bot.send_message(cid, f"La lista {listName} no existe.")

@bot.message_handler(regexp="^/done(?i)")
def command_done(message):
	'''Marca como hecha una única tarea de una lista concreta.'''
	cid = message.chat.id
	dic = getLists(cid)
	
	partes = message.text.split(',')
	if(len(partes) < 2):
		bot.send_message(cid, "Debe indicar el nombre de la lista y el número de la tarea separados por una coma. Ejemplo: /done Lista1, 0")
	else:
		listName = toSentence(partes[0][6:])
		taskNumber = None
		try:
			taskNumber = int(partes[1])
		except:
			bot.send_message(cid, "No ha indicado un número de tarea válido.")
			return
		
		if listName in dic.keys():
			ls = dic[listName]
			try:
				taskName = ls.pop(taskNumber)
				if("Hechas" in dic.keys()):
					dic["Hechas"].append(taskName)
				else:
					dic["Hechas"] = [taskName]
				writeLists(cid, dic)
				bot.send_message(cid, "Tarea marcada como hecha.")
			except:
				bot.send_message(cid, "Índice fuera de rango.")
		else:
			bot.send_message(cid, f"La lista {listName} no existe.")

@bot.message_handler(commands=["git", "github", "source", "src"])
def command_github(message):
	cid = message.chat.id
	
	bot.send_message(cid, "Puedes encontrar el código fuente de este bot en [GitHub](https://github.com/Pablo-Davila/TasksListsBot)", parse_mode='Markdown')
	
@bot.message_handler(regexp="^/id(?i)")
def command_id(message):
	cid = message.chat.id
	bot.send_message(cid,f"El id de su chat es {cid}")
	
print("\nRunning TasksListsBot.py")
bot.polling()
