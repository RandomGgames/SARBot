from os import system
system("title " + "SARBot.py")
import discord
import configparser
import time
import datetime
client = discord.Client()
config = configparser.ConfigParser()
config.read("config.ini")

def get_self_assignable_roles(message):
	roles = message.guild.roles
	roles.reverse()
	start_marker = ""
	end_marker = ""
	bot_role = ""
	for index, role in enumerate(roles):
		if role.name.lower() == "---sarbot start":
			start_marker = index
		elif role.name.lower() == "---sarbot end":
			end_marker = index
		elif role.name.lower() == "sarbot":
			bot_role = index
	
	if start_marker == "":
		return 1 #Start marker cannot be found
	elif end_marker == "":
		return 2 #End marker cannot be found
	elif start_marker > end_marker:
		return 3 #Markers in wrong order
	elif bot_role == "":
		return 4 #Bot role cannot be found
	elif start_marker < bot_role:
		return 5 #Bot role is below start marker
	
	return roles[start_marker + 1:end_marker] #return list of roles between markers

def log(text):
	if (datetime.datetime.now().time().hour > 12):
		timestamp = str(datetime.date.today().month) + "/" + str(datetime.date.today().day) + "/" + str(datetime.date.today().year) + " | " + str(datetime.datetime.now().time().hour - 12) + ":" + str(datetime.datetime.now().time().minute) + ":" + str(datetime.datetime.now().time().second) + ":" + str(datetime.datetime.now().time().microsecond) + " pm"
	else:
		timestamp = str(datetime.date.today().month) + "/" + str(datetime.date.today().day) + "/" + str(datetime.date.today().year) + " | " + str(datetime.datetime.now().time().hour) + ":" + str(datetime.datetime.now().time().minute) + ":" + str(datetime.datetime.now().time().second) + ":" + str(datetime.datetime.now().time().microsecond) + " am"
	print(str(text))
	with open("logs.txt", "a", encoding="UTF-8") as file: file.write(timestamp + " - " + str(text) + "\n")

@client.event
async def on_ready():
	print("Ready!")

@client.event
async def on_guild_join(guild):
	log("Bot has been added to " + str(guild) + " (id:" + str(guild.id) + ").")

@client.event
async def on_guild_remove(guild):
	log("Bot has been removed from " + str(guild) + " (id:" + str(guild.id) + ").")

#@client.event
#async def on_error(event, *args, **kwargs):
#    message = args[0]
#    log("CRITICAL ERROR!\nEvent: " + str(event) + "\nArgs: " + str(args) + "\nKwargs: " + str(kwargs) + ".")

