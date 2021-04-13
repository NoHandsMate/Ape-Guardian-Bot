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
    
    """ Ripete un messaggio """
    
    if len(args) == 0:
        await ctx.send('You must provide some words!')
    else:
        await ctx.send('{}'.format(' '.join(args)))

@bot.command()
async def git(ctx):
    
    """ Un comando che permette di avere il link per tutte le cose da fare sul bot"""
    
    await ctx.send('Ecco il link per la lista di tutte le cose da fare')
    await ctx.send('https://github.com/NoHandsMate/Ape-Guardian-Bot/projects/1')

