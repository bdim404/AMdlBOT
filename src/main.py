# !/usr/bin/env python
# -*- coding: utf-8 -*

from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters
from config import TELEGRAM_BOT_TOKEN, ADMIN_USER_IDS, ALLOWED_TELEGRAM_USER_IDS
from apple_music_checker import AppleMusicChecker
from spotify_downloader import get_url_type
from telegram import Update,Message
from dotenv import load_dotenv
import logging,os,asyncio,re

# Configure the logging;
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Start message handler;
async def handleStartMessage(update, context):
    userId = update.message.from_user.id
    logging.info(f"User {userId} started the bot.")
    if '-' not in ADMIN_USER_IDS and (userId in ADMIN_USER_IDS):
        await update.message.reply_text("Hey boss, I'm ready to serve you :)")
    elif '*' in ALLOWED_TELEGRAM_USER_IDS or userId in ALLOWED_TELEGRAM_USER_IDS:
        await update.message.reply_text("Hello! I'm apple music download bot,send me the link of the song you want to download.")
    else:
        await update.message.reply_text("Sorry, you are not allowed to use this bot, please contact admin to get the permission.")
    return

# Request handler;
async def handleRequest(update: Update, context):
    userId = update.message.from_user.id
    logging.info(f"User {userId} sent a message.")
    if update.message.chat.type == "private":
        if '-' not in ADMIN_USER_IDS and '*' not in ALLOWED_TELEGRAM_USER_IDS and userId not in ADMIN_USER_IDS and userId not in ALLOWED_TELEGRAM_USER_IDS:
            await update.message.reply_text("Sorry, you are not allowed to use this bot, please contact admin to get the permission.")
            return


    # Check if the message is a link including Apple Music;
    if update.message.chat.type == "private":
        if "https://music.apple.com/" in update.message.text :
            downloader = AppleMusicChecker()
            url = re.findall(r'(https?://\S+)', update.message.text)[0]
            await downloader.check_link_type(update, context, url)
        elif "https://open.spotify.com/" in update.message.text:
            url = re.findall(r'(https?://\S+)', update.message.text)[0]
            await get_url_type(update, context, url)
        else:
            logging.info("The message is not a link including Apple Music or Spotify.")
            await update.message.reply_text("Please send me the link of the song from Apple Music or Spotify you want to download.")

async def donate(update: Update, context):
    await update.message.reply_text("You can donate to me at https://ko-fi.com/bdim404.")

async def DownloadSongInGroup(update: Update, context):
    chatId = update.message.chat.id
    logging.info(f"Group {chatId} send a command.")

   # Log the reply_to_message.text and text
    if update.message.reply_to_message:
        logging.info(f"reply_to_message.text: {update.message.reply_to_message.text}")
    logging.info(f"text: {update.message.text}")

    # Check if the message is a link including Apple Music;
    if update.message.reply_to_message and "https://music.apple.com/" in update.message.reply_to_message.text:
        downloader = AppleMusicChecker()
        url = re.findall(r'(https?://\S+)', update.message.reply_to_message.text)[0]
        await downloader.check_link_type(update, context, url)
    elif update.message.reply_to_message and "https://open.spotify.com/" in update.message.reply_to_message.text:
        url = re.findall(r'(https?://\S+)', update.message.reply_to_message.text)[0]
        await get_url_type(update, context, url)
    else:
        logging.info("The message is not a link including Apple Music or Spotify.")
        await update.message.reply_text("Please reply to the message containing the link of the song you want to download, if you don't know how to download a song, send /help.")

async def help(update: Update, context):
    if update.message.chat.type == "private":
        await update.message.reply_text("This bot can download songs from Apple Music and Spotify. Just send the link of the song you want to download.")
    else:
        await update.message.reply_text("This bot can download songs from Apple Music and Spotify. Just reply to the message containing the link of the song you want to download with /download@bot.")

if __name__ == '__main__':
    bot = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    bot.add_handler(CommandHandler("start", handleStartMessage))
    bot.add_handler(CommandHandler("donate", donate))
    bot.add_handler(CommandHandler("download", DownloadSongInGroup))
    bot.add_handler(CommandHandler("help", help))
    bot.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handleRequest))
    bot.run_polling(timeout=60, allowed_updates=Update.ALL_TYPES)
    logging.info("Bot application started")