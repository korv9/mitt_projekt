import requests #hämta grejer från api
import os
from PIL import Image, ImageTk #för att visa bilden
from io import BytesIO #hantera bild data
import tkinter 
from tkinter import font as tkFont
import random
import datetime
import threading


class GUI: #klass för tkinter GUI, 
    def __init__(self) -> None:
        self.root=tkinter.Tk()
        self.root.title("weather app")
        self.root.geometry("800x800")

        weather_font = tkFont.Font(family="Helvetica", size=16, weight="bold")   #fonts för text labels
        wind_font = tkFont.Font(family="Helvetica", size=12, weight="bold")

        self.bg_label = tkinter.Label(self.root) #backgrundsbild label, uppdateras med satelitbilden så den hamnar bakom de andra labelsen
        self.bg_label.place(relwidth=1, relheight=1)

        button_width = 160 
        
        
        self.city_name = tkinter.StringVar() #sparar det man skriver i boxen 
        self.name_entry = tkinter.Entry(self.root,textvariable = self.city_name,  width=20, font=wind_font)
        self.name_entry.place(relx=0.5 , y=550, anchor="center") #centrerar labeln

        
        
         #huvudlabel som skriver ut väderinfo
        self.temperature_label = tkinter.Label(self.root, font=weather_font, fg="black",  text="")
        self.temperature_label.place(relx=0.5, y=100, anchor="center")
        
          #sök-knappen
        self.fetch_button = tkinter.Button(self.root, text="Search city", font=wind_font, command=lambda: self.fetch_weather()) 
        self.fetch_button.place(relx=0.5, y=600, anchor="center", width=button_width)
       
        #random-knappen
        self.random_city_button = tkinter.Button(self.root, text="Random city",font=wind_font, command=lambda: self.fetch_random_city_weather())
        self.random_city_button.place(relx=0.5, y=650, anchor="center", width=button_width)
        
        
    def fetch_weather(self): #funktionen som kallar på väder och bild funktionerna
        self.fetch_button.config(state=tkinter.DISABLED) #stänger av knappen medans det laddar
        city_name =self.city_name.get()
        city = City(city_name, self)
        city.get_weather()
        city.get_picture()
        self.fetch_button.config(state=tkinter.NORMAL) #startar knappen igen
       
        
    def fetch_random_city_weather(self): #funktion för att hämta random stad från lista
        self.random_city_button.config(state=tkinter.DISABLED)
        cities_file_path = "cities_list.txt"
        
        if os.path.exists(cities_file_path): #kollar om filen finns
            
            with open(cities_file_path, "r") as city_file:
                    cities = city_file.read().splitlines()
            
            if cities: #om listan inte är tom
                random_city = random.choice(cities) #väljer random stad
                city = City(random_city, self)
                city.get_weather() 
                city.get_picture()
        self.random_city_button.config(state=tkinter.NORMAL)


class Weather_API: #klass för att samla API 
    
        
         
    def get_weather_api(city_name):# hämtar info och skriver ut väder
        
        url = f"http://api.weatherapi.com/v1/current.json?key={API_key_weather}&q={city_name}" # skickar in API nyckeln i url samt stadens namn

        
        response = requests.get(url).json()
        return response

    def get_satellite_image_api(lat, lon, date):
        url_nasa = f"https://api.nasa.gov/planetary/earth/imagery?lon={lon}&lat={lat}&date={date}&dim=0.09&api_key={API_key_nasa}" # skickar in koordinater samt datum för att få en bild av staden
        response_nasa = requests.get(url_nasa)
        return response_nasa 



class City: #klass för att strukturera upp väderdatan stad för stad
    def __init__(self,name, gui) -> None:
        self.name = name
        self.gui = gui
        
 
    def save_city(self): #funktion att spara städer för att sen randomizea 
        cities_file_path = "cities_list.txt"
          
        if not os.path.exists(cities_file_path): #skapar fil om den inte finns
          open(cities_file_path, 'w').close()
          
        with open(cities_file_path, "r+") as city_file: 
            cities = city_file.read().splitlines() # delar upp efter raderna
            if self.name not in cities: # för att kolla så att inte en stad redan är skriven 
                city_file.write(f"{self.name}\n")
    
    
    


    
    
    def get_weather(self):# hämtar info och skriver ut väder
        
        

        try:
                
                response = Weather_API.get_weather_api(self.name)
                
                
                if "error" in response: # det kan bli error trots statuscode 200, om den inte hittar angivna staden
                    self.gui.weather_label.config(text="Could not recognize city name!") 
                else:
                   #fångar värden från response i variabler
                    temp = response["current"]["temp_c"]
                    weather = response["current"]["condition"]["text"]
                    wind_kph = response["current"]["wind_kph"]
                    wind_direction = response["current"]["wind_dir"]
                    
                    # för att skriva om riktning av vinden
                    wind_direction_map = {
                        "NW": "North West",
                        "SW": "South West",
                        "W": "West",
                        "E": "East",
                        "SE": "South East",
                        "NE": "North East",
                        "S": "South",
                        "N": "North"
                        
                    }
                    wind_direction = wind_direction_map.get(wind_direction,wind_direction)
                    wind_per_second = wind_kph /3.6
                    
                    
                    
                    
                    self.latitude = response["location"]["lat"]
                    self.longitude = response["location"]["lon"]
                    self.country = response["location"]["country"]
                    
                    
                    
                    #skriver ut till textlabels
                    self.gui.temperature_label.config(text=f" {self.name}, {self.country}\n TEMP:{temp}C\nWEATHER: {weather}\n WINDS:{wind_per_second:.2f}m/s {wind_direction}")
                    
                    
                    
    
        except Exception as e:
                
                print(f"nåt gick fel {e}")
    
     
    def get_picture(self):
         
         datum = datetime.date.today()
          
         
         def fetch_image():
            try:
                response_nasa = Weather_API.get_satellite_image_api(self.latitude,self.longitude, datum)
                
                
                if response_nasa.status_code == 200: #IF sats för att se om API har hämtats rätt
                
                    
                    
                    # tar satellit bilden och öppnar bilden 
                    image = Image.open(BytesIO(response_nasa.content))
                    
                    image = image.resize((800, 800),)# minskar storleken på bilden
                    img_tk = ImageTk.PhotoImage(image) # konverterar bilden med photoimage så den kommer fram i tkinter

                    #tkinter label för bilden
                    
                    
                    self.gui.bg_label.config(image=img_tk)
                    self.gui.bg_label.image = img_tk

                    self.save_city() #sparar staden efter att ha lyckats gå igenom alla funktioner

                else:
                    self.gui.weather_label.config(text="Failed to fetch satellite image.")

            except Exception as e:
             print(f"Something went wrong with the image: {e}")
             self.gui.temperature_label.config(text=f"Error fetching image data for {self.name}.")
         
         threading.Thread(target=fetch_image).start() #threadar funktionen så programmet inte hakar upp sig när bilden hämtas



with open("api_key.txt","r") as API_file:   #öppnar API_key filen o läser de två nycklarna
             API_keys = API_file.readlines()
             API_keys = [key.strip() for key in API_keys]  # tar bort tomrum 
             API_key_weather = API_keys[0] # läser rad 1 som är API nyckeln till openweater
             API_key_nasa = API_keys[1] # läser rad 2 som är API nyckeln till nasa


if __name__ == "__main__": #startar hela GUI-loopen
    gui = GUI()

    gui.root.mainloop()
