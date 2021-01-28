import discord
import os
import datetime
import copy

client = discord.Client()

import gspread
from oauth2client.service_account import ServiceAccountCredentials

# use creds to create a client to interact with the Google Drive API
scope = ['https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client_secret.json', scope)
sheet_client = gspread.authorize(creds)

summary_row = [
    "name", 
    '=sumif(Sheet1!A$2:A$1000,A%s,Sheet1!B$2:B$1000)', 
    '=VLOOKUP(B%s,Sheet3!A$1:D$301,4,TRUE)',
    '=VLOOKUP(B%s,Sheet3!A$1:D$301,1,TRUE)', 
    '=VLOOKUP(B%s,Sheet3!A$1:D$301,2,TRUE)']

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sh = sheet_client.open('Skill System')
sheet = sh.sheet1
summaryPage = sh.get_worksheet(1)

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith("$startSkill"):
        values = message.content.split("$startSkill")

        if (len(values) < 2):
            await message.channel.send("Not enough arguments passed for $startSkill")
            return

        skill = values[1].strip()
        key = str(message.author) + "|" + skill
        summary_row_copy = copy.copy(summary_row)
        summary_row_copy[0] = key

        for i in range(1, len(summary_row_copy)):
            summary_row_copy[i] = summary_row_copy[i] % (len(summaryPage.get_all_records()) + 2)

        summaryPage.append_row(summary_row_copy, value_input_option="USER_ENTERED")

        await message.channel.send("Created skill %s for %s" % (skill, message.author))

    if message.content.startswith('$report'):
        values = message.content.split(" ")

        if (len(values) < 3):
            await message.channel.send("Not enough arguments passed for $report")
            return

        xp = values[1].split("xp")[0]
        skill = values[2]
        key = str(message.author) + "|" + skill
        sheet.append_row([key, int(xp), str(datetime.datetime.now())])
        records = summaryPage.get_all_records()

        total_xp = -1
        min_xp = -1
        max_xp = -1
        level = -1
        for record in records:
            if (record["Name"].lower() == key.lower()):
                total_xp = record["Total XP"]
                level = record["Level"]
                min_xp = record["Min Level XP"]
                max_xp = record["Max Level XP"]

        if (total_xp == -1):
            await message.channel.send("It looks like this is a new skill. Please use $startSkill first to start it.")
            return

        xp_to_next_level = max_xp - total_xp

        await message.channel.send(
            '%sxp gained in %s. You are now level %s and %sxp away from level %s' % 
            (xp, skill, level, xp_to_next_level, level + 1))

    if message.content.startswith("$help"):
        help_message = "======== Commands ========\n$report XpAmount ExampleSkill\n$startSkill NewSkillName\n$status SkillName\n=========================="""
        await message.channel.send(help_message)

    if (message.content.startswith("$status")):
        values = message.content.split("$status")

        if (len(values) < 2):
            await message.channel.send("Not enough arguments passed for $status")
            return

        skill = values[1].strip()
        key = str(message.author) + "|" + skill
        total_xp = -1
        min_xp = -1
        max_xp = -1
        level = -1

        records = summaryPage.get_all_records()
        for record in records:
            if (record["Name"].lower() == key.lower()):
                total_xp = record["Total XP"]
                level = record["Level"]
                min_xp = record["Min Level XP"]
                max_xp = record["Max Level XP"]

        if (total_xp == -1):
            await message.channel.send("Could not find a skill named %s under your account." % skill)
            return

        xp_to_next_level = max_xp - total_xp

        await message.channel.send(
            'You are level %s and %sxp away from level %s' % 
            (level, xp_to_next_level, level + 1))
        

client.run('NzkzNjczMTcxMzcwOTAxNTc1.X-vrvQ.bpK58TU7IcIUHO-BUg1cLMYWgqI')
