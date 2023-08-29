from serpapi import GoogleSearch
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import datetime

TOKEN: str = ""  # insert your telegram bot token here
BOT_USERNAME: str = ""  # give your bot a name

# initializing variables
areas_dict: dict = {"North": ['Haifa', 'Karmiel', 'Kiryat Bialik', 'Nahariya', "Zikhron Yaakov"],
                    "Sharon": ['Hadera', 'Herzliya', 'Kfar Saba', 'Netanya', 'Raanana', 'Ramat Hasharon'],
                    "Center": ['Holon', 'Kiryat Ono', "Modiin", 'Petah Tikva', 'Ramat Gan', 'Rehovot',
                                        'Rishon Lezion', 'Tel Aviv-Yafo'],
                    "Jerusalem": ["Jerusalem"],
                    "South": ['Ashdod', 'Ashkelon', "Beer Sheva"]}

days_of_week: list[str] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
today: int = datetime.datetime.now().weekday()
days_list: list[str] = [days_of_week[today], days_of_week[(today+1) % 7], days_of_week[(today+2) % 7]]


# main class
class ShowtimesFinder:
    def __init__(self):
        self.film: str = ""
        self.area: str = ""
        self.city: str = ""
        self.day: str = ""

    # finds showtimes based on parameters given to the bots
    def find_showtimes(self) -> str:
        params: dict[str:str] = {
            "q": f"{self.film} showtimes {self.city} {self.day}",
            "gl": "il",
            "hl": "en",
            "google_domain": "google.co.il",
            "api_key": ""  # insert your serpapi key here
        }

        search: GoogleSearch = GoogleSearch(params)
        results: dict[str:any] = search.get_dict()

        showtimes: str = ""
        try:
            showtimes += (f"\nShowtimes for the film {results['knowledge_graph']['title']} in "
                          f"{self.city} on {self.day}:\n")
            for theater in results["showtimes"][0]["theaters"]:
                if float(theater["distance"].split(' ')[0]) < 10:
                    showtimes += f"\n{theater['name']}:\n {theater['showing'][0]['time']}\n"
            showtimes += ("\nTo order:\nPlanet: www.planetcinema.co.il\n"
                          "HOT Cinema: www.hotcinema.co.il\n"
                          "Cinema City: www.cinema-city.co.il\n"
                          "Lev: www.lev.co.il\n"
                          "Rav-Hen: www.rav-hen.co.il\n")
            self.reset_params()
            return showtimes
        except Exception:
            self.reset_params()
            return "something went wrong, please restart"

    # bot response handler
    def handle_response(self, text: str) -> str:
        processed: str = text.title()

        if not self.film:
            self.film = processed
            return f"Which area?\n {list(areas_dict.keys())}"

        elif not self.area:
            self.area = processed
            return f"Which city?\n {list(areas_dict[self.area])}"

        elif not self.city:
            self.city = processed
            return f"What day?\n {list(days_list)}"

        elif not self.day:
            self.day = processed
            return self.find_showtimes()
        else:
            self.reset_params()
            return "something went wrong, please restart"

    # reset class parameters for another run
    def reset_params(self):
        self.film = ""
        self.area = ""
        self.city = ""
        self.day = ""


# start response
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! Please choose a film: ")


# bot message handler
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE, showtimes_object: ShowtimesFinder):
    text: str = update.message.text

    response: str = showtimes_object.handle_response(text)

    await update.message.reply_text(response)


# main
def main():
    app = Application.builder().token(TOKEN).build()
    print("starting")
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(MessageHandler(filters.TEXT, handle_message))
    print("polling")
    app.run_polling(poll_interval=5)


if __name__ == '__main__':
    main()
