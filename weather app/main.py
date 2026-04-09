#!/usr/bin/env python3
"""
Weather Tracking Dashboard with History Storage
Complete weather application with realtime API fetching, history storage,
and advanced visualization features.
No hyphens or underscores used in code identifiers.
"""

import json
import csv
import os
import sys
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, simpledialog
import requests
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import matplotlib.dates as mdates


class APIConfiguration:
    """Centralized configuration for API endpoints and settings."""

    BASEURL = "https://api.openweathermap.org/data/2.5"
    GEOURL = "https://api.openweathermap.org/geo/1.0"
    TIMEOUT = 10
    UNITS = "metric"

    def __init__(self, apikey: str):
        self.apikey = apikey


class WeatherDataFetcher:
    """Handles all API interactions for weather data retrieval."""

    def __init__(self, config: APIConfiguration):
        self.config = config
        self.cache = {}
        self.cachetimeout = 300

    def fetchcurrentweather(self, city: str, forcefresh: bool = False) -> Optional[Dict[str, Any]]:
        """Fetch current weather data for a given city."""
        cachekey = f"current_{city.lower()}"
        if not forcefresh and cachekey in self.cache:
            cacheddata, cachetime = self.cache[cachekey]
            if (datetime.now() - cachetime).seconds < self.cachetimeout:
                cacheddata["fromcache"] = True
                return cacheddata

        try:
            coordinates = self.fetchcitycoordinates(city)
            if not coordinates:
                return None

            params = self.buildweatherparams(coordinates)
            response = self.makeapirequest(f"{self.config.BASEURL}/weather", params)

            if not response:
                return None

            weatherdata = self.parsecurrentweatherresponse(response, city, coordinates)
            weatherdata["fromcache"] = False
            weatherdata["realtime"] = True

            self.cache[cachekey] = (weatherdata.copy(), datetime.now())

            return weatherdata

        except Exception as e:
            print(f"Error: Unexpected error in fetchcurrentweather: {e}")
            return None

    def buildweatherparams(self, coordinates: Dict[str, Any]) -> Dict[str, Any]:
        """Build parameters for weather API request."""
        return {
            "lat": coordinates["lat"],
            "lon": coordinates["lon"],
            "appid": self.config.apikey,
            "units": self.config.UNITS
        }

    def makeapirequest(self, url: str, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Make HTTP request to API with error handling."""
        try:
            response = requests.get(url, params=params, timeout=self.config.TIMEOUT)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.Timeout:
            print("Error: Connection timeout while fetching weather data")
        except requests.exceptions.ConnectionError:
            print("Error: Failed to connect to weather service")
        except requests.exceptions.HTTPError as e:
            print(f"Error: HTTP error occurred: {e}")
        except Exception as e:
            print(f"Error: API request failed: {e}")
        return None

    def parsecurrentweatherresponse(self, data: Dict[str, Any], city: str,
                                    coordinates: Dict[str, Any]) -> Dict[str, Any]:
        """Parse and structure current weather API response."""
        return {
            "city": city.title(),
            "temperature": data["main"]["temp"],
            "feelslike": data["main"]["feels_like"],
            "humidity": data["main"]["humidity"],
            "pressure": data["main"]["pressure"],
            "windspeed": data["wind"]["speed"],
            "winddirection": data["wind"].get("deg", 0),
            "weatherdescription": data["weather"][0]["description"].capitalize(),
            "weathermain": data["weather"][0]["main"],
            "icon": data["weather"][0]["icon"],
            "timestamp": datetime.now().isoformat(),
            "country": coordinates.get("country", ""),
            "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).isoformat(),
            "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).isoformat(),
            "visibility": data.get("visibility", 0) / 1000,
            "cloudcover": data["clouds"]["all"]
        }

    def fetchcitycoordinates(self, city: str) -> Optional[Dict[str, Any]]:
        """Get geographic coordinates for a city name."""
        try:
            params = {
                "q": city,
                "limit": 1,
                "appid": self.config.apikey
            }

            response = self.makeapirequest(f"{self.config.GEOURL}/direct", params)

            if not response or len(response) == 0:
                print(f"Error: City '{city}' not found")
                return None

            return {
                "lat": response[0]["lat"],
                "lon": response[0]["lon"],
                "country": response[0].get("country", ""),
                "state": response[0].get("state", "")
            }
        except Exception as e:
            print(f"Error fetching coordinates: {e}")
            return None

    def fetchforecast(self, city: str, days: int = 5) -> Optional[List[Dict[str, Any]]]:
        """Fetch weather forecast for the next specified days."""
        try:
            coordinates = self.fetchcitycoordinates(city)
            if not coordinates:
                return None

            params = {
                "lat": coordinates["lat"],
                "lon": coordinates["lon"],
                "appid": self.config.apikey,
                "units": self.config.UNITS,
                "cnt": 40
            }

            response = self.makeapirequest(f"{self.config.BASEURL}/forecast", params)

            if not response:
                return None

            return self.parseforecastresponse(response, days)

        except Exception as e:
            print(f"Error fetching forecast: {e}")
            return None

    def parseforecastresponse(self, data: Dict[str, Any], requesteddays: int) -> List[Dict[str, Any]]:
        """Parse and structure forecast API response, limiting to requested days."""
        forecastdata = []

        today = datetime.now().date()
        maxdate = today + timedelta(days=requesteddays)

        for item in data["list"]:
            forecasttime = datetime.strptime(item["dt_txt"], "%Y-%m-%d %H:%M:%S")
            forecastdate = forecasttime.date()

            if today <= forecastdate < maxdate:
                forecastdata.append({
                    "timestamp": item["dt_txt"],
                    "temperature": item["main"]["temp"],
                    "feelslike": item["main"]["feels_like"],
                    "humidity": item["main"]["humidity"],
                    "windspeed": item["wind"]["speed"],
                    "weatherdescription": item["weather"][0]["description"].capitalize(),
                    "weathermain": item["weather"][0]["main"],
                    "icon": item["weather"][0]["icon"],
                    "probability": item.get("pop", 0) * 100,
                    "cloudcover": item["clouds"]["all"]
                })

        return forecastdata

    def clearcache(self):
        """Clear the API response cache."""
        self.cache.clear()


class WeatherHistoryManager:
    """Manages storage and retrieval of weather query history."""

    def __init__(self, storagefile: str = "weatherhistory.json"):
        self.storagefile = storagefile
        self.history = self.loadhistoryfromfile()

    def loadhistoryfromfile(self) -> List[Dict[str, Any]]:
        """Load history from JSON file."""
        try:
            if os.path.exists(self.storagefile):
                with open(self.storagefile, 'r', encoding='utf-8') as file:
                    return json.load(file)
            return []
        except Exception as e:
            print(f"Error loading history: {e}")
            return []

    def savehistorytofile(self) -> bool:
        """Save history to JSON file."""
        try:
            with open(self.storagefile, 'w', encoding='utf-8') as file:
                json.dump(self.history, file, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving history: {e}")
            return False

    def addentry(self, weatherdata: Dict[str, Any]) -> None:
        """Add a new weather query to history."""
        entry = self.createhistoryentry(weatherdata)
        self.history.append(entry)
        self.savehistorytofile()

    def createhistoryentry(self, weatherdata: Dict[str, Any]) -> Dict[str, Any]:
        """Create a history entry from weather data."""
        return {
            "id": len(self.history) + 1,
            "querytimestamp": datetime.now().isoformat(),
            "city": weatherdata["city"],
            "temperature": weatherdata["temperature"],
            "humidity": weatherdata["humidity"],
            "windspeed": weatherdata["windspeed"],
            "weatherdescription": weatherdata["weatherdescription"],
            "weathermain": weatherdata["weathermain"],
            "country": weatherdata.get("country", ""),
            "feelslike": weatherdata.get("feelslike"),
            "pressure": weatherdata.get("pressure")
        }

    def getallhistory(self, sortbydate: bool = True) -> List[Dict[str, Any]]:
        """Retrieve all history entries, optionally sorted by date."""
        if sortbydate:
            return sorted(
                self.history,
                key=lambda x: x["querytimestamp"],
                reverse=True
            )
        return self.history

    def gethistorybycity(self, city: str) -> List[Dict[str, Any]]:
        """Retrieve history entries for a specific city (case insensitive)."""
        citylower = city.lower()
        return [
            entry for entry in self.history
            if entry["city"].lower() == citylower
        ]

    def getpaginatedhistory(self, page: int = 1, pagesize: int = 10) -> Tuple[List[Dict[str, Any]], int]:
        """Get paginated history entries."""
        sortedhistory = self.getallhistory()
        totalpages = (len(sortedhistory) + pagesize - 1) // pagesize
        startidx = (page - 1) * pagesize
        endidx = startidx + pagesize
        return sortedhistory[startidx:endidx], totalpages

    def exporttocsv(self, filename: str = "weatherhistoryexport.csv") -> bool:
        """Export history to CSV file."""
        try:
            if not self.history:
                return False

            fieldnames = self.getcsvfieldnames()

            with open(filename, 'w', newline='', encoding='utf-8') as file:
                writer = csv.DictWriter(file, fieldnames=fieldnames)
                writer.writeheader()

                for entry in self.history:
                    row = {field: entry.get(field, "") for field in fieldnames}
                    writer.writerow(row)

            return True
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            return False

    def getcsvfieldnames(self) -> List[str]:
        """Get field names for CSV export."""
        return [
            "id", "querytimestamp", "city", "country", "temperature",
            "feelslike", "humidity", "pressure", "windspeed",
            "weatherdescription", "weathermain"
        ]

    def clearhistory(self) -> None:
        """Clear all history entries."""
        self.history = []
        self.savehistorytofile()

    def searchhistory(self, searchterm: str) -> List[Dict[str, Any]]:
        """Search history entries by city or weather description."""
        searchtermlower = searchterm.lower()
        results = []

        for entry in self.history:
            if self.matchessearchterm(entry, searchtermlower):
                results.append(entry)

        return results

    def matchessearchterm(self, entry: Dict[str, Any], searchtermlower: str) -> bool:
        """Check if entry matches search term."""
        return (searchtermlower in entry["city"].lower() or
                searchtermlower in entry["weatherdescription"].lower() or
                searchtermlower in entry["weathermain"].lower())


class WeatherAlertManager:
    """Manages weather alerts and notifications."""

    def __init__(self):
        self.alertthresholds = self.getdefaultthresholds()
        self.alerthistory = []

    def getdefaultthresholds(self) -> Dict[str, Any]:
        """Get default alert thresholds."""
        return {
            "hightemperature": 35.0,
            "lowtemperature": 0.0,
            "highwind": 50.0,
            "severeconditions": ["Thunderstorm", "Tornado", "Hurricane"]
        }

    def checksevereweather(self, weatherdata: Dict[str, Any]) -> List[str]:
        """Check for severe weather conditions and return alerts."""
        alerts = []

        alerts.extend(self.checktemperaturealerts(weatherdata))
        alerts.extend(self.checkwindalerts(weatherdata))
        alerts.extend(self.checkconditionalealerts(weatherdata))

        if alerts:
            self.alerthistory.append({
                "timestamp": datetime.now().isoformat(),
                "city": weatherdata["city"],
                "alerts": alerts.copy()
            })

        return alerts

    def checktemperaturealerts(self, weatherdata: Dict[str, Any]) -> List[str]:
        """Check temperature-related alerts."""
        alerts = []

        if weatherdata["temperature"] > self.alertthresholds["hightemperature"]:
            alerts.append(f"High temperature alert: {weatherdata['temperature']:.1f}°C")

        if weatherdata["temperature"] < self.alertthresholds["lowtemperature"]:
            alerts.append(f"Low temperature alert: {weatherdata['temperature']:.1f}°C")

        return alerts

    def checkwindalerts(self, weatherdata: Dict[str, Any]) -> List[str]:
        """Check wind-related alerts."""
        alerts = []

        if weatherdata["windspeed"] > self.alertthresholds["highwind"]:
            alerts.append(f"High wind alert: {weatherdata['windspeed']:.1f} m/s")

        return alerts

    def checkconditionalealerts(self, weatherdata: Dict[str, Any]) -> List[str]:
        """Check weather condition alerts."""
        alerts = []

        if weatherdata["weathermain"] in self.alertthresholds["severeconditions"]:
            alerts.append(f"Severe weather alert: {weatherdata['weathermain']}")

        return alerts


class WeatherDashboardGUI:
    """Main GUI application for Weather Tracking Dashboard."""

    def __init__(self, apikey: str):
        self.initializecomponents(apikey)
        self.setupmainwindow()
        self.setupmenu()

    def initializecomponents(self, apikey: str):
        """Initialize all components and managers."""
        config = APIConfiguration(apikey)
        self.fetcher = WeatherDataFetcher(config)
        self.historymanager = WeatherHistoryManager()
        self.alertmanager = WeatherAlertManager()

    def setupmainwindow(self):
        """Setup the main application window."""
        self.root = tk.Tk()
        self.root.title("Weather Tracking Dashboard")
        self.root.geometry("1200x800")

        self.initializevariables()
        self.setupui()
        self.setupstatusbar()

    def initializevariables(self):
        """Initialize tkinter variables."""
        self.autoupdaterunning = False
        self.autoupdatethread = None
        self.currentcity = tk.StringVar()
        self.updateinterval = tk.IntVar(value=30)
        self.currenthistorypage = 1

    def setupstatusbar(self):
        """Setup the status bar."""
        self.statusbar = ttk.Label(
            self.root,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

    def setupui(self):
        """Setup the main UI components."""
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=5, pady=5)

        self.createtabs()

    def createtabs(self):
        """Create all application tabs."""
        self.createweathertab()
        self.createforecasttab()
        self.createhistorytab()
        self.createanalyticstab()

    def createweathertab(self):
        """Create the current weather tab."""
        self.weatherframe = ttk.Frame(self.notebook)
        self.notebook.add(self.weatherframe, text="Current Weather")
        self.setupweathertab()

    def createforecasttab(self):
        """Create the forecast tab."""
        self.forecastframe = ttk.Frame(self.notebook)
        self.notebook.add(self.forecastframe, text="Forecast")
        self.setupforecasttab()

    def createhistorytab(self):
        """Create the history tab."""
        self.historyframe = ttk.Frame(self.notebook)
        self.notebook.add(self.historyframe, text="History")
        self.setuphistorytab()

    def createanalyticstab(self):
        """Create the analytics tab."""
        self.analyticsframe = ttk.Frame(self.notebook)
        self.notebook.add(self.analyticsframe, text="Analytics")
        self.setupanalyticstab()

    def setupmenu(self):
        """Setup application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        self.createfilemenu(menubar)
        self.createtoolsmenu(menubar)
        self.createautomenu(menubar)
        self.createhelpmenu(menubar)

    def createfilemenu(self, menubar: tk.Menu):
        """Create file menu."""
        filemenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=filemenu)
        filemenu.add_command(label="Export History to CSV", command=self.exporthistory)
        filemenu.add_command(label="Clear History", command=self.clearhistorydialog)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=self.root.quit)

    def createtoolsmenu(self, menubar: tk.Menu):
        """Create tools menu."""
        toolsmenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Tools", menu=toolsmenu)
        toolsmenu.add_command(label="Set Alert Thresholds", command=self.setthresholdsdialog)

    def createautomenu(self, menubar: tk.Menu):
        """Create auto update menu."""
        automenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Auto Update", menu=automenu)
        automenu.add_command(label="Start Auto Update", command=self.startautoupdate)
        automenu.add_command(label="Stop Auto Update", command=self.stopautoupdate)
        automenu.add_separator()
        automenu.add_command(label="Set Update Interval", command=self.setupdateintervaldialog)

    def createhelpmenu(self, menubar: tk.Menu):
        """Create help menu."""
        helpmenu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=helpmenu)
        helpmenu.add_command(label="About", command=self.showabout)

    def setupweathertab(self):
        """Setup the current weather tab UI."""
        self.createsearchframe()
        self.createweatherdisplayframe()

    def createsearchframe(self):
        """Create search frame for weather tab."""
        searchframe = ttk.LabelFrame(self.weatherframe, text="Search Location", padding=10)
        searchframe.pack(fill="x", padx=10, pady=5)

        ttk.Label(searchframe, text="City:").grid(row=0, column=0, padx=5)
        self.cityentry = ttk.Entry(searchframe, width=30, textvariable=self.currentcity)
        self.cityentry.grid(row=0, column=1, padx=5)
        self.cityentry.bind("<Return>", lambda e: self.fetchanddisplayweather())

        ttk.Button(
            searchframe,
            text="Get Weather",
            command=self.fetchanddisplayweather
        ).grid(row=0, column=2, padx=5)

    def createweatherdisplayframe(self):
        """Create weather display frame."""
        self.weatherdisplay = ttk.LabelFrame(self.weatherframe, text="Current Weather", padding=10)
        self.weatherdisplay.pack(fill="both", expand=True, padx=10, pady=5)

        self.weatherlabels = {}
        self.createweatherlabels()

    def createweatherlabels(self):
        """Create weather information labels."""
        labeltexts = [
            "City", "Country", "Temperature", "Feels Like", "Humidity",
            "Pressure", "Wind Speed", "Wind Direction", "Weather Description",
            "Visibility", "Cloud Cover", "Sunrise", "Sunset", "Last Updated"
        ]

        for i, text in enumerate(labeltexts):
            ttk.Label(self.weatherdisplay, text=f"{text}:", font=("Arial", 10, "bold")).grid(
                row=i, column=0, sticky="w", padx=5, pady=2
            )
            key = text.lower().replace(" ", "")
            self.weatherlabels[key] = ttk.Label(
                self.weatherdisplay, text="", font=("Arial", 10)
            )
            self.weatherlabels[key].grid(
                row=i, column=1, sticky="w", padx=5, pady=2
            )

    def setupforecasttab(self):
        """Setup the forecast tab UI."""
        self.createforecastcontrols()
        self.createforecastdisplay()

    def createforecastcontrols(self):
        """Create forecast control elements."""
        controlframe = ttk.Frame(self.forecastframe)
        controlframe.pack(fill="x", padx=10, pady=5)

        ttk.Label(controlframe, text="City:").pack(side="left", padx=5)
        self.forecastcityentry = ttk.Entry(controlframe, width=30)
        self.forecastcityentry.pack(side="left", padx=5)

        ttk.Label(controlframe, text="Days (1-5):").pack(side="left", padx=5)
        self.forecastdays = ttk.Spinbox(controlframe, from_=1, to=5, width=5)
        self.forecastdays.pack(side="left", padx=5)
        self.forecastdays.set(3)

        ttk.Button(
            controlframe,
            text="Get Forecast",
            command=self.fetchanddisplayforecast
        ).pack(side="left", padx=5)

    def createforecastdisplay(self):
        """Create forecast display area."""
        self.forecasttext = scrolledtext.ScrolledText(
            self.forecastframe,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Courier", 10)
        )
        self.forecasttext.pack(fill="both", expand=True, padx=10, pady=5)

    def setuphistorytab(self):
        """Setup the history tab UI."""
        self.createhistorycontrols()
        self.createhistorytree()

    def createhistorycontrols(self):
        """Create history control elements."""
        controlframe = ttk.Frame(self.historyframe)
        controlframe.pack(fill="x", padx=10, pady=5)

        self.createhistorysearchelements(controlframe)
        self.createhistorypaginationelements(controlframe)

    def createhistorysearchelements(self, parent: ttk.Frame):
        """Create history search elements."""
        ttk.Label(parent, text="Search:").pack(side="left", padx=5)
        self.historysearch = ttk.Entry(parent, width=30)
        self.historysearch.pack(side="left", padx=5)
        self.historysearch.bind("<KeyRelease>", self.filterhistory)

        ttk.Button(
            parent,
            text="Refresh",
            command=self.refreshhistorydisplay
        ).pack(side="left", padx=5)

    def createhistorypaginationelements(self, parent: ttk.Frame):
        """Create history pagination elements."""
        self.pagelabel = ttk.Label(parent, text="Page 1 of 1")
        self.pagelabel.pack(side="right", padx=5)

        ttk.Button(
            parent,
            text="Next",
            command=self.nexthistorypage
        ).pack(side="right", padx=2)

        ttk.Button(
            parent,
            text="Previous",
            command=self.prevhistorypage
        ).pack(side="right", padx=2)

    def createhistorytree(self):
        """Create history treeview widget."""
        treeframe = ttk.Frame(self.historyframe)
        treeframe.pack(fill="both", expand=True, padx=10, pady=5)

        columns = ("ID", "Timestamp", "City", "Temp (C)", "Humidity (%)", "Wind (m/s)", "Description")
        self.historytree = ttk.Treeview(treeframe, columns=columns, show="headings", height=20)

        self.configurehistorycolumns(columns)

        scrollbar = ttk.Scrollbar(treeframe, orient="vertical", command=self.historytree.yview)
        self.historytree.configure(yscrollcommand=scrollbar.set)

        self.historytree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.historytree.bind("<Double-1>", self.showhistorydetails)
        self.refreshhistorydisplay()

    def configurehistorycolumns(self, columns: Tuple[str, ...]):
        """Configure history treeview columns."""
        widths = [50, 150, 100, 80, 80, 80, 150]
        for col, width in zip(columns, widths):
            self.historytree.heading(col, text=col)
            self.historytree.column(col, width=width)

    def setupanalyticstab(self):
        """Setup the analytics tab UI."""
        self.createanalyticscontrols()
        self.creategraphframe()

    def createanalyticscontrols(self):
        """Create analytics control elements."""
        controlframe = ttk.Frame(self.analyticsframe)
        controlframe.pack(fill="x", padx=10, pady=5)

        ttk.Label(controlframe, text="City:").pack(side="left", padx=5)
        self.analyticscity = ttk.Entry(controlframe, width=20)
        self.analyticscity.pack(side="left", padx=5)

        self.creategraphbuttons(controlframe)

    def creategraphbuttons(self, parent: ttk.Frame):
        """Create graph generation buttons."""
        ttk.Button(
            parent,
            text="Temperature Graph",
            command=self.generatetemperaturegraph
        ).pack(side="left", padx=5)

        ttk.Button(
            parent,
            text="Wind Graph",
            command=self.generatewindgraph
        ).pack(side="left", padx=5)

        ttk.Button(
            parent,
            text="Humidity Graph",
            command=self.generatehumiditygraph
        ).pack(side="left", padx=5)

    def creategraphframe(self):
        """Create frame for displaying graphs."""
        self.graphframe = ttk.Frame(self.analyticsframe)
        self.graphframe.pack(fill="both", expand=True, padx=10, pady=5)

    def fetchanddisplayweather(self):
        """Fetch and display current weather."""
        city = self.cityentry.get().strip()
        if not city:
            messagebox.showwarning("Input Required", "Please enter a city name")
            return

        self.updatestatus(f"Fetching weather for {city}...")
        weatherdata = self.fetcher.fetchcurrentweather(city, forcefresh=True)

        if weatherdata:
            self.processweatherdata(weatherdata)
        else:
            messagebox.showerror("Error", f"Could not fetch weather data for {city}")
            self.updatestatus("Ready")

    def processweatherdata(self, weatherdata: Dict[str, Any]):
        """Process and display weather data."""
        self.displayweatherdata(weatherdata)
        self.historymanager.addentry(weatherdata)
        self.checkanddisplayalerts(weatherdata)
        self.updatestatus(f"Weather for {weatherdata['city']} updated successfully")

    def checkanddisplayalerts(self, weatherdata: Dict[str, Any]):
        """Check for and display weather alerts."""
        alerts = self.alertmanager.checksevereweather(weatherdata)
        if alerts:
            alertmsg = "\n".join(alerts)
            messagebox.showwarning("Weather Alert", f"Severe weather conditions detected:\n\n{alertmsg}")

    def displayweatherdata(self, data: Dict[str, Any]):
        """Display weather data in the UI."""
        self.displaybasicweatherinfo(data)
        self.displaytimedata(data)
        self.displaymiscdata(data)

    def displaybasicweatherinfo(self, data: Dict[str, Any]):
        """Display basic weather information."""
        self.weatherlabels["city"].config(text=data.get("city", "N/A"))
        self.weatherlabels["country"].config(text=data.get("country", "N/A"))
        self.weatherlabels["temperature"].config(text=f"{data.get('temperature', 0):.1f}°C")
        self.weatherlabels["feelslike"].config(text=f"{data.get('feelslike', 0):.1f}°C")
        self.weatherlabels["humidity"].config(text=f"{data.get('humidity', 0)}%")
        self.weatherlabels["pressure"].config(text=f"{data.get('pressure', 0)} hPa")

    def displaytimedata(self, data: Dict[str, Any]):
        """Display time-related weather information."""
        sunrise = data.get("sunrise", "")
        sunset = data.get("sunset", "")
        if sunrise and sunset:
            if isinstance(sunrise, datetime):
                sunrisetime = sunrise.strftime("%H:%M:%S")
                sunsettime = sunset.strftime("%H:%M:%S")
            else:
                sunrisetime = datetime.fromisoformat(sunrise).strftime("%H:%M:%S")
                sunsettime = datetime.fromisoformat(sunset).strftime("%H:%M:%S")
            self.weatherlabels["sunrise"].config(text=sunrisetime)
            self.weatherlabels["sunset"].config(text=sunsettime)

        timestamp = data.get("timestamp", "")
        if timestamp:
            if isinstance(timestamp, datetime):
                timestr = timestamp.strftime("%Y-%m-%d %H:%M:%S")
            else:
                timestr = datetime.fromisoformat(timestamp).strftime("%Y-%m-%d %H:%M:%S")
            self.weatherlabels["lastupdated"].config(text=timestr)

    def displaymiscdata(self, data: Dict[str, Any]):
        """Display miscellaneous weather information."""
        self.weatherlabels["windspeed"].config(text=f"{data.get('windspeed', 0):.1f} m/s")
        self.weatherlabels["winddirection"].config(text=f"{data.get('winddirection', 0)}°")
        self.weatherlabels["weatherdescription"].config(text=data.get("weatherdescription", "N/A"))
        self.weatherlabels["visibility"].config(text=f"{data.get('visibility', 0):.1f} km")
        self.weatherlabels["cloudcover"].config(text=f"{data.get('cloudcover', 0)}%")

    def fetchanddisplayforecast(self):
        """Fetch and display weather forecast."""
        city = self.forecastcityentry.get().strip()
        if not city:
            messagebox.showwarning("Input Required", "Please enter a city name")
            return

        days = self.getforecastdays()
        self.updatestatus(f"Fetching {days}-day forecast for {city}...")

        forecastdata = self.fetcher.fetchforecast(city, days)

        if forecastdata:
            self.displayforecast(forecastdata, city, days)
            self.updatestatus(f"{days}-day forecast for {city} loaded")
        else:
            messagebox.showerror("Error", f"Could not fetch forecast for {city}")
            self.updatestatus("Ready")

    def getforecastdays(self) -> int:
        """Get number of forecast days from spinbox."""
        try:
            return int(self.forecastdays.get())
        except ValueError:
            return 3

    def displayforecast(self, forecastdata: List[Dict[str, Any]], city: str, days: int):
        """Display forecast data in the text widget."""
        self.forecasttext.delete(1.0, tk.END)
        self.insertforecastheader(city, days)

        if not forecastdata:
            self.forecasttext.insert(tk.END, "\nNo forecast data available for the specified period.\n")
            return

        self.insertforecastdata(forecastdata)

    def insertforecastheader(self, city: str, days: int):
        """Insert forecast header text."""
        header = f"{days}-Day Weather Forecast for {city.title()}\n"
        header += "=" * 80 + "\n\n"
        self.forecasttext.insert(tk.END, header)

    def insertforecastdata(self, forecastdata: List[Dict[str, Any]]):
        """Insert forecast data entries grouped by day."""
        currentdate = ""
        for entry in forecastdata:
            timestamp = datetime.strptime(entry["timestamp"], "%Y-%m-%d %H:%M:%S")
            datestr = timestamp.strftime("%A, %B %d, %Y")

            if datestr != currentdate:
                currentdate = datestr
                self.forecasttext.insert(tk.END, f"\n{datestr}\n")
                self.forecasttext.insert(tk.END, "-" * 50 + "\n")

            self.insertforecastline(entry, timestamp)

    def insertforecastline(self, entry: Dict[str, Any], timestamp: datetime):
        """Insert single forecast line."""
        timestr = timestamp.strftime("%H:%M")
        forecastline = (
            f"{timestr} | "
            f"Temp: {entry['temperature']:.1f}°C | "
            f"Feels: {entry['feelslike']:.1f}°C | "
            f"Humidity: {entry['humidity']}% | "
            f"Wind: {entry['windspeed']:.1f} m/s | "
            f"Clouds: {entry['cloudcover']}% | "
            f"{entry['weatherdescription']}"
        )
        if entry.get('probability', 0) > 0:
            forecastline += f" | Rain: {entry['probability']:.0f}%"
        forecastline += "\n"
        self.forecasttext.insert(tk.END, forecastline)

    def refreshhistorydisplay(self):
        """Refresh the history treeview with current data."""
        self.clearhistorytree()
        historypage, totalpages = self.historymanager.getpaginatedhistory(
            self.currenthistorypage, 15
        )
        self.populatehistorytree(historypage)
        self.updatepaginationlabel(totalpages)

    def clearhistorytree(self):
        """Clear all items from history treeview."""
        for item in self.historytree.get_children():
            self.historytree.delete(item)

    def populatehistorytree(self, historypage: List[Dict[str, Any]]):
        """Populate history treeview with entries."""
        for entry in historypage:
            values = self.extracthistoryvalues(entry)
            self.historytree.insert("", "end", values=values)

    def extracthistoryvalues(self, entry: Dict[str, Any]) -> Tuple:
        """Extract values for history treeview display."""
        return (
            entry.get("id", ""),
            entry.get("querytimestamp", "")[:19].replace("T", " "),
            entry.get("city", ""),
            f"{entry.get('temperature', 0):.1f}",
            f"{entry.get('humidity', 0)}",
            f"{entry.get('windspeed', 0):.1f}",
            entry.get("weatherdescription", "")
        )

    def updatepaginationlabel(self, totalpages: int):
        """Update pagination label."""
        self.pagelabel.config(text=f"Page {self.currenthistorypage} of {max(1, totalpages)}")

    def filterhistory(self, event=None):
        """Filter history based on search term."""
        searchterm = self.historysearch.get().strip()
        self.clearhistorytree()

        if not searchterm:
            self.refreshhistorydisplay()
            return

        results = self.historymanager.searchhistory(searchterm)
        self.displaysearchresults(results)

    def displaysearchresults(self, results: List[Dict[str, Any]]):
        """Display search results in treeview."""
        for entry in results[:100]:
            values = self.extracthistoryvalues(entry)
            self.historytree.insert("", "end", values=values)

        self.pagelabel.config(text=f"Search results: {len(results)} entries")

    def nexthistorypage(self):
        """Go to next history page."""
        totalpages = self.historymanager.getpaginatedhistory(1, 15)[1]
        if self.currenthistorypage < totalpages:
            self.currenthistorypage += 1
            self.refreshhistorydisplay()

    def prevhistorypage(self):
        """Go to previous history page."""
        if self.currenthistorypage > 1:
            self.currenthistorypage -= 1
            self.refreshhistorydisplay()

    def showhistorydetails(self, event):
        """Show detailed view of selected history entry."""
        selection = self.historytree.selection()
        if not selection:
            return

        item = self.historytree.item(selection[0])
        entryid = item["values"][0]

        for entry in self.historymanager.history:
            if entry["id"] == entryid:
                self.showentrydetailswindow(entry)
                break

    def showentrydetailswindow(self, entry: Dict[str, Any]):
        """Show a window with detailed entry information."""
        detailwindow = tk.Toplevel(self.root)
        detailwindow.title(f"Weather Details - {entry['city']}")
        detailwindow.geometry("400x300")

        textwidget = scrolledtext.ScrolledText(detailwindow, wrap=tk.WORD)
        textwidget.pack(fill="both", expand=True, padx=10, pady=10)

        details = self.formatentrydetails(entry)
        textwidget.insert(1.0, details)
        textwidget.config(state="disabled")

    def formatentrydetails(self, entry: Dict[str, Any]) -> str:
        """Format entry details for display."""
        details = f"Weather Details for {entry['city']}\n"
        details += "=" * 50 + "\n\n"
        details += f"Query Time: {entry['querytimestamp']}\n"
        details += f"City: {entry['city']}\n"
        details += f"Country: {entry.get('country', 'N/A')}\n"
        details += f"Temperature: {entry['temperature']:.1f}°C\n"
        details += f"Feels Like: {entry.get('feelslike', 'N/A')}°C\n"
        details += f"Humidity: {entry['humidity']}%\n"
        details += f"Pressure: {entry.get('pressure', 'N/A')} hPa\n"
        details += f"Wind Speed: {entry['windspeed']:.1f} m/s\n"
        details += f"Weather: {entry['weatherdescription']}\n"
        details += f"Condition: {entry['weathermain']}\n"
        return details

    def generatetemperaturegraph(self):
        """Generate temperature trend graph for a city."""
        self.generategraph(
            "Temperature",
            lambda history: [entry["temperature"] for entry in history],
            self.addtemperatureplots
        )

    def generatewindgraph(self):
        """Generate wind speed trend graph for a city."""
        self.generategraph(
            "Wind Speed",
            lambda history: [entry["windspeed"] for entry in history],
            self.addwindplots,
            ylabel="Wind Speed (m/s)"
        )

    def generatehumiditygraph(self):
        """Generate humidity trend graph for a city."""
        self.generategraph(
            "Humidity",
            lambda history: [entry["humidity"] for entry in history],
            self.addhumidityplots,
            ylabel="Humidity (%)",
            ylim=(0, 100)
        )

    def generategraph(self, graphtitle: str, datacallback, plotcallback, **kwargs):
        """Generic graph generation method."""
        city = self.analyticscity.get().strip()
        if not city:
            messagebox.showwarning("Input Required", "Please enter a city name")
            return

        history = self.historymanager.gethistorybycity(city)
        if not history:
            messagebox.showinfo("No Data", f"No history found for {city}")
            return

        self.cleargraphframe()
        fig = Figure(figsize=(10, 5))
        ax = fig.add_subplot(111)

        plotcallback(ax, history)
        self.customizegraphaxes(ax, city, graphtitle, **kwargs)

        self.displaygraph(fig)

    def addtemperatureplots(self, ax: plt.Axes, history: List[Dict[str, Any]]):
        """Add temperature plots to graph."""
        timestamps = [datetime.fromisoformat(entry["querytimestamp"]) for entry in history]
        temperatures = [entry["temperature"] for entry in history]
        feelslike = [entry.get("feelslike", t) for entry, t in zip(history, temperatures)]

        ax.plot(timestamps, temperatures, 'b-', label='Temperature', linewidth=2)
        ax.plot(timestamps, feelslike, 'r--', label='Feels Like', linewidth=1.5)
        ax.legend()

    def addwindplots(self, ax: plt.Axes, history: List[Dict[str, Any]]):
        """Add wind speed plots to graph."""
        timestamps = [datetime.fromisoformat(entry["querytimestamp"]) for entry in history]
        windspeeds = [entry["windspeed"] for entry in history]
        ax.bar(timestamps, windspeeds, width=0.01, color='skyblue', edgecolor='navy')

    def addhumidityplots(self, ax: plt.Axes, history: List[Dict[str, Any]]):
        """Add humidity plots to graph."""
        timestamps = [datetime.fromisoformat(entry["querytimestamp"]) for entry in history]
        humidity = [entry["humidity"] for entry in history]
        ax.fill_between(timestamps, humidity, alpha=0.3, color='green')
        ax.plot(timestamps, humidity, 'g-', linewidth=2)

    def customizegraphaxes(self, ax: plt.Axes, city: str, graphtitle: str, **kwargs):
        """Customize graph axes with provided parameters."""
        ax.set_xlabel("Date")
        ax.set_ylabel(kwargs.get("ylabel", "Value"))
        ax.set_title(f"{graphtitle} Trends for {city.title()}")
        ax.grid(True, alpha=0.3)

        if "ylim" in kwargs:
            ax.set_ylim(kwargs["ylim"])

        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
        fig = ax.get_figure()
        fig.autofmt_xdate()

    def cleargraphframe(self):
        """Clear all widgets from graph frame."""
        for widget in self.graphframe.winfo_children():
            widget.destroy()

    def displaygraph(self, fig: Figure):
        """Display graph in the graph frame."""
        canvas = FigureCanvasTkAgg(fig, self.graphframe)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def exporthistory(self):
        """Export history to CSV file."""
        if self.historymanager.exporttocsv():
            messagebox.showinfo("Success", "History exported to weatherhistoryexport.csv")
        else:
            messagebox.showerror("Error", "Failed to export history")

    def clearhistorydialog(self):
        """Show dialog to confirm history clearing."""
        if messagebox.askyesno("Confirm", "Are you sure you want to clear all history?"):
            self.historymanager.clearhistory()
            self.refreshhistorydisplay()
            messagebox.showinfo("Success", "History cleared")

    def setthresholdsdialog(self):
        """Set weather alert thresholds."""
        dialog = tk.Toplevel(self.root)
        dialog.title("Alert Thresholds")
        dialog.geometry("400x300")

        hightemp, lowtemp, highwind = self.createthresholdinputfields(dialog)

        def savethresholds():
            if self.savethresholdconfiguration(hightemp, lowtemp, highwind):
                dialog.destroy()
                messagebox.showinfo("Success", "Thresholds updated")

        ttk.Button(dialog, text="Save", command=savethresholds).pack(pady=20)

    def createthresholdinputfields(self, dialog: tk.Toplevel) -> Tuple:
        """Create threshold input fields."""
        ttk.Label(dialog, text="High Temperature Alert (°C):").pack(pady=5)
        hightemp = ttk.Entry(dialog, width=20)
        hightemp.pack(pady=5)
        hightemp.insert(0, str(self.alertmanager.alertthresholds["hightemperature"]))

        ttk.Label(dialog, text="Low Temperature Alert (°C):").pack(pady=5)
        lowtemp = ttk.Entry(dialog, width=20)
        lowtemp.pack(pady=5)
        lowtemp.insert(0, str(self.alertmanager.alertthresholds["lowtemperature"]))

        ttk.Label(dialog, text="High Wind Alert (m/s):").pack(pady=5)
        highwind = ttk.Entry(dialog, width=20)
        highwind.pack(pady=5)
        highwind.insert(0, str(self.alertmanager.alertthresholds["highwind"]))

        return hightemp, lowtemp, highwind

    def savethresholdconfiguration(self, hightemp: ttk.Entry, lowtemp: ttk.Entry,
                                   highwind: ttk.Entry) -> bool:
        """Save threshold configuration."""
        try:
            self.alertmanager.alertthresholds["hightemperature"] = float(hightemp.get())
            self.alertmanager.alertthresholds["lowtemperature"] = float(lowtemp.get())
            self.alertmanager.alertthresholds["highwind"] = float(highwind.get())
            return True
        except ValueError:
            messagebox.showerror("Error", "Invalid numeric value")
            return False

    def setupdateintervaldialog(self):
        """Set auto update interval."""
        interval = simpledialog.askinteger(
            "Update Interval",
            "Enter update interval in minutes:",
            minvalue=1,
            maxvalue=1440,
            initialvalue=self.updateinterval.get()
        )
        if interval:
            self.updateinterval.set(interval)
            messagebox.showinfo("Success", f"Update interval set to {interval} minutes")

    def startautoupdate(self):
        """Start automatic weather updates."""
        if not self.currentcity.get():
            messagebox.showwarning("No City", "Please enter a city in the Current Weather tab first")
            return

        if self.autoupdaterunning:
            messagebox.showinfo("Already Running", "Auto update is already running")
            return

        self.autoupdaterunning = True
        self.autoupdatethread = threading.Thread(target=self.autoupdateworker, daemon=True)
        self.autoupdatethread.start()
        self.updatestatus("Auto update started")

    def autoupdateworker(self):
        """Worker thread for automatic updates."""
        while self.autoupdaterunning:
            city = self.currentcity.get()
            if city:
                self.performautoupdate(city)
            self.waitfornextupdate()

    def performautoupdate(self, city: str):
        """Perform single auto update."""
        weatherdata = self.fetcher.fetchcurrentweather(city, forcefresh=True)
        if weatherdata:
            self.root.after(0, self.displayweatherdata, weatherdata)
            self.historymanager.addentry(weatherdata)
            self.checkalertsforautoupdate(weatherdata)

    def checkalertsforautoupdate(self, weatherdata: Dict[str, Any]):
        """Check alerts during auto update."""
        alerts = self.alertmanager.checksevereweather(weatherdata)
        if alerts:
            self.root.after(0, lambda: messagebox.showwarning(
                "Weather Alert",
                f"Severe weather detected:\n\n" + "\n".join(alerts)
            ))

    def waitfornextupdate(self):
        """Wait for next update interval."""
        for i in range(self.updateinterval.get() * 60):
            if not self.autoupdaterunning:
                break
            time.sleep(1)

    def stopautoupdate(self):
        """Stop automatic weather updates."""
        self.autoupdaterunning = False
        self.updatestatus("Auto update stopped")

    def updatestatus(self, message: str):
        """Update status bar message."""
        self.statusbar.config(text=message)
        self.root.update()

    def showabout(self):
        """Show about dialog."""
        abouttext = """Weather Tracking Dashboard
Version 1.0

A comprehensive weather tracking application with:
• Real-time weather data from OpenWeatherMap
• Local history storage in JSON format
• Weather forecasting for up to 5 days
• Graphical weather trends and analytics
• Weather alerts for severe conditions
• Automatic updates at custom intervals

Created with Python, Tkinter, and Matplotlib"""

        messagebox.showinfo("About", abouttext)

    def run(self):
        """Start the GUI application."""
        self.root.mainloop()


def main():
    """Main entry point for the application."""
    APIKEY = "05b44afef4bb7ca953ea354957712265"

    if APIKEY == "YOUR_API_KEY_HERE":
        displayapikeyinstructions()
        sys.exit(1)

    dashboard = WeatherDashboardGUI(APIKEY)
    dashboard.run()


def displayapikeyinstructions():
    """Display API key setup instructions."""
    print("Please set your OpenWeatherMap API key in the code")
    print("Get a free API key from: https://openweathermap.org/api")
    print("\nTo run this application:")
    print("1. Visit https://openweathermap.org/api")
    print("2. Sign up for a free account")
    print("3. Get your API key from your account dashboard")
    print("4. Replace 'YOUR_API_KEY_HERE' with your actual API key")
    print("5. Run: pip install requests matplotlib")
    print("6. Run this script again")


if __name__ == "__main__":
    main()