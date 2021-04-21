from __future__ import print_function
import discord
import os.path
import gspread
import time
import difflib

from dotenv import load_dotenv
from discord.ext import commands
from ast import literal_eval

load_dotenv()
gc = gspread.service_account(filename="rolebotCredentials.json")
TOKEN = os.getenv('DISCORD_TOKEN')
intents = discord.Intents.all()
intents.typing = False
intents.presences = False
intents.members = True
print("booting")
bot = commands.Bot(command_prefix='~', intents=intents)
message = "Hiya! Welcome to the LOST 2021 Server! \n" \
          "If you are a competing in the competition please fill out this form for role assignment \n" \
          "https://forms.gle/ktDbcbMeJXXRXTJd7 \n" \
          "If you are a volunteer, please fill out this form (if you havent already) \n" \
          "https://forms.gle/swtz3QGERqrRcoee8  \n" \
          "If you are a spectator,, your role will be automatically be assigned, no need to do anything"

@bot.event
async def on_ready():
    print(f'{bot.user.name} is loaded')

@bot.event
async def on_member_join(member):
    spectator = discord.utils.get(member.guild.roles, name="spectator")
    await member.add_roles(spectator)
    await member.send(message)
    print("New Member")

@bot.command(pass_context=True)
async def changeColor(ctx, *, args):
    args = int(args, 16)
    gen = (y for y in ctx.author.roles if y.name.lower() != "member" and y.name.lower() != "captain")
    for y in gen:
        role = discord.utils.get(ctx.author.roles, name=y.name)
    await role.edit(reason=None, colour=args)
    await ctx.send(role.color)

@bot.command(pass_context=True)
@commands.has_role("Volunteers")
async def badChannel(ctx):
    guild = ctx.guild
    members = ctx.guild.members
    await ctx.send("Reset Members")
    for d in range(1, 9):
        currentdivision="Division " + str(d)
        print(currentdivision)
        division_channels = discord.utils.get(ctx.guild.categories, name="Division " + str(d)).channels
        voiec_channels = discord.utils.get(ctx.guild.categories, name="Division " + str(d)).voice_channels
        for c in division_channels:
            await c
            await c.set_permissions(discord.utils.get(ctx.guild.roles, name="spectator"),
                                                                read_messages=True, send_messages=False)
@bot.command(pass_context=True)
@commands.has_role("Volunteers")
async def resetChannels(ctx):
    guild = ctx.guild
    members = ctx.guild.members
    await ctx.send("Reset Channels")
    for d in range(1, 9):
        currentdivision= "Division " + str(d)
        division_channels = discord.utils.get(ctx.guild.categories, name="Division " + str(d)).channels
        division_voice = discord.utils.get(ctx.guild.categories, name="Division " + str(d)).voice_channels
        for c in division_channels:
            await c.edit(sync_permissions=True)
        counter = 1
        for bc in division_channels[0:2]:
            bot_name = "Mr. Clean" if counter == 1 else "Mr. Clean " + str(counter)
            print(discord.utils.get(members, name=bot_name))
            await bc.set_permissions(discord.utils.get(members, name=bot_name), read_messages=True, send_messages=True)
            counter += 1
            for rc in ctx.guild.roles:
                await bc.set_permissions(rc, read_messages=True, send_messages=False)
        voice_counter = 1
        for bv in division_voice[0:2]:
            bot_name = "Mr. Clean" if counter == 1 else "Mr. Clean " + str(counter)
            print(discord.utils.get(members, name=bot_name))
            await bv.set_permissions(discord.utils.get(members, name=bot_name), connect=True, speak=True)
            print(difflib.get_close_matches("Will[Lynbrook]", "Mr. Clean", n=1))
            for r in ctx.guild.roles:
                if difflib.get_close_matches("Mr. Clean", r.name, n=1) == None:
                    await bv.set_permissions(r, connect=True, speak=False)
            voice_counter += 1
@bot.command(pass_context=True)
@commands.has_role("Volunteers")
async def RemoveSpectator(ctx):
    guild = ctx.guild
    await ctx.send("Removing Spectator")
    ctx.guild.fetch_members()
    users = ctx.guild.members
    roles= ctx.guild.roles
    for u in users:
        urole=u.roles
        await u.add_roles(discord.utils.get(roles, name="Member"))
        if len(urole) > 3 and discord.utils.get(urole, name="spectator") != None:
            await u.remove_roles(discord.utils.get(urole, name="spectator"))
            # Either creates the role and adds person to it or adds the role to the person