@client.event
async def on_message(message):
	
	if message.author == client.user: return
	elif message.author.bot == True: return
	elif message.channel.type is discord.ChannelType.private: 
		log("Ignoring DM from \"" + str(message.channel.recipient.name) + "#" + str(message.channel.recipient.discriminator) + "\" (id: " + str(message.channel.recipient.id) + ").")
		return
	
	usertagid = "\"" + str(message.author.name) + "#" + str(message.author.discriminator) + " (id:" + str(message.author.id) + ")\""
	guildnameid = "\"" + str(message.guild.name) + " (id:" + str(message.guild.id) + ")\""
	channelnameid = "\"" + str(message.channel.name) + " (id:" + str(message.channel.id) + ")\""
	
	if config.has_option("Server Configs", str(message.guild.id)) == False:
		config["Server Configs"][str(message.guild.id)] = ""
		
	if message.content.lower() == "!sarbot help":
		await message.channel.send("Check your DMs!")
		await message.author.send("__**Initial Setup**__:\n- Create two roles named `---sarbot start` and `---sarbot end`, placing the start marker above the end marker. Also make sure the bot's role is above these so it can give users the roles. \n- Place roles you want to be self assignable between the two maker roles. Ones starting with --- will be seen as sections where you can separate roles into different categories.\n\n- This bot requires *IT'S OWN ROOM THAT OTHER BOT'S DON'T USE*. To set which room, use the command `!sarbot setroom`.\n- After all that, you can create the role embed using the command `!sarbot roles`.\n- All that's required now is users are able to talk in the text room to toggle roles.\n\nIf you have any other issues, don't hesitate to join the support discord at https://discord.gg/GNWFjKh")
		log("Sent help DM to " + usertagid)
		
	if message.content.lower() == "!sarbot setroom":
		if message.author.guild_permissions.administrator:
			config["Server Configs"][str(message.guild.id)] = str(message.channel.id)
			config.write(open('config.ini', 'w'))
			await message.channel.send("✅ Self assignable roles room set to this room", delete_after = 2)
			log(usertagid + " set the self assignable roles room on " + guildnameid + " to " + channelnameid + ".")
		else:
			await message.channel.send("❌ You don't have the administrator permission", delete_after = 2)
			log(usertagid + " tried to set the bot room to " + channelnameid + " but doesn't have administrator on " + guildnameid + ".")
		await message.delete(delay = 0.5)
		
	if message.content.lower() == "!sarbot report":
		report_text  = "\nusertagid: " + str(usertagid) + "\nguildnameid: " + str(guildnameid) + "\nchannelnameid: " + str(channelnameid) + "\n\nRoles:\n\n"
		for role in message.guild.roles:
			report_text = report_text + "Name: " + str(role.name) + "\n"
			report_text = report_text + "ID: " + str(role.id) + "\n"
			report_text = report_text + "position: " + str(role.position) + "\n"
			report_text = report_text + "created_at: " + str(role.created_at) + "\n\n"
		report_text = report_text + "END OF REPORT"
		print("")
		log(usertagid + " reported an issue on " + guildnameid + " in " + channelnameid + ".\n\nISSUE REPORT:\n" + str(report_text))
		print("")
		await message.channel.send("✅ Log report sent to bot owner.", delete_after = 3)
		await message.delete(delay = 3)
		
	elif config["Server Configs"][str(message.guild.id)] == str(message.channel.id):
		roles = get_self_assignable_roles(message)
		if type(roles) == int:
			if roles == 1: #Start marker cannot be found
				await message.channel.send("❌ Self assignable role start marker cannot be found (Wrong name/doesn't exist? Needs to be named \"--- sarb start marker ---\"). Do `!sarbot help` for setup instructions.", delete_after = 5)
				log("Error " + str(roles) + " on " + guildnameid + " for " + usertagid + ", self assignable role start marker cannot be found.")
			elif roles == 2: #End marker cannot be found
				await message.channel.send("❌ Self assignable role end marker cannot be found (Wrong name/doesn't exist? Needs to be named \"--- sarb end marker ---\"). Do `!sarbot help` for setup instructions.", delete_after = 5)
				log("Error " + str(roles) + " on " + guildnameid + " for " + usertagid + ", self assignable role end marker cannot be found.")
			elif roles == 3: #Markers in wrong order
				await message.channel.send("❌ Self assignable makers are in wrong order (Start needs to be on top!). Do `!sarbot help` for setup instructions.", delete_after = 5)
				log("Error " + str(roles) + " on " + guildnameid + " for " + usertagid + ", self assignable makers are in wrong order.")
			elif roles == 4: #Bot role cannot be found
				await message.channel.send("❌ Bot role cannot be found (Needs to be named SARBot! Don't change it!). Do `!sarbot help` for setup instructions.", delete_after = 5)
				log("Error " + str(roles) + " on " + guildnameid + " for " + usertagid + ", bot role cannot be found.")
			elif roles == 5: #Bot role is below start marker
				await message.channel.send("❌ Bot role is below start maker (Needs to be above!). Do `!sarbot help` for setup instructions.", delete_after = 5)
				log("Error " + str(roles) + " on " + guildnameid + " for " + usertagid + ", bot role is below start maker.")
		
		#Create Embed
		elif message.content.lower() == "!sarbot roles":
			if message.author.guild_permissions.administrator == True:
				#Check if there are self assignable roles
				self_assignable_roles_list = []
				for role in roles:
					if not role.name.startswith("---"):
						self_assignable_roles_list.append(role)
				
				#If there are no self assignable roles
				if len(self_assignable_roles_list) ==  0:
					await message.channel.send("❌ No roles are marked as self-assignable (Someone needs to add/move some between the start and end markers). Do `!sarbot help` for setup instructions.", delete_after = 5)
					log("Error in " + guildnameid + " for " + udertagid + ", no roles are marked as self-assignable.")
				
				#If there are self assignable roles
				else:
					#No sections defined, send regular list:
					if not any(role for role in roles if role.name.startswith("---")):
						embed_roles_string = ""
						role_number = 0
						for embed_role in roles:
							role_number += 1
							embed_roles_string = str(embed_roles_string) + str(role_number) + " <@&" + str(embed_role.id) + ">\n"
						await message.channel.send(embed = discord.Embed(title="Self Assignable Roles", color = 0x00ff00, description = embed_roles_string))
						await message.channel.send(embed = discord.Embed(title="How to", color = 0x00ff00,description="To toggle a role (add it if you don't have it, remove it if you already do), say the number(s) that is/are in front of the role(s) that you want.\nExample: Say `1, 3-5` in chat and the roles with the numbers `1, 3, 4, 5` will be given if you don't have them already, or removed if you do have them."))
						log("Created roles embed on " + guildnameid + " in " + channelnameid + " for " + usertagid + ".")		
					
					#A section is defined somewhere, find where and create sub categories
					else:
						embed_roles = roles.copy()
						embed_roles_list = []
						field_name = "Untitled"
						role_number = 0
						assignable_roles_count = 0
						embed = discord.Embed(title = "Self Assignable Roles", color = 0x00ff00)
						for role in embed_roles:
							if role.name.startswith("---"):
								if len(embed_roles_list) > 0:
									#Send list of embeds with no title
									embed_roles_string = ""
									for embed_role in embed_roles_list:
										role_number += 1
										embed_roles_string = str(embed_roles_string) + str(role_number) + " <@&" + str(embed_role.id) + ">\n"
									embed.add_field(name = field_name, value = embed_roles_string, inline = True)
									embed_roles_list = []
									#Set embed name for next field
									field_name = role.name[3:]
								else:
									#Set field name because there is no previous 
									field_name = role.name[3:]
							else:
								#Add current non-field name role to available roles list
								assignable_roles_count += 1
								embed_roles_list.append(role)
						#Before sending final field, make sure it's not an empty list
						if len(embed_roles_list) > 0:
							embed_roles_string = ""
							for embed_role in embed_roles_list:
								role_number += 1
								embed_roles_string = str(embed_roles_string) + str(role_number) + " <@&" + str(embed_role.id) + ">\n"
							embed.add_field(name = field_name, value = embed_roles_string, inline = True)
						if assignable_roles_count > 0:
							#Send Final Embed
							await message.channel.send(embed = embed)
							await message.channel.send(embed = discord.Embed(title="How to", color = 0x00ff00,description="To toggle a role (add it if you don't have it, remove it if you already do), say the number(s) that is/are in front of the role(s) that you want.\nExample: Say `1, 3-5` in chat and the roles with the numbers `1, 3, 4, 5` will be given if you don't have them already, or removed if you do have them."))
							log("Created roles embed on " + guildnameid + " in " + channelnameid + " for " + usertagid + ".")
			else:
				await message.channel.send("❌ You don't have a role with administrator permission! You need a role with that permission.", delete_after = 5)
				log(usertagid + " doesn't have administrator on " + guildnameid + "while trying to create the roles embed in " + channelnameid + ".")
		
		#Request role toggle
		else:
			#Check if there are self assignable roles
			self_assignable_roles_list = []
			for role in roles:
				if not role.name.startswith("---"):
					self_assignable_roles_list.append(role)
			#If there are no self assignable roles
			if len(self_assignable_roles_list) ==  0:
				await message.channel.send("❌ No roles are marked as self-assignable (Someone needs to add/move some between the start and end markers). Do `!sarbot help` for setup instructions.", delete_after = 5)
				log("Error in " + guildnameid + " for " + usertagid + ", no roles are marked as self-assignable.")
			
			#If there are self assignable roles
			else:
				#Clean up string
				wanted_roles_message = message.content
				wanted_roles_message = wanted_roles_message.replace(",", " ")
				while "  " in wanted_roles_message:
					wanted_roles_message = wanted_roles_message.replace("  ", " ")
				if wanted_roles_message[0] == " ":
					wanted_roles_message = wanted_roles_message[1:]
				if wanted_roles_message[-1] == " ":
					wanted_roles_message = wanted_roles_message[:-1]
				wanted_roles_message = wanted_roles_message.replace(",", " ")
				
				#Check for non-allowed characters
				allowed_characters = [" ", "-", "0", "1", "2", "3", "4", "5", "6", "7", "8", "9"]
				not_allowed_characters = ""
				not_allowed_characters = wanted_roles_message
				for character in allowed_characters:
					if character in wanted_roles_message:
						not_allowed_characters = not_allowed_characters.replace(character, "")
				
				#Error checks
				if len(not_allowed_characters) > 0:
					await message.channel.send("❌ Invalid characters in message", delete_after = 3)
					log("Invalid characters sent in " + channelnameid + " from " + usertagid + " on " + guildnameid + ".")
				elif wanted_roles_message[0] == "-" or wanted_roles_message[-1] == "-" or "- " in wanted_roles_message or " -" in wanted_roles_message or "-," in wanted_roles_message:
					await message.channel.send("❌ Invalid range request for roles", delete_after = 3)
					log("Invalid request for roles sent in " + channelnameid + " by " + usertagid + " on " + guildnameid + ".")
				#No errors found, continue with creating list of numbers
				else:
					#Turn wanted roles string into list
					wanted_roles_list = list(wanted_roles_message.split(" "))
					
					#Removes ranges of numbers and adds numbers within range
					had_error = 0
					for index, each in enumerate(wanted_roles_list):
						if "-" in each: #Has range of numbers
							#Get range of numbers
							get_range = list(each.split("-"))
							if get_range[0] == "0" or get_range[-1] == "0":
								had_error = 1
								await message.channel.send("❌ 0 is not a valid role number", delete_after = 3)
							elif int(get_range[0]) < int(get_range[-1]) + 1:
								numbers_in_range = list(range(int(get_range[0]), int(get_range[-1]) + 1))
								#Remove the range request and add the numbers in the range
								wanted_roles_list.pop(index)
								for number in numbers_in_range:
									wanted_roles_list.append(str(number))
							else:
								had_error = 1
								await message.channel.send("❌ Invalid request for roles range. First number has to be higher than second number", delete_after = 5)
								log("Invalid request for roles range \"" + str(each) + "\" sent into " + channelnameid + " by " + usertagid + " on " + guildnameid + ".")
								
					if had_error != 1:
						#Remove duplicates if there are any
						wanted_roles_list = list(dict.fromkeys(wanted_roles_list))
						#Turn wanted roles strings into ints
						for i in range(len(wanted_roles_list)):
							wanted_roles_list[i] = int(wanted_roles_list[i])
					
						#Toggle roles based on wanted roles list and available roles list
						for wanted_role_number in wanted_roles_list:
							#If role is outside limit
							if len(self_assignable_roles_list) < wanted_role_number or wanted_role_number == 0:
								await message.channel.send("❌ " + str(wanted_role_number) + " is not a valid role number", delete_after = 5)
								log(usertagid + " requested an invalid role number " + str(wanted_role_number) + " in " + channelnameid + " on " + guildnameid + ".")
							#Toggle role
							else:
								#If has role:
								if self_assignable_roles_list[wanted_role_number - 1] in message.author.roles:
									#Remove
									await message.author.remove_roles(self_assignable_roles_list[wanted_role_number - 1])
									await message.channel.send("✅ Removed the " + str(self_assignable_roles_list[wanted_role_number - 1].name) + " role", delete_after = 5)
									log("Removed the \"" + str(self_assignable_roles_list[wanted_role_number - 1].name) + "\" (id:" + str(self_assignable_roles_list[wanted_role_number - 1].id) + ") role from " + usertagid + " on " + guildnameid + ".")
								#If doesn't have role:
								else:
									#Give
									await message.author.add_roles(self_assignable_roles_list[wanted_role_number - 1])
									await message.channel.send("✅ Added the " + str(self_assignable_roles_list[wanted_role_number - 1].name) + " role", delete_after = 5)
									log("Added the \"" + str(self_assignable_roles_list[wanted_role_number - 1].name) + "\" (id:" + str(self_assignable_roles_list[wanted_role_number - 1].id) + ") role to " + usertagid + " on " + guildnameid + ".")
		await message.delete(delay = 3)

client.run(config["Bot"]["Token"])
