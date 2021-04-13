from discord.ext import commands


bot = commands.Bot(command_prefix='$')

@bot.listen()
async def on_message(message):
    if message.author == bot.user:
        return
    if message.content.startswith('$'):
        print('From {0.author}: {0.content}'.format(message))

@bot.listen()
async def on_ready():
    print('Bot is online and ready to go')


# From here handle all the commands

@bot.command()
async def echo(ctx, *args):    # ctx = Context 
    if len(args) == 0:
        await ctx.send('You must provide some words!')
    else:
        await ctx.send('{}'.format(' '.join(args)))

@bot.command()
async def git(ctx):
   await ctx.send('Ecco il link per la lista di tutte le cose da fare')
   await ctx.send('https://github.com/NoHandsMate/Ape-Guardian-Bot/projects/1')

@bot.command()
async def aiuto(ctx):           # Help command that shows all the command avaible
   await ctx.send('\
                   Ecco la lista di tutti i comandi: \n\
                   $help: mostra questa lista\n\
                   $echo ... : ripete tutte le parole scritte dopo echo\n\
                   $git: mostra il link per la lista di tutte le cose da fare\n\
                   Musica:\n\
                   $play ... : cerca e riproduce un video da yt con delle parole-chiave o un url \n\
                   $stop: ferma la riproduzione\n\
                   $volume 0-300: aggiusta il volume\n\
                   $yt ... : cerca e scarica un video da yt con delle parole-chiave o url')