@bot.command(pass_context=True)
@commands.has_role("Volunteers")
async def match(ctx, division_coord, match_num, begin_end):
    await ctx.send("Movement Started")
    #Variable Definitions
    ctx.guild.fetch_members()
    guild = ctx.guild
    sh = gc.open("SCHEDULE")
    wr = sh.get_worksheet(3)
    coord_translate = literal_eval(division_coord)
    await ctx.send(division_coord)
    division, room = coord_translate
    match = int(match_num)
    row = 1
    roles = ctx.guild.roles
    rolesString=[]
    end = True if begin_end == "end" else False

    #Grabs the text channel which you buzz in
    division_channels = discord.utils.get(ctx.guild.categories, name="Division " + str(division)).channels
    buzz_channel = discord.utils.get(division_channels, name="room-" + str(room) + "-buzzing")
    print(buzz_channel)

    #Grabs the voice channel which you buzz in and grabs ppl in voice channel
    voice_division = discord.utils.get(ctx.guild.categories, name="Division " + str(division)).voice_channels
    voice_buzz = discord.utils.get(voice_division, name="Room " + str(room) + " Audio")
    voice_general = discord.utils.get(ctx.guild.channels, name="chill")
    print(voice_buzz)

    #Gets Team Names
    for role in roles:
        rolesString.append(role.name)
    row = division*2 if room == 1 else division*2+1
    teamA = wr.cell(row, match*2).value
    print(teamA)
    teamB = wr.cell(row, match*2+1).value
    print(teamB)
    teamC = wr.cell(row, match*2+2).value
    teamD = wr.cell(row, match*2+3).value
    roleA = difflib.get_close_matches(teamA, rolesString, n=1)[0]
    roleB = difflib.get_close_matches(teamB, rolesString, n=1)[0]
    if teamC != None and teamD != None:
        roleC = difflib.get_close_matches(teamC, rolesString, n=1)[0]
        roleD = difflib.get_close_matches(teamD, rolesString, n=1)[0]
    server = ctx.message.guild

    if end:
        # If end moves players out of their VC into general and revises perms
        members = voice_buzz.members
        for member in members:
            if (member.voice is not None and member.voice.channel != voice_general):
                if roleA.lower() in [roles.name.lower() for roles in member.roles]:
                    await member.move_to(voice_general)

        for member in members:
            if (member.voice is not None and member.voice.channel != voice_general):
                if roleB.lower() in [roles.name.lower() for roles in member.roles]:
                    await member.move_to(voice_general)
    else:
        # If start moves players into their match VC
        members = ctx.guild.members
        for member in members:
            if (member.voice is not None and member.voice.channel != voice_buzz):
                if roleA.lower() in [roles.name.lower() for roles in member.roles]:
                    await member.move_to(voice_buzz)

        for member in members:
            if (member.voice is not None and member.voice.channel != voice_buzz):
                if roleB.lower() in [roles.name.lower() for roles in member.roles]:
                    await member.move_to(voice_buzz)

    #Changes Perms by removing old team
    if end:
        await ctx.channel.set_permissions(discord.utils.get(roles, name=roleA), send_messages=False, read_messages=False)
        await ctx.channel.set_permissions(discord.utils.get(roles, name=roleB), send_messages=False, read_messages=False, connect=True)
        await voice_buzz.set_permissions(discord.utils.get(roles, name=roleA), send_messages=False, read_messages=False, connect=True)

        if teamC != None and teamD != None :
            await ctx.channel.set_permissions(discord.utils.get(roles, name=roleC), send_messages=True, read_messages=True)
            await ctx.channel.set_permissions(discord.utils.get(roles, name=roleD), send_messages=True, read_messages=True)
    else:
        await ctx.channel.set_permissions(discord.utils.get(roles, name=roleA), send_messages=True, read_messages=True)
        await ctx.channel.set_permissions(discord.utils.get(roles, name=roleB), send_messages=True, read_messages=True)
        await voice_buzz.set_permissions(discord.utils.get(roles, name=roleA), send_messages=True, read_messages=True, connect=True)
        await voice_buzz.set_permissions(discord.utils.get(roles, name=roleB), send_messages=True, read_messages=True, connect=True)
    await ctx.send("Movement Complete")

@bot.command(pass_context=True)
async def syncSheet(ctx):
    await ctx.send("Syncing Sheet")
    while True:

        #Opens the spreadsheet
        sh = gc.open("Role Assignment LOST")
        usernames = sh.sheet1.col_values(3)
        teams = sh.sheet1.col_values(4)
        captains = sh.sheet1.col_values(5)
        roles = ctx.guild.roles
        members = ctx.guild.members

        #for m in members:
        #    if m.nick is not None:
        #        team = re.search(r"\[([A-Za-z0-9_]+)\]", m.nick)


        for i in range(1, len(usernames)):
            ctx.guild.fetch_members()
            if discord.utils.get(ctx.guild.members, name=usernames[i]) is not None:
                user = discord.utils.get(ctx.guild.members, name=usernames[i])
                #Either creates the role and adds person to it or adds the role to the person
                if teams[i].lower() in [y.name.lower() for y in roles] and captains[i] == "Yes":
                    await user.add_roles(discord.utils.get(roles, name="captain"),
                                         discord.utils.get(roles, name=teams[i]))
                    #print("Adding User to team " + teams[i])
                elif teams[i].lower() in [y.name.lower() for y in roles]:
                    await user.add_roles(discord.utils.get(roles, name=teams[i]))
                    #print("Adding User to team " + teams[i])
                if teams[i].lower() not in [y.name.lower() for y in roles] and captains[i] == "Yes":
                    team = await ctx.guild.create_role(name=teams[i])
                    team .hoist = True
                    await user.add_roles(team)
                    #print("Adding User to new team " + teams[i])
                elif teams[i].lower() not in [y.name.lower() for y in roles]:
                    team = await ctx.guild.create_role(name=teams[i])
                    await user.add_roles(team)
                    #print("Adding User to new team " + teams[i])

        time.sleep(120)

bot.run(TOKEN)

