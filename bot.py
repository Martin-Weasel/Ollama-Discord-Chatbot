import discord
import ollama
import logging
import customtkinter as ctk
from discord.ext import commands
from customtkinter import *
from tkinter import *
from tkinter import messagebox
from PIL import Image

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
            username = str(message.author).split('#')[0]
            user_message = str(message.content)

            if message.author == bot.user:
                return

            if bot.user.mentioned_in(message):
                
                user_id = f"{message.guild.id}-{message.author.id}" # makes user_id
                if user_id not in context_window:                   # checks if user_id is in context window
                    context_window[user_id] = []                    # adds it to nested list

                command = message.content.replace(f'<@!{bot.user.id}>', '').strip()
                
                context_window[user_id].append(f"{username} : {user_message}") # appends current conversation to context window under user_id
                
                prompt = "\n".join(context_window[user_id])         # sets the list inside the string

                response = ollama.generate(model=self.MODEL_NAME, prompt=prompt)
                context_window[user_id].append(f"{bot.user.name} : {response['response']}")

                await message.channel.send(response["response"])

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
            messagebox.showerror("Error", "Please enter the name of the Model e.g llama2 !")
        else:
            Discord_bot(self.DISCORD_BOT_TOKEN, self.MODEL_NAME)
        
if __name__ == "__main__":
    GUI()
