import discord
import ollama
import logging
import customtkinter as ctk
from discord.ext import commands
from customtkinter import *
from tkinter import *
from tkinter import messagebox
from PIL import Image

SYSTEM_PROMPT = "User's nickname is \"%n\" and it is case-sensitive!"
context_window = {} # creating a dictionary for context window
# This dictionary will follow this format
# {"user_id" : [list of messages]}
# user_id is a compound id consisting of current guild id and current author id

class Discord_bot:
    def __init__(self, bot_token, model_name):
        self.DISCORD_BOT_TOKEN = bot_token
        self.MODEL_NAME = model_name

        logging.basicConfig(filename='log.txt', level=logging.INFO, format='[%(asctime)s] [%(levelname)s] %(message)s')

        intents = discord.Intents.default()
        intents.messages = True

        bot = commands.Bot(command_prefix='@Chat ', intents=intents)

        @bot.event
        async def on_ready():
            print(f'We have logged in as {bot.user.name}')

        @bot.event
        async def on_message(message):
            username = message.author.display_name                                                  # get the username of the author

            if message.author == bot.user: return

            if bot.user.mentioned_in(message):
                user_id = f"{message.guild.id}-{message.channel.id}-{message.author.id}"            # form the user_id
                if user_id not in context_window:                                                   # check if user_id is in context window
                    context_window[user_id] = []                                                    # add user into context window
                    system_prompt = SYSTEM_PROMPT.replace('%n', username)                           # form the system prompt
                    context_window[user_id].append({'role': 'system', 'content': system_prompt})    # append the system prompt to the context window

                plain_message = message.content.replace(f'<@{bot.user.id}>', '').strip()            # remove the mention and strip the message
                
                context_window[user_id].append({'role': 'user', 'content': plain_message})          # append user's message to the context window

                response = ollama.chat(model=self.MODEL_NAME, messages=context_window[user_id])     # generate response based on the context
                context_window[user_id].append(response['message'])                                 # append assistant's message to the context window
                
                response_message = f"<@{message.author.id}> {response['message']['content']}"       # form the response message and tag the user
                await message.channel.send(response_message)                                        # send the message content to the channel
                
            await bot.process_commands(message)

        bot.run(self.DISCORD_BOT_TOKEN)

class GUI:
    def __init__(self):
        app = ctk.CTk()
        app.title("Discord Chatbot")
        app.geometry("700x500")
        ctk.set_appearance_mode("dark")

        image_frame = ctk.CTkFrame(app, width=325, height=650)
        image_frame.place(x=0, y=0)

        background_image = ctk.CTkImage(Image.open("discord.jpg"),size=(325, 650))

        background_image_label = ctk.CTkLabel(image_frame, image=background_image, text="")
        background_image_label.grid(row=0, column=0)

        bot_token_label = ctk.CTkLabel(app, text="Discord Bot\n\n", text_color="white", font=("Arial", 50), justify="center")
        bot_token_label.place(x=360, y=50)

        self.bot_token_entry = ctk.CTkEntry(app, placeholder_text="Enter your bot token here...", width=300, height=50)
        self.bot_token_entry.place(x=360, y=140)

        self.model_name_entry = ctk.CTkEntry(app, placeholder_text="Enter the name of the model here e.g llama2", width=300, height=50)
        self.model_name_entry.place(x=360, y=220)

        start_button = ctk.CTkButton(app, text="Start Bot", width=150, height=50, command=self.start_bot)
        start_button.place(x=360, y=300)
        
        app.mainloop()
        
    def start_bot(self):
        self.DISCORD_BOT_TOKEN = self.bot_token_entry.get()
        self.MODEL_NAME = self.model_name_entry.get()
        if self.DISCORD_BOT_TOKEN == "":
            messagebox.showerror("Error", "Please enter your BOT Token!")
        elif self.MODEL_NAME == "":
            messagebox.showerror("Error", "Please enter the name of the Model e.g llama3.1:8b !")
        else:
            Discord_bot(self.DISCORD_BOT_TOKEN, self.MODEL_NAME)
        
if __name__ == "__main__":
    GUI()